import os
import re
from collections.abc import Iterator
from dataclasses import dataclass, field

from django.db import transaction
from django.template import engines
from django.template.backends.django import DjangoTemplates
from django.template.base import smart_split
from django.template.utils import get_app_template_dirs

from tinycontent.models import TinyContent, TinyContentUsage
from tinycontent.utils.naming import derive_title

TAG_CALL_RE = re.compile(r"{%\s*(tinycontent_simple|tinycontent)\s+(.+?)\s*%}")
_QUOTED_RE = re.compile(r"^(['\"]).*\1$")


@dataclass
class IndexResult:
    templates_scanned: int = 0
    usages_recorded: int = 0
    created: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _template_dirs() -> list[str]:
    dirs: dict[str, None] = {}

    for engine in engines.all():
        if not isinstance(engine, DjangoTemplates):
            continue

        for template_dir in engine.engine.dirs:
            dirs[str(template_dir)] = None

        if engine.engine.app_dirs:
            for template_dir in get_app_template_dirs("templates"):
                dirs[str(template_dir)] = None

    return list(dirs)


def _iter_template_files() -> Iterator[str]:
    for template_dir in _template_dirs():
        for root, _dirs, files in os.walk(template_dir):
            for filename in files:
                yield os.path.join(root, filename)


def _resolve_name(argstring: str) -> str | None:
    bits = list(smart_split(argstring))
    if not bits:
        return None

    parts = []
    for bit in bits:
        if not _QUOTED_RE.match(bit):
            return None
        parts.append(bit[1:-1])

    return ":".join(parts)


def _scan_template(path: str) -> tuple[list[tuple[str, str, int]], list[str]]:
    usages: list[tuple[str, str, int]] = []
    warnings: list[str] = []

    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except (OSError, UnicodeDecodeError):
        return usages, warnings

    for line_number, line in enumerate(lines, start=1):
        for match in TAG_CALL_RE.finditer(line):
            name = _resolve_name(match.group(2))
            if name is None:
                warnings.append(
                    f"{path}:{line_number}: skipped tag with a non-literal name"
                )
                continue
            usages.append((name, path, line_number))

    return usages, warnings


class TinyContentIndexer:
    @classmethod
    def build(cls) -> IndexResult:
        result = IndexResult()
        all_usages: list[tuple[str, str, int]] = []

        template_files = list(_iter_template_files())
        result.templates_scanned = len(template_files)

        for path in template_files:
            usages, warnings = _scan_template(path)
            all_usages.extend(usages)
            result.warnings.extend(warnings)

        discovered_names = {name for name, _path, _line in all_usages}

        with transaction.atomic():
            existing_names = set(
                TinyContent.objects.filter(name__in=discovered_names).values_list(
                    "name", flat=True
                )
            )
            missing_names = discovered_names - existing_names
            TinyContent.objects.bulk_create(
                TinyContent(
                    name=name,
                    title=derive_title(name),
                    content="",
                    active=False,
                    autocreated=True,
                )
                for name in missing_names
            )
            result.created = sorted(missing_names)

            name_to_id = dict(
                TinyContent.objects.filter(name__in=discovered_names).values_list(
                    "name", "id"
                )
            )

            TinyContentUsage.objects.all().delete()
            usage_objs = [
                TinyContentUsage(
                    content_id=name_to_id[name],
                    template_path=path,
                    line_number=line_number,
                )
                for name, path, line_number in set(all_usages)
                if name in name_to_id
            ]
            TinyContentUsage.objects.bulk_create(usage_objs, ignore_conflicts=True)
            result.usages_recorded = len(usage_objs)

            used_ids = {usage.content_id for usage in usage_objs}
            TinyContent.objects.filter(autocreated=True).exclude(
                id__in=used_ids
            ).update(active=False)

        return result
