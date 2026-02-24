from django.apps import AppConfig


class IndexNowConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "indexnow"

    def ready(self) -> None:
        # Import inside ready() so Django app loading can complete first.
        from .signals import connect_default_receiver

        connect_default_receiver()
