from django.contrib import admin
from django.urls import path
from dashboard import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('upload-schedule/', views.upload_schedule_csv, name='upload_schedule'),
    path('export/', views.export_trait_status_csv, name='export_csv'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('save-edits/', views.save_trait_edits, name='save_trait_edits'),
path('history/<str:plant_id>/', views.plant_trait_history, name='plant_trait_history'),


    # ✅ Add this new path for AJAX updates
    path('update-trait/', views.update_trait_value, name='update_trait'),
]
