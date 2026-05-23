from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Album(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_albums')
    collaborators = models.ManyToManyField(User, related_name='collaborated_albums', blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    cover_photo = models.ForeignKey(
        'Photo', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='cover_of'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_admin(self, user):
        """Check if user is the album owner (admin role)."""
        return self.owner == user

    def can_edit(self, user):
        """Check if user can edit this album (owner or collaborator)."""
        return self.owner == user or self.collaborators.filter(pk=user.pk).exists()

    def can_view(self, user):
        """Check if user can view this album."""
        if self.is_public:
            return True
        if user.is_authenticated:
            return self.owner == user or self.collaborators.filter(pk=user.pk).exists()
        return False

    @property
    def photo_count(self):
        return self.photos.count()


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
