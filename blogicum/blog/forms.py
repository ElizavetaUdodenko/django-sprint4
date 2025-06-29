from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta():
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d',
                attrs={'type': 'datetime-local'}
            )
        }


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'email')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
