from collections.abc import Callable

from django.conf import settings

from tinycontent.utils.importer import import_from_dotted_path


def get_app_verbose_name() -> str:
    return getattr(settings, "TINYCONTENT_VERBOSE_NAME", "Tinycontent")


def get_auto_index_enabled() -> bool:
    return getattr(settings, "TINYCONTENT_AUTO_INDEX", True)


def get_filter_list() -> list[Callable[[str], str]]:
    try:
        path_list = settings.TINYCONTENT_FILTER
    except AttributeError:
        return []

    if isinstance(path_list, str):
        path_list = [
            path_list,
        ]

    return [import_from_dotted_path(path) for path in path_list]
