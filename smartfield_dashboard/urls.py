from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from dashboard import views

# -------------------------------------------------------------------
# Swagger / API Schema Configuration
# -------------------------------------------------------------------
schema_view = get_schema_view(
    openapi.Info(
        title="SmartField BrAPI",
        default_version='v2',
        description="API documentation for SmartField BrAPI endpoints",
        contact=openapi.Contact(email="henry.mwaka@naro.go.ug"),
        license=openapi.License(name="Apache 2.0"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# -------------------------------------------------------------------
# URL Patterns
# -------------------------------------------------------------------
urlpatterns = [
    # Admin & Authentication
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='dashboard/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='dashboard/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset_complete.html'), name='password_reset_complete'),

    # Swagger & ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # OAuth2
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    # BrAPI Endpoints
    path('brapi/v2/', include('dashboard.urls.brapi_urls')),

    # Base Dashboard Page
    path('', views.index, name='index'),

    # Modular Dashboard Includes with Namespaces
    path('dashboard/', include('dashboard.urls')),  # General dashboard views
    path('dashboard/traits/', include(('dashboard.urls.trait_urls', 'traits'), namespace='traits')),
    path('dashboard/gps/', include(('dashboard.urls.gps_urls', 'gps'), namespace='gps')),
    path('dashboard/users/', include(('dashboard.urls.user_urls', 'users'), namespace='users')),
    path('dashboard/planting/', include(('dashboard.urls.planting_urls', 'planting'), namespace='planting')),
    path('dashboard/exports/', include(('dashboard.urls.export_urls', 'exports'), namespace='exports')),
    path('dashboard/mail/', include(('dashboard.urls.mail_urls', 'mail'), namespace='mail')),
    path('update-actual-date/', views.update_actual_date_ajax, name='update_actual_date_ajax'),



    # GPS & Mapping Views
    path('bulk-gps/', views.bulk_gps_assignment, name='bulk_gps'),
    path('field-visualization/', views.field_visualization_view, name='field_visualization'),
    path('field-map/', views.field_map_view, name='field_map'),
    path('api/plot-coordinates/', views.plot_coordinates_api, name='plot_coordinates_api'),

    # Planting Dates
    path('planting-dates/', views.planting_dates_view, name='planting_dates'),
    path('plot-planting-dates/', views.plot_planting_dates, name='plot_planting_dates'),

    # User Management
    path('user-management/', views.user_management, name='user_management'),
    path('user-management/update-status/', views.update_user_status, name='update_user_status'),
    path('update-user-modal/', views.update_user_from_modal, name='update_user_from_modal'),

    # Miscellaneous
    path('test-email/', views.test_email, name='test_email'),
]
