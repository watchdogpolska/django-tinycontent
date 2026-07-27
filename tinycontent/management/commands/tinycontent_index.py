from typing import Any

from django.core.management.base import BaseCommand

from tinycontent.indexer import TinyContentIndexer


class Command(BaseCommand):
    help = (
        "Scan all Django templates for tinycontent/tinycontent_simple tag usages, "
        "rebuild the template usage index and autocreate any missing content blocks."
    )

    def handle(self, *args: Any, **options: Any) -> None:
        result = TinyContentIndexer.build()

        self.stdout.write(f"Templates scanned: {result.templates_scanned}")
        self.stdout.write(f"Usages recorded: {result.usages_recorded}")

        if result.created:
            self.stdout.write(f"Created {len(result.created)} content block(s):")
            for name in result.created:
                self.stdout.write(f"  - {name}")

        if result.warnings:
            self.stdout.write(self.style.WARNING(f"{len(result.warnings)} warning(s):"))
            for warning in result.warnings:
                self.stdout.write(self.style.WARNING(f"  - {warning}"))
