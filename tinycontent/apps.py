import logging
import os
import sys
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.db import DatabaseError
from django.db.models.signals import post_migrate

from .conf import get_app_verbose_name, get_auto_index_enabled

logger = logging.getLogger(__name__)


class TinyContentConfig(AppConfig):
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "tinycontent"
    verbose_name: str = get_app_verbose_name()

    def ready(self) -> None:
        post_migrate.connect(self._on_post_migrate, sender=self)

        if (
            settings.DEBUG
            and self._auto_index_enabled()
            and os.environ.get("RUN_MAIN") == "true"
        ):
            self._run_index_safely()

    @staticmethod
    def _auto_index_enabled() -> bool:
        return get_auto_index_enabled() and "pytest" not in sys.modules

    def _on_post_migrate(self, **kwargs: Any) -> None:
        if self._auto_index_enabled():
            self._run_index_safely()

    @staticmethod
    def _run_index_safely() -> None:
        from tinycontent.indexer import TinyContentIndexer

        try:
            TinyContentIndexer.build()
        except DatabaseError:
            logger.warning(
                "tinycontent: skipped automatic template indexing, "
                "database is not ready yet"
            )
