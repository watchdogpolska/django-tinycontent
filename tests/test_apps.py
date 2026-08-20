from unittest import mock

import pytest
from django.db import DatabaseError

from tinycontent.apps import TinyContentConfig
from tinycontent.conf import get_auto_index_enabled, get_use_tinymce


def test_get_auto_index_enabled_defaults_true():
    assert get_auto_index_enabled() is True


def test_get_auto_index_enabled_respects_setting(settings):
    settings.TINYCONTENT_AUTO_INDEX = False
    assert get_auto_index_enabled() is False


def test_get_use_tinymce_defaults_false():
    assert get_use_tinymce() is False


def test_get_use_tinymce_respects_setting(settings):
    settings.TINYCONTENT_USE_TINYMCE = True
    assert get_use_tinymce() is True


def test_auto_index_disabled_while_running_under_pytest():
    # "pytest" is always present in sys.modules during a test run, which is
    # exactly the guard that keeps this feature from firing during our own
    # (or a host project's) test suite.
    assert TinyContentConfig._auto_index_enabled() is False


def test_run_index_safely_swallows_database_error():
    with mock.patch(
        "tinycontent.indexer.TinyContentIndexer.build",
        side_effect=DatabaseError("no such table"),
    ):
        TinyContentConfig._run_index_safely()


@pytest.mark.django_db
def test_run_index_safely_calls_build():
    with mock.patch("tinycontent.indexer.TinyContentIndexer.build") as build:
        TinyContentConfig._run_index_safely()
    build.assert_called_once()
