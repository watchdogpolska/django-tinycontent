import pytest

from tinycontent.models import TinyContent


@pytest.mark.django_db
def test_tinycontent_str(simple_content):
    assert "foobar" == str(simple_content)


@pytest.mark.django_db
def test_tinycontentfile_str(file_upload):
    assert "Foobar" == str(file_upload)


@pytest.mark.django_db
def test_tinycontentfile_slug(file_upload):
    assert "foobar" == file_upload.slug


@pytest.mark.django_db
def test_tinycontent_defaults(simple_content):
    assert simple_content.active is True
    assert simple_content.autocreated is False


@pytest.mark.django_db
def test_title_auto_derived_from_name():
    content = TinyContent.objects.create(name="footer:copyright-notice_v2.1")
    assert content.title == "Footer Copyright Notice V2 1"


@pytest.mark.django_db
def test_title_not_overwritten_once_set():
    content = TinyContent.objects.create(name="footer", title="Custom Footer Title")
    assert content.title == "Custom Footer Title"

    content.content = "updated"
    content.save()
    content.refresh_from_db()
    assert content.title == "Custom Footer Title"
