from django.contrib.auth import get_user_model
from django.db import models

from blogicum.settings import MAX_LENGTH
from core.models import TimeStampedPublishedModel

User = get_user_model()


class Location(TimeStampedPublishedModel):
    """
    Model representing a location where the post was published from.

    Attributes:
        name (CharField): The location name where post was published from.
    """

    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return f'Location: {self.name} (ID: {self.pk})'


class Category(TimeStampedPublishedModel):
    """
    Model representing a blog category.

    Attributes:
        title (CharField): The title of the category.
        description (TextField): The full description of the category.
        slug (SlugField): The slug (URL-friendly name) of the category.
    """

    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'Category: {self.title} (ID: {self.pk})'


class Post(TimeStampedPublishedModel):
    """
    Model representing a blog post.

    Attributes:
        title (CharField): The title of the post.
        text (TextField): The full text content of the post.
        pub_date (DateTimeField): The date and time when the post was last
            published.
        author (ForeignKey): The author who created the post.
        location (ForeignKey): The location this post was published from.
        category (ForeignKey): The category this post belongs to.
    """

    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now=False,
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — можно делать '
            'отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts_images',
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-created_at', 'title')
        default_related_name = 'posts'

    def __str__(self):
        return f'Post: {self.title} by {self.author.username}'


class Comment(models.Model):
    """
    Model representing a comment attached to the specific post.

    Attributes:
        text (TextField): The full text content of the comment.
        post (ForeignKey): The post that the comment is attached to.
        author (ForeignKey): The author who created the comment.
        created_at (DateTimeField): The time stamp when th comment was created.
    """

    text = models.TextField('Комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Соответсвующая публикация'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментария'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return f'Comment by {self.author.username} on Post ID {self.post.pk}'
