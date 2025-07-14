# dashboard/urls/__init__.py

from django.urls import path, include
from dashboard import views

app_name = "dashboard"  # Optional but good for reverse URL resolution

urlpatterns = [
    path('', views.index, name='dashboard_home'),
    path('traits/', include(('dashboard.urls.trait_urls', 'traits'), namespace='traits')),
    path('gps/', include(('dashboard.urls.gps_urls', 'gps'), namespace='gps')),
    path('users/', include(('dashboard.urls.user_urls', 'users'), namespace='users')),
    path('planting/', include(('dashboard.urls.planting_urls', 'planting'), namespace='planting')),
    path('exports/', include(('dashboard.urls.export_urls', 'exports'), namespace='exports')),
    path('mail/', include(('dashboard.urls.mail_urls', 'mail'), namespace='mail')),
]
