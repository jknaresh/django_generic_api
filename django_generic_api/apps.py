from django.apps import AppConfig
from django.conf import settings


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
                "user": "2000/hour",  # Rate limit for authenticated users
                "anon": "20/hour",  # Rate limit for unauthenticated users,
                # 20 request per 1 hour
            },
            "EXCEPTION_HANDLER": "django_generic_api.utils.custom_exception_handler",
        }

        # Apply these defaults directly to `REST_FRAMEWORK` settings
        if not hasattr(settings, "REST_FRAMEWORK"):
            setattr(settings, "REST_FRAMEWORK", {})

        # Apply these defaults directly to `api_settings`
        for key, value in DEFAULT_DRF_THROTTLE_SETTINGS.items():
            if key not in settings.REST_FRAMEWORK:
                settings.REST_FRAMEWORK[key] = value

        # Predefining cache settings
        GENERIC_API_PACKAGE_CACHE_SETTINGS = {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-cache-name",
        }

        """
        1. If settings does not have cache, define as cache.default.
        2. If settings does not have cache.default, add cache configuration.
        """
        if not hasattr(settings, "CACHES"):
            setattr(
                settings,
                "CACHES",
                {"default": GENERIC_API_PACKAGE_CACHE_SETTINGS},
            )
        else:
            if "default" not in settings.CACHES:
                settings.CACHES["default"] = GENERIC_API_PACKAGE_CACHE_SETTINGS
