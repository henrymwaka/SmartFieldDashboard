from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from dashboard import views

urlpatterns = [
    # Admin and Auth
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Home
    path('', views.index, name='index'),

    # Uploads
    path('upload/', views.upload_csv, name='upload_csv'),
    path('upload-schedule/', views.upload_schedule_csv, name='upload_schedule'),

    # Exports
    path('export/', views.export_trait_status_csv, name='export_csv'),
    path("export/pdf/", views.export_trait_pdf, name="export_trait_pdf"),
    path("export-trait-reminders-pdf/", views.export_trait_reminders_pdf, name="export_trait_reminders_pdf"),

    # Trait edits
    path('save-edits/', views.save_trait_edits, name='save_trait_edits'),
    path('update-trait/', views.update_trait_value, name='update_trait'),

    # Trait progress and visualization
    path('trait-status/', views.trait_status_table, name='trait_status_table'),
    path('trait-heatmap/', views.trait_heatmap_view, name='trait_heatmap'),

    # Planting dates
    path('planting-dates/', views.planting_dates_view, name='planting_dates'),
    path('plot-planting-dates/', views.plot_planting_dates, name='plot_planting_dates'),

    # GPS and map views
    path('bulk-gps/', views.bulk_gps_assignment, name='bulk_gps'),
    path('field-visualization/', views.field_visualization_view, name='field_visualization'),
    path('field-map/', views.field_map_view, name='field_map'),
    path('api/plot-coordinates/', views.plot_coordinates_api, name='plot_coordinates_api'),

    # Trait history
    path('history/<str:plant_id>/', views.plant_trait_history, name='plant_trait_history'),
    path('snapshot/<str:plant_id>/', views.plant_snapshot, name='plant_snapshot'),
    path('snapshot/<str:plant_id>/download/', views.download_plant_history_csv, name='download_plant_history_csv'),

    # Trait Reminder Dashboard
    path('reminder-dashboard/', views.trait_reminder_dashboard, name='trait_reminder_dashboard'),

    # Test Email
    path('test-email/', views.test_email, name='test_email'),
]
