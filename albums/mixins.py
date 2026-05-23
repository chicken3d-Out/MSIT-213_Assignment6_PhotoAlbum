from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Album, Photo


class AlbumOwnerMixin(LoginRequiredMixin):
    """Only album owner (admin) can access."""

    def get_album(self):
        return get_object_or_404(Album, pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated:
            album = self.get_album()
            if not album.is_admin(request.user):
                raise PermissionDenied
        return response


class AlbumEditorMixin(LoginRequiredMixin):
    """Album owner or collaborator can access."""

    def get_album(self):
        return get_object_or_404(Album, pk=self.kwargs.get('pk') or self.kwargs.get('album_pk'))

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated:
            album = self.get_album()
            if not album.can_edit(request.user):
                raise PermissionDenied
        return response


class PhotoOwnerMixin(LoginRequiredMixin):
    """Only the photo uploader or album owner can access."""

    def get_photo(self):
        return get_object_or_404(Photo, pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated:
            photo = self.get_photo()
            is_uploader = photo.uploaded_by == request.user
            is_album_owner = photo.album.is_admin(request.user)
            if not (is_uploader or is_album_owner):
                raise PermissionDenied
        return response
