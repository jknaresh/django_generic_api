from django.urls import path
from .views import GenericFetchAPIView, GenericSaveAPIView

urlpatterns = [
    path("fetch/", GenericFetchAPIView.as_view(), name="generic-fetch"),
    path("save/", GenericSaveAPIView.as_view(), name="generic-save"),
]
