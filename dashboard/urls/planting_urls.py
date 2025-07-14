# dashboard/urls/planting_urls.py

from django.urls import path
from dashboard import views

app_name = "planting"  # ✅ Enables namespacing as 'planting:plot_planting_dates' etc.

urlpatterns = [
    path("planting-dates/", views.planting_dates_view, name="planting_dates"),
    path("plot-planting-dates/", views.plot_planting_dates, name="plot_planting_dates"),
]
