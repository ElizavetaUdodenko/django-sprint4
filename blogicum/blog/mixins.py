from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect

from .models import Comment


class OnlyAuthorMixin(UserPassesTestMixin):
    """Restrict access to views only for the author of the object."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentMixin:
    """Mixin for retrieving comments by post_id and comment_id."""

    model = Comment

    def get_object(self, queryset=None):
        return (
            get_object_or_404(
                Comment,
                pk=self.kwargs['comment_id'],
                post_id=self.kwargs['post_id']
            )
        )
