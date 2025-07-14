# dashboard/urls/user_urls.py

from django.urls import path
from dashboard import views

app_name = "users"

urlpatterns = [
    path('user-management/', views.user_management, name='user_management'),
    path('user-management/update-status/', views.update_user_status, name='update_user_status'),
    path('update-user-modal/', views.update_user_from_modal, name='update_user_from_modal'),
]
