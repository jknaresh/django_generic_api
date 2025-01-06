import os
import sys

import django
from django.conf import settings
from django.core.management import call_command

sys.path.extend(
    [
        os.path.dirname(os.path.dirname(__file__)),  # Base directory
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "tests"
        ),  # Tests directory
    ]
)


def pytest_configure():
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "rest_framework",
            "rest_framework_simplejwt",
            "django_generic_api",
            "django_generic_api.tests.demo_app",
            "captcha",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        SECRET_KEY="test-secret-key",
        ALLOWED_HOSTS=["*"],
        ROOT_URLCONF="django_generic_api.django_generic_api.urls",
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
            ),
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",
                "rest_framework.throttling.UserRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "user": "2000/hour",  # Rate limit for authenticated users
                "anon": "100/hour",  # Rate limit for unauthenticated users,
                # 100 request per 1 hour
            },
            "EXCEPTION_HANDLER": "django_generic_api.django_generic_api.utils"
            ".custom_exception_handler",
        },
        CORS_ALLOWED_ORIGINS=["http://192.168.2.218", "http://localhost:8599"],
        CORS_ALLOW_ALL_ORIGINS=True,
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation"
                ".UserAttributeSimilarityValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation"
                ".MinimumLengthValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation"
                ".CommonPasswordValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation"
                ".NumericPasswordValidator",
            },
        ],
        CAPTCHA_BACKGROUND_COLOR="#ffffff",
        CAPTCHA_FOREGROUND_COLOR="#d4c9c9",
        CAPTCHA_IMAGE_SIZE=(200, 200),
        CAPTCHA_FONT_SIZE=25,
        CAPTCHA_LENGTH=7,
    )

    django.setup()
    call_command("makemigrations", "demo_app")
    call_command("migrate")
