import django
from django.conf import settings
from django.core.management import call_command
import os
import sys

# Add the base directory to sys.path for clean imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def pytest_configure():

    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "rest_framework",
            "rest_framework_simplejwt",
            "django_generic_api",
            "django_generic_api.tests.demo_app",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        SECRET_KEY="test-secret-key",
        ALLOWED_HOSTS=["*"],
        ROOT_URLCONF="django_generic_api.urls",
        BASE_URL="http://127.0.0.1:8050",
        MIDDLEWARE=[
            "corsheaders.middleware.CorsMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
        REST_FRAMEWORK={
            "DEFAULT_AUTHENTICATION_CLASSES": (
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            )
        },
        CORS_ALLOWED_ORIGINS=["http://192.168.2.218", "http://localhost:8599"],
        CORS_ALLOW_ALL_ORIGINS=True,
    )

    django.setup()
    call_command("makemigrations", "demo_app")
    call_command("migrate")
