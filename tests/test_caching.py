from unittest import mock

import pytest
from django.db import DEFAULT_DB_ALIAS, connections
from django.test.utils import CaptureQueriesContext

from tinycontent.models import TinyContent


class FakeCache:
    def __init__(self) -> None:
        self.items: dict[str, TinyContent] = {}

    def get(self, key: str) -> TinyContent | None:
        return self.items.get(key, None)

    def set(self, key: str, value: TinyContent) -> None:
        self.items[key] = value

    def delete(self, key: str) -> None:
        del self.items[key]


class QueryCounter(CaptureQueriesContext):
    def __init__(self) -> None:
        conn = connections[DEFAULT_DB_ALIAS]
        super().__init__(conn)

    def num_queries(self) -> int:
        return len(self)


@pytest.mark.django_db
def test_cache_hit_on_second_time(simple_content):
    with mock.patch("tinycontent.models.cache", FakeCache()):
        with QueryCounter() as q:
            obj = TinyContent.get_content_by_name(simple_content.name)
            assert obj == simple_content
            assert q.num_queries() == 1

        with QueryCounter() as q:
            obj = TinyContent.get_content_by_name(simple_content.name)
            assert obj == simple_content
            assert q.num_queries() == 0


@pytest.mark.django_db
def test_cache_invalidated_by_delete(simple_content):
    with mock.patch("tinycontent.models.cache", FakeCache()):
        with QueryCounter() as q:
            obj = TinyContent.get_content_by_name(simple_content.name)
            assert obj == simple_content
            assert q.num_queries() == 1

        with QueryCounter() as q:
            simple_content.delete()
            assert q.num_queries() == 1

        with QueryCounter() as q:
            with pytest.raises(TinyContent.DoesNotExist):
                obj = TinyContent.get_content_by_name(simple_content.name)
            assert q.num_queries() == 1


@pytest.mark.django_db
def test_cache_invalidated_by_save(simple_content):
    with mock.patch("tinycontent.models.cache", FakeCache()):
        with QueryCounter() as q:
            obj = TinyContent.get_content_by_name(simple_content.name)
            assert obj == simple_content
            assert q.num_queries() == 1

        with QueryCounter() as q:
            simple_content.content = "hello"
            simple_content.save()
            assert q.num_queries() == 1

        with QueryCounter() as q:
            obj = TinyContent.get_content_by_name(simple_content.name)
            assert obj.name == simple_content.name
            assert obj.content == "hello"
            assert q.num_queries() == 1

        with QueryCounter() as q:
            obj = TinyContent.get_content_by_name(simple_content.name)
            assert obj.name == simple_content.name
            assert obj.content == "hello"
            assert q.num_queries() == 0
