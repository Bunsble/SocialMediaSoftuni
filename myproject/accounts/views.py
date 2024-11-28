from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from .forms import CustomUserCreationForm, CommentForm, PostForm
from .models import Post, Comment, Like, CustomUser
from django.shortcuts import render, redirect
from django.db import connection
from .forms import EditProfileForm

from django.db.models import Q

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(request, 'accounts/delete_account.html')


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from .forms import CustomUserCreationForm, CommentForm, PostForm, EditProfileForm
from .models import Post, Comment, Like, CustomUser
from django.shortcuts import render, redirect
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib import messages
from django.contrib.auth.hashers import make_password

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Get the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        date_of_birth = request.POST.get('date_of_birth')
        password = request.POST.get('password')
        profile_image = request.FILES.get('profile_image')
        banner_image = request.FILES.get('banner_image')

        # Update the user's information using raw SQL
        with connection.cursor() as cursor:
            if password:
                # If password is provided, update it along with other fields
                hashed_password = make_password(password)
                cursor.execute("""
                    UPDATE accounts_customuser
                    SET username = %s, email = %s, first_name = %s, last_name = %s,
                         date_of_birth = %s, password = %s
                    WHERE id = %s
                """, [username, email, first_name, last_name, date_of_birth, hashed_password, request.user.id])
            else:
                # If no password provided, update other fields only
                cursor.execute("""
                    UPDATE accounts_customuser
                    SET username = %s, email = %s, first_name = %s, last_name = %s,
                         date_of_birth = %s
                    WHERE id = %s
                """, [username, email, first_name, last_name, date_of_birth, request.user.id])

        # Handle profile image upload
        if profile_image:
            file_name = f"profile_images/{request.user.id}_{profile_image.name}"
            file_path = default_storage.save(file_name, ContentFile(profile_image.read()))
            image_url = f"/media/{file_path}"
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE accounts_customuser
                    SET profile_image = %s
                    WHERE id = %s
                """, [image_url, request.user.id])

        # Handle banner image upload
        if banner_image:
            file_name = f"banner_images/{request.user.id}_{banner_image.name}"
            file_path = default_storage.save(file_name, ContentFile(banner_image.read()))
            banner_url = file_path
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE accounts_customuser
                    SET banner_image = %s
                    WHERE id = %s
                """, [banner_url, request.user.id])

        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('profile')  # Redirect to profile page after saving

    else:
        # Fetch the current user's information
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT username, email, first_name, last_name, date_of_birth, profile_image, banner_image
                FROM accounts_customuser
                WHERE id = %s
            """, [request.user.id])
            user_info = cursor.fetchone()

        context = {
            'username': user_info[0],
            'email': user_info[1],
            'first_name': user_info[2],
            'last_name': user_info[3],
            'date_of_birth': user_info[4],
            'profile_image': user_info[5],
            'banner_image': user_info[6],
        }
        return render(request, 'accounts/edit_profile.html', context)


@login_required
def toggle_like(request, post_id):
    if request.method in ['POST', 'DELETE']:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM accounts_like WHERE user_id = %s AND post_id = %s", [request.user.id, post_id])
            like_exists = cursor.fetchone()[0] > 0

            if request.method == 'POST' and not like_exists:
                cursor.execute("INSERT INTO accounts_like (user_id, post_id) VALUES (%s, %s)", [request.user.id, post_id])
                status = 'liked'
            elif request.method == 'DELETE' and like_exists:
                cursor.execute("DELETE FROM accounts_like WHERE user_id = %s AND post_id = %s", [request.user.id, post_id])
                status = 'unliked'
            else:
                status = 'unchanged'

            cursor.execute("SELECT COUNT(*) FROM accounts_like WHERE post_id = %s", [post_id])
            like_count = cursor.fetchone()[0]

        return JsonResponse({
            'status': status,
            'like_count': like_count
        })

    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_post(request, post_id):
    with connection.cursor() as cursor:
        # First, delete all comments associated with the post
        cursor.execute("""
            DELETE FROM accounts_comment
            WHERE post_id = %s
        """, [post_id])

        # Then, delete all likes associated with the post
        cursor.execute("""
            DELETE FROM accounts_like
            WHERE post_id = %s
        """, [post_id])

        # Finally, delete the post
        cursor.execute("""
            DELETE FROM accounts_post
            WHERE id = %s AND user_id = %s
        """, [post_id, request.user.id])
    return redirect('profile')



from django.views import View
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CommentForm, PostForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class FeedView(LoginRequiredMixin, View):
    template_name = 'accounts/feed.html'

    def get(self, request):
        search_query = request.GET.get('search', '')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.content, p.image, p.created_at, u.username, 
                       (SELECT COUNT(*) FROM accounts_like WHERE post_id = p.id) as like_count
                FROM accounts_post p
                JOIN accounts_customuser u ON p.user_id = u.id
                WHERE p.content LIKE %s OR u.username LIKE %s
                ORDER BY p.created_at DESC
            """, [f'%{search_query}%', f'%{search_query}%'])
            posts = cursor.fetchall()

            cursor.execute("""
                SELECT id, username, email
                FROM accounts_customuser
                WHERE username LIKE %s OR email LIKE %s
            """, [f'%{search_query}%', f'%{search_query}%'])
            users = cursor.fetchall()

            cursor.execute("""
                SELECT c.id, c.post_id, c.user_id, c.text, c.created_at, u.username
                FROM accounts_comment c
                JOIN accounts_customuser u ON c.user_id = u.id
                ORDER BY c.created_at DESC
            """)
            comments = cursor.fetchall()

        comment_form = CommentForm()

        liked_posts = set()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT post_id FROM accounts_like WHERE user_id = %s
            """, [request.user.id])
            liked_posts = {row[0] for row in cursor.fetchall()}

        return render(request, self.template_name, {
            'posts': posts,
            'users': users,
            'comments': comments,
            'comment_form': comment_form,
            'liked_posts': liked_posts,
            'search_query': search_query,
        })

    def post(self, request):
        if 'comment_post' in request.POST:
            post_id = request.POST.get('post_id')
            text = request.POST.get('comment_text')
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO accounts_comment (user_id, post_id, text, created_at) 
                    VALUES (%s, %s, %s, NOW())
                """, [request.user.id, post_id, text])
            return redirect('feed')
        return self.get(request)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .forms import PostForm
