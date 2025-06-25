from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.views.generic.list import MultipleObjectMixin

from blog.models import Category, Comment, Post
from blogicum.settings import POSTS_PER_PAGE

from .forms import CommentForm, PostForm, UserUpdateForm

User = get_user_model()


def get_published_posts():
    """
    Returns a queryset of posts that are published and available for display.

    Returns:
        QuerySet: A queryset of published Post objects.
    """
    return (
        Post.objects
        .select_related('author', 'category', 'location')
        .filter(
            category__is_published=True,
            is_published=True,
            pub_date__date__lte=timezone.now()
        )
        .annotate(comment_count=Count('comments'))
    )


def redirect_to_profile_page(username):
    return reverse('blog:profile', kwargs={'username': username})


def redirect_to_post_page(post_id):
    return reverse(
        'blog:post_detail',
        kwargs={'post_id': post_id}
    )


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class BlogLogoutView(LoginRequiredMixin, LogoutView):

    def get(self, request):
        logout(request)
        return render(request, 'registration/logged_out.html')


class PostsListView(ListView):
    """Display the homepage of the website."""

    template_name = 'blog/index.html'
    queryset = get_published_posts()
    paginate_by = POSTS_PER_PAGE


class ProfileDetailView(DetailView, MultipleObjectMixin):
    """Display the profile."""

    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = POSTS_PER_PAGE

    def get_context_data(self, **kwargs):
        user = self.get_object()
        if self.request.user.is_authenticated and self.request.user == user:
            posts = (
                Post.objects
                .filter(author=user)
                .annotate(comment_count=Count('comments'))
            )
        else:
            posts = get_published_posts().filter(author=user)
        context = super().get_context_data(object_list=posts, **kwargs)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return redirect_to_profile_page(self.request.user.username)


class CategoryListView(ListView):
    """Display all posts related to the requested category."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return get_published_posts().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    """Display the full content of a specific post requested by a user."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = (
            Comment.objects
            .filter(post=self.object)
        )
        context['form'] = CommentForm()
        context['comments'] = comments
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return redirect_to_profile_page(self.request.user.username)


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return redirect_to_post_page(self.kwargs['post_id'])


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return redirect_to_profile_page(self.request.user.username)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post_id = self.kwargs['post_id']
        form.instance.post = Post.objects.get(pk=post_id)
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return redirect_to_post_page(self.kwargs['post_id'])


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return redirect_to_post_page(self.kwargs['post_id'])


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return redirect_to_post_page(self.kwargs['post_id'])
