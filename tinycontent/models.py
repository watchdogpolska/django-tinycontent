import base64
from typing import Any

import autoslug
from django.core.cache import cache
from django.db import models

from tinycontent.conf import get_filter_list
from tinycontent.utils.naming import derive_title


class TinyContent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=150, blank=True)
    content = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    autocreated = models.BooleanField(default=False, editable=False)

    def __str__(self) -> str:
        return self.name

    def rendered_content(self) -> str:
        filters = get_filter_list()

        content = self.content

        for filter in filters:
            content = filter(content)

        return content

    @staticmethod
    def get_content_by_name(name: str) -> "TinyContent":
        cache_key = TinyContent.get_cache_key(name)
        obj = cache.get(cache_key)

        if obj is None:
            obj = TinyContent.objects.get(name=name)
            cache.set(cache_key, obj)

        return obj

    @staticmethod
    def get_cache_key(name: str) -> str:
        return f"tinycontent_{base64.b64encode(bytes(name, 'utf-8'))}"

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        cache.delete(TinyContent.get_cache_key(self.name))
        return super().delete(*args, **kwargs)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.title:
            self.title = derive_title(self.name)
        cache.delete(TinyContent.get_cache_key(self.name))
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Content block"


class TinyContentUsage(models.Model):
    content = models.ForeignKey(
        TinyContent, related_name="usages", on_delete=models.PROTECT
    )
    template_path = models.CharField(max_length=500)
    line_number = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.template_path}:{self.line_number}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content", "template_path", "line_number"],
                name="unique_tinycontent_usage",
            ),
        ]
        ordering = ("template_path", "line_number")
        verbose_name = "Template usage"
        verbose_name_plural = "Template usages"


class TinyContentFileUpload(models.Model):
    name = models.CharField(max_length=60, help_text="The name of the file.")
    slug = autoslug.AutoSlugField(populate_from="name", unique=True)
    file = models.FileField(upload_to="tinycontent/uploads")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "File upload"
        ordering = ("-created",)
