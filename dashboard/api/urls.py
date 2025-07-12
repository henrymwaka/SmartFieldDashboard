from django.urls import path
from .views import ODKXSyncReceiver

urlpatterns = [
    path('sync/', ODKXSyncReceiver.as_view(), name='odkx_sync'),
]
