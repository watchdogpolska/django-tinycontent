import pytest
from django.core.management import call_command
from django.test import override_settings

from tinycontent.models import TinyContent


@pytest.mark.django_db
def test_tinycontent_index_command_creates_content(tmp_path, capsys):
    (tmp_path / "page.html").write_text("{% tinycontent_simple 'welcome' %}\n")

    templates = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [str(tmp_path)],
            "APP_DIRS": False,
        }
    ]
    with override_settings(TEMPLATES=templates):
        call_command("tinycontent_index")

    assert TinyContent.objects.filter(name="welcome").exists()

    out = capsys.readouterr().out
    assert "Templates scanned: 1" in out
    assert "welcome" in out
