from django.urls import path
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from .views import (
    FeedView, CreatePostView, ProfileView, RegisterView, UserLoginView,
    delete_post, upload_banner, upload_profile_picture, admin_create_user, admin_create_post, admin_delete_user, admin_edit_user, admin_delete_post, admin_edit_post, admin_users, toggle_like, edit_profile, delete_account, user_profile, edit_post, custom_logout, user_profile, admin_posts,
)

urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
    path('create_post/', CreatePostView.as_view(), name='create_post'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('toggle_like/<int:post_id>/', toggle_like, name='toggle_like'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('delete_account/', delete_account, name='delete_account'),
    path('profile/<int:user_id>/', user_profile, name='user_profile'),
    path('edit-post/<int:post_id>/', edit_post, name='edit_post'),
    path('admin/', admin_posts, name='admin_posts'),
    path('admin/users/', admin_users, name='admin_users'),
    path('admin/posts/create/', admin_create_post, name='admin_create_post'),
    path('admin/users/create/', admin_create_user, name='admin_create_user'),
    path('admin/posts/edit/<int:post_id>/', admin_edit_post, name='admin_edit_post'),
    path('admin/posts/delete/<int:post_id>/', admin_delete_post, name='admin_delete_post'),
    path('admin/users/edit/<int:user_id>/', admin_edit_user, name='admin_edit_user'),
    path('admin/users/delete/<int:user_id>/', admin_delete_user, name='admin_delete_user'),
    path('upload_profile_picture/', upload_profile_picture, name='upload_profile_picture'),
    path('upload_banner/', upload_banner, name='upload_banner'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

