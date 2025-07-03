from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from dashboard import views
from dashboard.views import (
    index,
    upload_csv,
    upload_schedule_csv,
    export_trait_status_csv,
    save_trait_edits,
    update_trait_value,
    plant_trait_history,
    plant_snapshot,
    download_plant_history_csv,
    trait_status_table,
    trait_heatmap_view,
    planting_dates_view,
    plot_planting_dates,
    bulk_gps_assignment,
    field_visualization_view,
    field_map_view,
    plot_coordinates_api,
)

urlpatterns = [
    # Admin and Auth
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Home
    path('', index, name='index'),

    # Uploads
    path('upload/', upload_csv, name='upload_csv'),
    path('upload-schedule/', upload_schedule_csv, name='upload_schedule'),

    # Exports
    path('export/', export_trait_status_csv, name='export_csv'),

    # Trait edits
    path('save-edits/', save_trait_edits, name='save_trait_edits'),
    path('update-trait/', update_trait_value, name='update_trait'),

    # Trait progress and visualization
    path('trait-status/', trait_status_table, name='trait_status_table'),
    path('trait-heatmap/', trait_heatmap_view, name='trait_heatmap'),

    # Planting dates
    path('planting-dates/', planting_dates_view, name='planting_dates'),
    path('plot-planting-dates/', plot_planting_dates, name='plot_planting_dates'),

    # GPS and map views
    path('bulk-gps/', bulk_gps_assignment, name='bulk_gps'),
    path('field-visualization/', field_visualization_view, name='field_visualization'),
    path('field-map/', field_map_view, name='field_map'),
    path('api/plot-coordinates/', plot_coordinates_api, name='plot_coordinates_api'),

    # Trait history
    path('history/<str:plant_id>/', plant_trait_history, name='plant_trait_history'),
    path('snapshot/<str:plant_id>/', plant_snapshot, name='plant_snapshot'),
    path('snapshot/<str:plant_id>/download/', download_plant_history_csv, name='download_plant_history_csv'),
    
    # Trait Reminder
    path('reminder-dashboard/', views.trait_reminder_dashboard, name='trait_reminder_dashboard'),

]
