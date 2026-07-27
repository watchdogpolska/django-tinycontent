import pytest
from django.test import override_settings

from tinycontent.indexer import TinyContentIndexer
from tinycontent.models import TinyContent, TinyContentUsage


def _templates_setting(template_dir):
    return [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [str(template_dir)],
            "APP_DIRS": False,
        }
    ]


@pytest.mark.django_db
def test_build_autocreates_missing_reference(tmp_path):
    (tmp_path / "page.html").write_text("{% tinycontent_simple 'welcome' %}\n")

    with override_settings(TEMPLATES=_templates_setting(tmp_path)):
        result = TinyContentIndexer.build()

    content = TinyContent.objects.get(name="welcome")
    assert content.content == ""
    assert content.active is False
    assert content.autocreated is True
    assert content.title == "Welcome"
    assert result.created == ["welcome"]
    assert result.usages_recorded == 1

    usage = TinyContentUsage.objects.get(content=content)
    assert usage.template_path == str(tmp_path / "page.html")
    assert usage.line_number == 1


@pytest.mark.django_db
def test_build_records_multi_arg_and_multiple_usages(tmp_path):
    (tmp_path / "a.html").write_text(
        "line one\n{% tinycontent 'foo' 'bar' %}fallback{% endtinycontent %}\n"
    )
    (tmp_path / "b.html").write_text("{% tinycontent_simple 'foo:bar' %}\n")

    with override_settings(TEMPLATES=_templates_setting(tmp_path)):
        result = TinyContentIndexer.build()

    content = TinyContent.objects.get(name="foo:bar")
    assert result.usages_recorded == 2
    assert TinyContentUsage.objects.filter(content=content).count() == 2


@pytest.mark.django_db
def test_build_skips_dynamic_names_and_warns(tmp_path):
    (tmp_path / "page.html").write_text("{% tinycontent_simple page.slug %}\n")

    with override_settings(TEMPLATES=_templates_setting(tmp_path)):
        result = TinyContentIndexer.build()

    assert not TinyContent.objects.exists()
    assert result.usages_recorded == 0
    assert len(result.warnings) == 1
    assert "page.html:1" in result.warnings[0]


@pytest.mark.django_db
def test_build_is_idempotent_rebuild_from_scratch(tmp_path):
    (tmp_path / "page.html").write_text("{% tinycontent_simple 'welcome' %}\n")

    with override_settings(TEMPLATES=_templates_setting(tmp_path)):
        TinyContentIndexer.build()
        TinyContentIndexer.build()

    assert TinyContent.objects.filter(name="welcome").count() == 1
    assert TinyContentUsage.objects.count() == 1


@pytest.mark.django_db
def test_build_only_deactivates_autocreated_rows(tmp_path):
    manual = TinyContent.objects.create(
        name="manual", content="Hello", active=True, autocreated=False
    )
    auto = TinyContent.objects.create(
        name="stale-auto", content="", active=True, autocreated=True
    )
    (tmp_path / "page.html").write_text("no tags here\n")

    with override_settings(TEMPLATES=_templates_setting(tmp_path)):
        TinyContentIndexer.build()

    manual.refresh_from_db()
    auto.refresh_from_db()

    # Manually-created row is untouched even though it now has 0 usages.
    assert manual.active is True
    # Indexer-created row with 0 usages gets deactivated.
    assert auto.active is False


@pytest.mark.django_db
def test_build_does_not_touch_active_while_still_used(tmp_path):
    auto = TinyContent.objects.create(
        name="welcome", content="Hi", active=True, autocreated=True
    )
    (tmp_path / "page.html").write_text("{% tinycontent_simple 'welcome' %}\n")

    with override_settings(TEMPLATES=_templates_setting(tmp_path)):
        TinyContentIndexer.build()

    auto.refresh_from_db()
    assert auto.active is True


@pytest.mark.django_db
def test_build_deactivates_autocreated_row_even_if_manually_reactivated(tmp_path):
    auto = TinyContent.objects.create(
        name="welcome", content="Hi", active=True, autocreated=True
    )
    (tmp_path / "page.html").write_text("no tags here\n")

    with override_settings(TEMPLATES=_templates_setting(tmp_path)):
        TinyContentIndexer.build()

    auto.refresh_from_db()
    assert auto.active is False
