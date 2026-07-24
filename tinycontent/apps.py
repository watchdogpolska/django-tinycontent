from django.apps import AppConfig

from .conf import get_app_verbose_name


class TinyContentConfig(AppConfig):
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "tinycontent"
    verbose_name: str = get_app_verbose_name()
