from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Post, Comment
from .models import Post, Comment, Like
from .forms import CommentForm

@login_required
def feed(request):
    posts = Post.objects.all()
    comments = Comment.objects.all()
    comment_form = CommentForm()

    # Precompute whether the user has liked each post
    liked_posts = {post.id: post.likes.filter(user=request.user).exists() for post in posts}

    if request.method == 'POST':
        # Handle the comment submission
        if 'comment_post' in request.POST:
            post_id = request.POST.get('post_id')
            text = request.POST.get('comment_text')
            post = Post.objects.get(id=post_id)
            comment = Comment(user=request.user, post=post, text=text)
            comment.save()
            return redirect('feed')

        # Handle the like submission
        if 'like_post' in request.POST:
            post_id = request.POST.get('post_id')
            post = Post.objects.get(id=post_id)
            Like.objects.get_or_create(user=request.user, post=post)
            return redirect('feed')

    return render(request, 'accounts/feed.html', {
        'posts': posts,
        'comments': comments,
        'comment_form': comment_form,
        'liked_posts': liked_posts,  # Pass the liked posts information
    })



#@login_required
#def feed(request):
#    posts = Post.objects.all().order_by('-created_at')  # Показваме последните постове
#    comments = Comment.objects.all()
#    return render(request, 'accounts/feed.html', {'posts': posts, 'comments': comments})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'accounts/create_post.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

