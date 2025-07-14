# dashboard/urls/mail_urls.py

from django.urls import path
from dashboard import views

urlpatterns = [
    path("test-email/", views.test_email, name="test_email"),
]
