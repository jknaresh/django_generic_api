from django.urls import path

from .views import (
    GenericFetchAPIView,
    GenericSaveAPIView,
    LoginAPIView,
    LogoutAPIView,
)

urlpatterns = [
    path("fetch/", GenericFetchAPIView.as_view(), name="generic-fetch"),
    path("save/", GenericSaveAPIView.as_view(), name="generic-save"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
