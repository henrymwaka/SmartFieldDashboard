# api/urls.py

from django.urls import path, include
from . import views
urlpatterns = [
    path('ping/', views.ping, name='ping'),  # test route
    path("api/", include("api.urls")),
]
