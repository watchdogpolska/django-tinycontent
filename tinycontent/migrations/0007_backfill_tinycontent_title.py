import re

from django.db import migrations

_TITLE_CHARS_RE = re.compile(r"[:\-_.]+")


def backfill_title(apps, schema_editor):
    TinyContent = apps.get_model("tinycontent", "TinyContent")
    for content in TinyContent.objects.filter(title=""):
        content.title = _TITLE_CHARS_RE.sub(" ", content.name).strip().title()
        content.save(update_fields=["title"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("tinycontent", "0006_tinycontentusage_and_metadata_fields"),
    ]

    operations = [
        migrations.RunPython(backfill_title, noop),
    ]
