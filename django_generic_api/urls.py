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
    UserInfoAPIView,
)

urlpatterns = [
    path("v1/fetch/", GenericFetchAPIView.as_view(), name="generic-fetch"),
    path("v1/save/", GenericSaveAPIView.as_view(), name="generic-save"),
    path("v1/logout/", LogoutAPIView.as_view(), name="logout"),
    path("v1/login/", GenericLoginAPIView.as_view(), name="login"),
    path("v1/register/", GenericRegisterAPIView.as_view(), name="register"),
    path("v1/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "v1/activate/<str:encoded_token>/",
        AccountActivateAPIView.as_view(),
        name="activate",
    ),
    path(
        "v1/forgotPassword/",
        GenericForgotPasswordAPIView.as_view(),
        name="forgotPassword",
    ),
    path(
        "v1/generate-captcha/", CaptchaServiceAPIView.as_view(), name="captcha"
    ),
    path(
        "v1/newpassword/<str:encoded_token>/",
        NewPasswordAPIView.as_view(),
        name="newpassword",
    ),
    path("v1/captcha/", include(captcha_urls)),
    path("v1/user-info/", UserInfoAPIView.as_view(), name="user_info"),
]
