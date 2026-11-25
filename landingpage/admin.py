from django.contrib import admin
from django.utils.html import format_html

from .models import PageSeo, Slide


@admin.register(PageSeo)
class PageSeoAdmin(admin.ModelAdmin):
    list_display = ('key', 'path', 'title', 'is_published')

    def has_delete_permission(self, request, obj=None):
        return not (obj and obj.key == 'home')


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'slug', 'page', 'order', 'is_active')
    list_display_links = ('thumbnail', 'slug')
    list_editable = ('order', 'is_active')
    list_filter = ('page', 'is_active')
    ordering = ('page', 'order')

    @admin.display(description='Preview')
    def thumbnail(self, obj):
        return format_html('<img src="{}" alt="" style="height:40px">', obj.desktop.jpg)
