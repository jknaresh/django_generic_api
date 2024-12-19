from captcha import urls as captcha_urls
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    GenericFetchAPIView,
    GenericSaveAPIView,
    LogoutAPIView,
    GenericLoginAPIView,
    GenericRegisterAPIView,
    AccountActivateAPIView,
    GenericForgotPasswordAPIView,
    CaptchaServiceAPIView,
    NewPasswordAPIView,
)

urlpatterns = [
    path("fetch/", GenericFetchAPIView.as_view(), name="generic-fetch"),
    path("save/", GenericSaveAPIView.as_view(), name="generic-save"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("login/", GenericLoginAPIView.as_view(), name="login"),
    path("register/", GenericRegisterAPIView.as_view(), name="register"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "activate/<str:encoded_token>/",
        AccountActivateAPIView.as_view(),
        name="activate",
    ),
    path(
        "forgotPassword/",
        GenericForgotPasswordAPIView.as_view(),
        name="forgotPassword",
    ),
    path("generate_captcha/", CaptchaServiceAPIView.as_view(), name="captcha"),
    path(
        "newpassword/<str:encoded_token>/",
        NewPasswordAPIView.as_view(),
        name="newpassword",
    ),
    path("captcha/", include(captcha_urls)),
]
