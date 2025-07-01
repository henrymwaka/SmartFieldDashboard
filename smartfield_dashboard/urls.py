from dashboard.views import trait_status_table
from django.contrib import admin
from django.urls import path
from dashboard import views
from dashboard.views import plot_coordinates_api, field_map_view, bulk_gps_assignment
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
    path('update-trait/', views.update_trait_value, name='update_trait'),
    path('trait-status/', trait_status_table, name='trait_status_table'),
    path('trait-status/', views.trait_status_table, name='trait_status_table'),


    # Bulk GPS assignment form
    path('bulk-gps/', bulk_gps_assignment, name='bulk_gps'),

    # Field visualization + GPS routes
    path('field-visualization/', views.field_visualization_view, name='field_visualization'),
    path('field-map/', field_map_view, name='field_map'),
    path('api/plot-coordinates/', plot_coordinates_api, name='plot_coordinates_api'),

    # Trait history and snapshot routes
    path('history/<str:plant_id>/', views.plant_trait_history, name='plant_trait_history'),
    path('snapshot/<str:plant_id>/', views.plant_snapshot, name='plant_snapshot'),
    path('snapshot/<str:plant_id>/download/', views.download_plant_history_csv, name='download_plant_history_csv'),
]