from .models import Post
import os

class CreatePostView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = 'accounts/create_post.html'
    success_url = reverse_lazy('feed')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = self.request.user

        if 'image' in form.cleaned_data and form.cleaned_data['image']:
            image = form.cleaned_data['image']
            file_name = f"posts/{self.request.user.id}_{image.name}"
            
            # Ensure the directory exists
            directory = os.path.join(settings.MEDIA_ROOT, 'posts')
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Save the file
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            # Set the image field to the path with /media/ prefix
            post.image = f"/media/{file_name}"

        post.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

        

class ProfileView(LoginRequiredMixin, ListView):
    template_name = 'accounts/profile.html'
    context_object_name = 'posts'

    def get_queryset(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, content, image, created_at
                FROM accounts_post
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, [self.request.user.id])
            return cursor.fetchall()

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Registration successful!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please correct the errors.')
        return super().form_invalid(form)

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Login successful!')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)

from django.shortcuts import render, get_object_or_404

def user_profile(request, user_id):
    with connection.cursor() as cursor:
        # Fetch user information including profile picture and banner image
        cursor.execute("""
            SELECT id, username, email, first_name, last_name, date_of_birth, profile_image, banner_image
            FROM accounts_customuser
            WHERE id = %s
        """, [user_id])
        user_info = cursor.fetchone()

        if not user_info:
            return render(request, '404.html', status=404)

        # Fetch user's posts
        cursor.execute("""
            SELECT id, content, image, created_at
            FROM accounts_post
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, [user_id])
        posts = cursor.fetchall()

    context = {
        'user_info': user_info,
        'posts': posts,
    }
    return render(request, 'accounts/user_profile.html', context)

    
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('home')  # or wherever you want to redirect after logout

    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import connection
from .forms import PostForm

@login_required
def edit_post(request, post_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, content, image
            FROM accounts_post
            WHERE id = %s AND user_id = %s
        """, [post_id, request.user.id])
        post = cursor.fetchone()

    if not post:
        return redirect('profile')  # Or to a 404 page

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data['content']
            image = form.cleaned_data['image']

            if image:
                file_name = f"posts/{request.user.id}_{image.name}"
                file_path = default_storage.save(file_name, ContentFile(image.read()))
                image_url = default_storage.url(file_path)
            else:
                image_url = post[2]  # Keep the existing image if no new image is uploaded

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE accounts_post
                    SET content = %s, image = %s
                    WHERE id = %s AND user_id = %s
                """, [content, image_url, post_id, request.user.id])

            return redirect('profile')
    else:
        form = PostForm(initial={'content': post[1], 'image': post[2]})

    return render(request, 'accounts/edit_post.html', {'form': form, 'post_id': post_id})



from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, CustomUser

def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser

from django.db.models import Q

@user_passes_test(is_staff_or_superuser)
def admin_posts(request):
    search_query = request.GET.get('search', '')
    posts = Post.objects.all().order_by('-created_at')
    
    if search_query:
        posts = posts.filter(
            Q(user__username__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    return render(request, 'admin/posts.html', {'posts': posts, 'active_tab': 'posts', 'search_query': search_query})

@user_passes_test(lambda u: u.is_superuser)
def admin_users(request):
    search_query = request.GET.get('search', '')
    users = CustomUser.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    return render(request, 'admin/users.html', {'users': users, 'active_tab': 'users', 'search_query': search_query})


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

@login_required
def upload_profile_picture(request):
    if request.method == 'POST':
        if request.FILES.get('profile_picture'):
            request.user.profile_picture = request.FILES['profile_picture']
            request.user.save()
            messages.success(request, 'Profile picture updated successfully.')
        else:
            messages.error(request, 'No file was uploaded.')
    return redirect('profile')

@login_required
def upload_banner(request):
    if request.method == 'POST':
        if request.FILES.get('banner'):
            request.user.banner_image = request.FILES['banner']
            request.user.save()
            messages.success(request, 'Banner image updated successfully.')
        else:
            messages.error(request, 'No file was uploaded.')
    return redirect('profile')

@user_passes_test(is_staff_or_superuser)
def admin_edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        # Handle post edit
        post.content = request.POST.get('content')
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.save()
        return redirect('admin_posts')
    return render(request, 'admin/edit_post.html', {'post': post, 'active_tab': 'posts'})


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from .forms import AdminPostForm, AdminUserCreationForm

@user_passes_test(lambda u: u.is_superuser)
def admin_create_post(request):
    if request.method == 'POST':
        form = AdminPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('admin_posts')
    else:
        form = AdminPostForm()
    return render(request, 'admin/create_post.html', {'form': form, 'active_tab': 'posts'})

@user_passes_test(lambda u: u.is_superuser)
def admin_create_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_users')
    else:
        form = AdminUserCreationForm()
    return render(request, 'admin/create_user.html', {'form': form, 'active_tab': 'users'})



@user_passes_test(is_staff_or_superuser)
def admin_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('admin_posts')

@user_passes_test(lambda u: u.is_superuser)
def admin_edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        # Handle user edit
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.is_staff = 'is_staff' in request.POST
        user.save()
        return redirect('admin_users')
    return render(request, 'admin/edit_user.html', {'edit_user': user})

@user_passes_test(lambda u: u.is_superuser)
def admin_delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_superuser:
        user.delete()
    return redirect('admin_users')


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser

@user_passes_test(lambda u: u.is_superuser)
def admin_edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.is_staff = 'is_staff' in request.POST
        user.save()
        return redirect('admin_users')
    return render(request, 'admin/edit_user.html', {'user': user, 'active_tab': 'users'})

@user_passes_test(lambda u: u.is_superuser)
def admin_delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_superuser:
        user.delete()
    return redirect('admin_users')
