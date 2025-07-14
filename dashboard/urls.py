# dashboard/urls.py
from django.urls import path, include
from . import views

app_name = "dashboard"  # Optional but helpful for namespacing if used elsewhere

urlpatterns = [
    # Core views
    path('', views.index, name='index'),
    path('update-actual-date/', views.update_actual_date_ajax, name='update_actual_date_ajax'),
    path('upload-brapi-data/', views.upload_brapi_data_view, name='upload_brapi_data'),

    # Modular includes with correct namespaces
    path('traits/', include(('dashboard.urls.trait_urls', 'traits'), namespace='traits')),
    path('gps/', include(('dashboard.urls.gps_urls', 'gps'), namespace='gps')),
    path('users/', include(('dashboard.urls.user_urls', 'users'), namespace='users')),
    path('planting/', include(('dashboard.urls.planting_urls', 'planting'), namespace='planting')),
    path('exports/', include(('dashboard.urls.export_urls', 'exports'), namespace='exports')),
    path('mail/', include(('dashboard.urls.mail_urls', 'mail'), namespace='mail')),
]
