from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration class for the Core application.

    This class sets up its name and configuration module path.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
