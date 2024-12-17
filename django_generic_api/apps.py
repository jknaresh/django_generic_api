from django.apps import AppConfig
from django.conf import settings
from .config import (
    user_rate,
    anon_rate,
    # captcha_bg_color,
    # captcha_fg_color,
    # captcha_img_size,
    # captcha_font_size,
    # captcha_length,
)


class DjangoGenericApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_generic_api"

    def ready(self):
        # Predefining the DRF throttle settings
        DEFAULT_DRF_THROTTLE_SETTINGS = {
            "DEFAULT_THROTTLE_CLASSES": [
                # Customized anon user
                "rest_framework.throttling.AnonRateThrottle",
                # DRF authenticated user
                "rest_framework.throttling.UserRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "user": f"{user_rate}/hour",  # Rate limit for authenticated users
                "anon": f"{anon_rate}/hour",  # Rate limit for unauthenticated users,
            },
            "EXCEPTION_HANDLER": "django_generic_api.utils.custom_exception_handler",
        }

        # Apply these defaults directly to `REST_FRAMEWORK` settings
        if not hasattr(settings, "REST_FRAMEWORK"):
            setattr(settings, "REST_FRAMEWORK", {})

        # Apply these defaults directly to `api_settings`
        for key, value in DEFAULT_DRF_THROTTLE_SETTINGS.items():
            if not settings.REST_FRAMEWORK.get(key):
                settings.REST_FRAMEWORK[key] = value

        # # Captcha Settings
        # if not hasattr(settings, "CAPTCHA_BACKGROUND_COLOR"):
        #     setattr(settings, "CAPTCHA_BACKGROUND_COLOR", captcha_bg_color)
        # if not hasattr(settings, "CAPTCHA_FOREGROUND_COLOR"):
        #     setattr(settings, "CAPTCHA_FOREGROUND_COLOR", captcha_fg_color)
        # if not hasattr(settings, "CAPTCHA_IMAGE_SIZE"):
        #     setattr(settings, "CAPTCHA_IMAGE_SIZE", captcha_img_size)
        # if not hasattr(settings, "CAPTCHA_FONT_SIZE"):
        #     setattr(settings, "CAPTCHA_FONT_SIZE", captcha_font_size)
        # if not hasattr(settings, "CAPTCHA_LENGTH"):
        #     setattr(settings, "CAPTCHA_LENGTH", captcha_length)
