from django.apps import AppConfig


class BlogConfig(AppConfig):
    """
    Configuration class for the Blog application.

    This class sets up its name and configuration module path.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Блог'
