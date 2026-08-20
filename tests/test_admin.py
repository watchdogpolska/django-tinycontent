import sys

import pytest
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.core.exceptions import ImproperlyConfigured
from django.db.models import ProtectedError
from django.test import RequestFactory, override_settings

from tinycontent.admin import (
    MissingReferenceFilter,
    TinyContentAdmin,
    UnusedContentFilter,
)
from tinycontent.models import TinyContent, TinyContentUsage

pytestmark = pytest.mark.django_db


@pytest.fixture()
def tc_admin():
    return TinyContentAdmin(TinyContent, admin.site)


@pytest.fixture()
def rf():
    return RequestFactory()


def test_has_add_permission_is_always_false(tc_admin, rf):
    request = rf.get("/admin/tinycontent/tinycontent/add/")
    assert tc_admin.has_add_permission(request) is False


def test_name_is_readonly_only_when_editing(tc_admin, rf, simple_content):
    request = rf.get("/admin/")
    assert tc_admin.get_readonly_fields(request, None) == ()
    assert "name" in tc_admin.get_readonly_fields(request, simple_content)


def test_deleting_used_content_is_protected(simple_content):
    TinyContentUsage.objects.create(
        content=simple_content, template_path="a.html", line_number=1
    )
    with pytest.raises(ProtectedError):
        simple_content.delete()


def test_deleting_unused_content_succeeds(simple_content):
    simple_content.delete()
    assert not TinyContent.objects.filter(pk=simple_content.pk).exists()


def test_usage_count_annotation(tc_admin, rf, simple_content):
    TinyContentUsage.objects.create(
        content=simple_content, template_path="a.html", line_number=1
    )
    TinyContentUsage.objects.create(
        content=simple_content, template_path="a.html", line_number=2
    )

    request = rf.get("/admin/")
    obj = tc_admin.get_queryset(request).get(pk=simple_content.pk)
    assert tc_admin.usage_count(obj) == 2


def test_unused_content_filter(tc_admin, rf, simple_content):
    used = TinyContent.objects.create(name="used")
    TinyContentUsage.objects.create(content=used, template_path="a.html", line_number=1)

    request = rf.get("/admin/", {"unused": "1"})
    filt = UnusedContentFilter(request, {"unused": "1"}, TinyContent, tc_admin)
    filtered = filt.queryset(request, tc_admin.get_queryset(request))

    names = set(filtered.values_list("name", flat=True))
    assert simple_content.name in names
    assert used.name not in names


def test_missing_reference_filter(tc_admin, rf):
    auto = TinyContent.objects.create(name="auto-thing", autocreated=True)
    manual = TinyContent.objects.create(name="manual-thing", autocreated=False)

    request = rf.get("/admin/", {"missing": "1"})
    filt = MissingReferenceFilter(request, {"missing": "1"}, TinyContent, tc_admin)
    filtered = filt.queryset(request, tc_admin.get_queryset(request))

    names = set(filtered.values_list("name", flat=True))
    assert auto.name in names
    assert manual.name not in names


def test_rebuild_index_action_runs_indexer(tc_admin, rf, tmp_path, monkeypatch):
    monkeypatch.setattr(tc_admin, "message_user", lambda *args, **kwargs: None)
    (tmp_path / "page.html").write_text("{% tinycontent_simple 'welcome' %}\n")

    request = rf.get("/admin/")
    templates = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [str(tmp_path)],
            "APP_DIRS": False,
        }
    ]
    with override_settings(TEMPLATES=templates):
        tc_admin.rebuild_index(request, TinyContent.objects.none())

    assert TinyContent.objects.filter(name="welcome").exists()


def test_content_field_uses_plain_textarea_by_default(tc_admin, rf, simple_content):
    request = rf.get("/admin/")
    form_class = tc_admin.get_form(request, simple_content)
    widget = form_class.base_fields["content"].widget
    assert type(widget) is AdminTextareaWidget


def test_content_field_uses_tinymce_when_enabled(tc_admin, rf, simple_content):
    tinymce_widgets = pytest.importorskip("tinymce.widgets")

    with override_settings(TINYCONTENT_USE_TINYMCE=True):
        request = rf.get("/admin/")
        form_class = tc_admin.get_form(request, simple_content)

    widget = form_class.base_fields["content"].widget
    assert isinstance(widget, tinymce_widgets.TinyMCE)


def test_tinymce_widget_defaults_to_gpl_license_key(tc_admin):
    pytest.importorskip("tinymce.widgets")

    widget = tc_admin._tinymce_widget()
    assert widget.mce_attrs["license_key"] == "gpl"


def test_tinymce_widget_respects_host_license_key(tc_admin):
    pytest.importorskip("tinymce.widgets")

    with override_settings(TINYMCE_DEFAULT_CONFIG={"license_key": "abc123"}):
        widget = tc_admin._tinymce_widget()

    assert "license_key" not in widget.mce_attrs


def test_tinymce_enabled_without_package_raises(tc_admin, monkeypatch):
    pytest.importorskip("tinymce.widgets")
    monkeypatch.setitem(sys.modules, "tinymce.widgets", None)

    with pytest.raises(ImproperlyConfigured):
        tc_admin._tinymce_widget()
