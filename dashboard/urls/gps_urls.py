# dashboard/urls/gps_urls.py

from django.urls import path
from dashboard import views

app_name = "gps"

urlpatterns = [
    path('field-map/', views.field_map_view, name='field_map'),
    path('field-visualization/', views.field_visualization_view, name='field_visualization'),
    path('bulk-gps/', views.bulk_gps_assignment, name='bulk_gps'),
    path('api/plot-coordinates/', views.plot_coordinates_api, name='plot_coordinates_api'),
]
