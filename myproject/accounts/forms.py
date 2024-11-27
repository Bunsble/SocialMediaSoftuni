from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Post
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Add a comment...', 'rows': 4}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')
