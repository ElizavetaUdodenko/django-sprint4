from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blogicum.settings import POSTS_PER_PAGE

from .forms import CommentForm, PostForm, UserUpdateForm
from .mixins import OnlyAuthorMixin, CommentMixin
from .models import Category, Comment, Post

User = get_user_model()

POST_NOT_FOUND_MESSAGE = 'Post Not Found.'


def get_user(username):
    """Return the user object based on the provided username."""
    return get_object_or_404(User, username=username)


def get_published_category(category_slug):
    """Return a published category based on the provided slug."""
    return (
        get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
    )


def get_posts(apply_general_filter=False, apply_comments_count=False):
    """
    Return a queryset of posts with optional filtering and comment counting.

    Args:
        apply_general_filter (bool): Whether to filter by publication status.
        apply_comments_count (bool): Whether to annotate comment count.

    Returns:
        QuerySet: The filtered and/or annotated queryset of posts.
    """
    posts = Post.objects.select_related('author', 'category', 'location')
    if apply_general_filter:
        posts = posts.filter(
            category__is_published=True,
            is_published=True,
            pub_date__date__lte=timezone.now()
        )
    if apply_comments_count:
        posts = (
            posts.annotate(comment_count=Count('comments'))
            .order_by('-pub_date', 'title')
        )
    return posts


class BlogLogoutView(LoginRequiredMixin, LogoutView):
    """Custom logout view that renders a logout confirmation page."""

    def get(self, request):
        logout(request)
        return render(request, 'registration/logged_out.html')


class PostsListView(ListView):
    """Display the homepage with the list of published posts."""

    template_name = 'blog/index.html'
    queryset = get_posts(apply_general_filter=True, apply_comments_count=True)
    paginate_by = POSTS_PER_PAGE


class ProfileDetailView(ListView):
    """Display a user's profile and their posts."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        user = get_user(self.kwargs['username'])
        if self.request.user.is_authenticated and self.request.user == user:
            posts = posts = get_posts(
                apply_general_filter=False,
                apply_comments_count=True
            )
        else:
            posts = get_posts(
                apply_general_filter=True,
                apply_comments_count=True
            )
        posts = posts.filter(author=user)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {
            'profile': get_user(self.kwargs['username']),
            'page_obj': self.get_queryset()
        }
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Allow the user to update their profile."""

    model = User
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CategoryListView(ListView):
    """Display all posts related to the requested category."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        category = get_published_category(self.kwargs['category_slug'])
        return (
            get_posts(apply_general_filter=True, apply_comments_count=True)
            .filter(category=category)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = (
            get_published_category(self.kwargs['category_slug'])
        )
        return context


class PostDetailView(DetailView):
    """Display a specific post with its comments."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if (
            self.request.user != post.author
            and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date >= timezone.now()
            )
        ):
            raise Http404(POST_NOT_FOUND_MESSAGE)
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = (
            Comment.objects
            .select_related('author')
            .filter(post=self.object)
        )
        context['form'] = CommentForm()
        context['comments'] = comments
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Allow logged-in users to create a new post."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Allow authors to update their posts."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Allow authors to delete their posts."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Allow logged-in users to create comments for posts."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(OnlyAuthorMixin, CommentMixin, UpdateView):
    """Allow authors to update their comments."""

    form_class = CommentForm
    template_name = 'blog/comment.html'


class CommentDeleteView(OnlyAuthorMixin, CommentMixin, DeleteView):
    """Allow authors to delete their comments."""

    template_name = 'blog/comment.html'
