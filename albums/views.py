from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Album, Photo
from .forms import RegisterForm, AlbumForm, PhotoForm, PhotoEditForm
from .mixins import AlbumOwnerMixin, AlbumEditorMixin, PhotoOwnerMixin


# ─── Auth Views ───────────────────────────────────────────────

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('album_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Welcome, {user.username}! Your account has been created.')
        return super().form_valid(form)


# ─── Album Views ──────────────────────────────────────────────

class AlbumListView(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'albums/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user
        qs = Album.objects.filter(
            Q(owner=user) | Q(collaborators=user)
        ).distinct().prefetch_related('photos')

        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['public_albums'] = Album.objects.filter(is_public=True).exclude(
            Q(owner=self.request.user) | Q(collaborators=self.request.user)
        ).distinct()[:6]
        return ctx


class AlbumDetailView(LoginRequiredMixin, DetailView):
    model = Album
    template_name = 'albums/album_detail.html'
    context_object_name = 'album'

    def get_object(self, queryset=None):
        album = get_object_or_404(Album, pk=self.kwargs['pk'])
        if not album.can_view(self.request.user):
            raise PermissionDenied
        return album

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['photos'] = self.object.photos.all()
        ctx['is_admin'] = self.object.is_admin(self.request.user)
        ctx['can_edit'] = self.object.can_edit(self.request.user)
        ctx['photo_form'] = PhotoForm()
        return ctx


class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'
    success_url = reverse_lazy('album_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Album created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Create'
        return ctx


class AlbumUpdateView(AlbumOwnerMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'albums/album_form.html'

    def get_album(self):
        return get_object_or_404(Album, pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request, 'Album updated successfully!')
        return reverse('album_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action'] = 'Edit'
        return ctx


class AlbumDeleteView(AlbumOwnerMixin, DeleteView):
    model = Album
    template_name = 'albums/album_confirm_delete.html'
    success_url = reverse_lazy('album_list')

    def get_album(self):
        return get_object_or_404(Album, pk=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'Album deleted.')
        return super().form_valid(form)


# ─── Photo Views ──────────────────────────────────────────────

class PhotoUploadView(AlbumEditorMixin, View):
    """Upload one or more photos to an album."""

    def get_album(self):
        return get_object_or_404(Album, pk=self.kwargs['pk'])

    def post(self, request, pk):
        album = get_object_or_404(Album, pk=pk)
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.album = album
            photo.uploaded_by = request.user
            photo.save()
            # Set as cover if it's the first photo
            if not album.cover_photo:
                album.cover_photo = photo
                album.save()
            messages.success(request, 'Photo uploaded successfully!')
        else:
            messages.error(request, 'Upload failed. Please check the form.')
        return redirect('album_detail', pk=pk)


class PhotoDetailView(LoginRequiredMixin, DetailView):
    model = Photo
    template_name = 'albums/photo_detail.html'
    context_object_name = 'photo'

    def get_object(self, queryset=None):
        photo = get_object_or_404(Photo, pk=self.kwargs['pk'])
        if not photo.album.can_view(self.request.user):
            raise PermissionDenied
        return photo

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['can_edit'] = (
            self.object.uploaded_by == self.request.user or
            self.object.album.is_admin(self.request.user)
        )
        return ctx


class PhotoUpdateView(PhotoOwnerMixin, UpdateView):
    model = Photo
    form_class = PhotoEditForm
    template_name = 'albums/photo_form.html'

    def get_photo(self):
        return get_object_or_404(Photo, pk=self.kwargs['pk'])

    def get_success_url(self):
        messages.success(self.request, 'Photo updated!')
        return reverse('photo_detail', kwargs={'pk': self.object.pk})


class PhotoDeleteView(PhotoOwnerMixin, DeleteView):
    model = Photo
    template_name = 'albums/photo_confirm_delete.html'

    def get_photo(self):
        return get_object_or_404(Photo, pk=self.kwargs['pk'])

    def get_success_url(self):
        messages.success(self.request, 'Photo deleted.')
        return reverse('album_detail', kwargs={'pk': self.object.album.pk})

    def form_valid(self, form):
        photo = self.get_object()
        album = photo.album
        # If this was the cover, unset it
        if album.cover_photo == photo:
            album.cover_photo = None
            album.save()
        return super().form_valid(form)


class SetCoverView(AlbumOwnerMixin, View):
    """Set a photo as album cover — owner only."""

    def get_album(self):
        return get_object_or_404(Album, pk=self.kwargs['album_pk'])

    def post(self, request, album_pk, pk):
        album = get_object_or_404(Album, pk=album_pk)
        photo = get_object_or_404(Photo, pk=pk, album=album)
        album.cover_photo = photo
        album.save()
        messages.success(request, 'Cover photo updated!')
        return redirect('album_detail', pk=album_pk)
