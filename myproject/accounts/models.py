from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


#class Post(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    content = models.TextField()
#    image = models.ImageField(upload_to='posts/', blank=True, null=True)
#    created_at = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return f"Post by {self.user.username} at {self.created_at}"

#class Comment(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
#    content = models.TextField()
#    created_at = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return f"Comment by {self.user.username} on {self.post.id}"

#class Like(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
#
#    def __str__(self):
#        return f"Like by {self.user.username} on {self.post.id}"


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username
