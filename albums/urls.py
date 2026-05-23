from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),

    # Albums
    path('', views.AlbumListView.as_view(), name='album_list'),
    path('albums/create/', views.AlbumCreateView.as_view(), name='album_create'),
    path('albums/<int:pk>/', views.AlbumDetailView.as_view(), name='album_detail'),
    path('albums/<int:pk>/edit/', views.AlbumUpdateView.as_view(), name='album_edit'),
    path('albums/<int:pk>/delete/', views.AlbumDeleteView.as_view(), name='album_delete'),

    # Photos
    path('albums/<int:pk>/upload/', views.PhotoUploadView.as_view(), name='photo_upload'),
    path('photos/<int:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('photos/<int:pk>/edit/', views.PhotoUpdateView.as_view(), name='photo_edit'),
    path('photos/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    path('albums/<int:album_pk>/cover/<int:pk>/', views.SetCoverView.as_view(), name='set_cover'),
]
