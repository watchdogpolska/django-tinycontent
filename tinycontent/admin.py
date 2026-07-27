from typing import Any

from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from tinycontent.indexer import TinyContentIndexer
from tinycontent.models import TinyContent, TinyContentFileUpload, TinyContentUsage


class TinyContentUsageInline(admin.TabularInline):
    model = TinyContentUsage
    fields = ("template_path", "line_number")
    readonly_fields = ("template_path", "line_number")
    extra = 0
    can_delete = False

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False


class UnusedContentFilter(admin.SimpleListFilter):
    title = "unused content"
    parameter_name = "unused"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> tuple[tuple[str, str], ...]:
        return (("1", "Unused (0 template usages)"),)

    def queryset(
        self, request: HttpRequest, queryset: QuerySet[TinyContent]
    ) -> QuerySet[TinyContent]:
        if self.value() == "1":
            return queryset.filter(usage_count=0)
        return queryset


class MissingReferenceFilter(admin.SimpleListFilter):
    title = "missing references"
    parameter_name = "missing"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> tuple[tuple[str, str], ...]:
        return (("1", "Autocreated (needs content)"),)

    def queryset(
        self, request: HttpRequest, queryset: QuerySet[TinyContent]
    ) -> QuerySet[TinyContent]:
        if self.value() == "1":
            return queryset.filter(autocreated=True)
        return queryset


class TinyContentAdmin(admin.ModelAdmin):
    list_display = ("title", "name", "usage_count", "active", "autocreated")
    list_filter = (UnusedContentFilter, MissingReferenceFilter, "active")
    search_fields = (
        "name",
        "title",
        "content",
    )
    inlines = (TinyContentUsageInline,)
    actions = ("rebuild_index",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[TinyContent]:
        return super().get_queryset(request).annotate(usage_count=Count("usages"))

    @admin.display(ordering="usage_count", description="Usages")
    def usage_count(self, obj: TinyContent) -> int:
        return obj.usage_count

    def get_readonly_fields(
        self, request: HttpRequest, obj: TinyContent | None = None
    ) -> tuple[str, ...]:
        if obj is not None:
            return ("name",)
        return ()

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    @admin.action(description="Rebuild template usage index")
    def rebuild_index(
        self, request: HttpRequest, queryset: QuerySet[TinyContent]
    ) -> None:
        result = TinyContentIndexer.build()
        message = (
            f"Scanned {result.templates_scanned} template(s), "
            f"recorded {result.usages_recorded} usage(s), "
            f"created {len(result.created)} content block(s)."
        )
        if result.warnings:
            message += f" {len(result.warnings)} warning(s) — see server logs."
        self.message_user(request, message)


admin.site.register(TinyContent, TinyContentAdmin)


class TinyContentFileUploadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    search_fields = ("name",)


admin.site.register(TinyContentFileUpload, TinyContentFileUploadAdmin)
