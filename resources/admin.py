from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploader', 'created_at', 'download_count')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('download_count', 'created_at')
