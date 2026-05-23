from django.contrib import admin
from .models import Album, Photo


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'is_public', 'photo_count', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'description', 'owner__username']
    filter_horizontal = ['collaborators']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title', 'description', 'album__title']
    readonly_fields = ['uploaded_at', 'updated_at']
