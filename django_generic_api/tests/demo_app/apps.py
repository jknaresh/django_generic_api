from django.apps import AppConfig


class TestAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_generic_api.tests.demo_app"
