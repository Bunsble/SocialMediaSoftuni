from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),  # Път към профила
    path('create_post/', views.create_post, name='create_post'),
    path('feed/', views.feed, name='feed'),  # Добавяме URL за feed
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
