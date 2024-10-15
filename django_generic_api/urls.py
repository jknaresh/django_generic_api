from django.urls import path

from .views import (
    GenericFetchAPIView,
    GenericSaveAPIView,
    LogoutAPIView,
    GenericLoginAPIView,
    GenericRegisterAPIView,
    EmailActivateAPIView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path("fetch/", GenericFetchAPIView.as_view(), name="generic-fetch"),
    path("save/", GenericSaveAPIView.as_view(), name="generic-save"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("login/", GenericLoginAPIView.as_view(), name="login"),
    path("register/", GenericRegisterAPIView.as_view(), name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "activate/<str:encoded_token>/", EmailActivateAPIView.as_view(), name="activate"
    ),
]
