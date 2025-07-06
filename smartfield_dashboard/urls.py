from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

from dashboard import views  # general views (e.g., login, dashboard)
from dashboard import brapi_views  # all BrAPI-related views




urlpatterns = [
    # Admin and Auth
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    # BrAPI
    path('brapi/v2/calls', brapi_views.brapi_calls, name='brapi-calls'),
    path('brapi/v2/commoncropnames', brapi_views.brapi_commoncropnames, name='brapi_commoncropnames'),
    path('brapi/v2/germplasm', brapi_views.brapi_germplasm, name='brapi_germplasm'),
    path('brapi/v2/germplasm/<int:germplasmDbId>', brapi_views.brapi_germplasm_detail, name='brapi_germplasm_detail'),
    path('brapi/v2/locations', brapi_views.brapi_locations, name='brapi_locations'),
    path('brapi/v2/observationunits', brapi_views.brapi_observationunits, name='brapi-observationunits'),
    path('brapi/v2/observationvariables', brapi_views.brapi_observationvariables, name='brapi-observationvariables'),
    path('brapi/v2/observations', brapi_views.brapi_observations, name='brapi-observations'),
    path('brapi/v2/programs', brapi_views.brapi_programs, name='brapi_programs'),
    path('brapi/v2/studies', brapi_views.brapi_studies, name='brapi-studies'),
    path('brapi/v2/studies/<str:studyDbId>', brapi_views.brapi_study_detail, name='brapi_study_detail'),
    path('brapi/v2/studies/<str:studyDbId>/observationunits', brapi_views.brapi_study_observationunits, name='brapi_study_observationunits'),
    path('brapi/v2/trials', brapi_views.brapi_trials, name='brapi-trials'),
    path('brapi/v2/genotypes', brapi_views.brapi_genotypes, name='brapi_genotypes'),
    path('brapi/v2/phenotypes', brapi_views.brapi_phenotypes, name='brapi_phenotypes'),
    path('brapi/v2/studies-search', brapi_views.brapi_studies_search, name='brapi_studies_search'),


   
      
    # User Management
    path('user-management/', views.user_management, name='user_management'),
    path('user-management/update-status/', views.update_user_status, name='update_user_status'),
    path('update-user-modal/', views.update_user_from_modal, name='update_user_from_modal'),  # ✅ Correct name used in template

    # Password Reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='dashboard/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='dashboard/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset_complete.html'),
         name='password_reset_complete'),

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
    path("edit-traits/", views.edit_traits_view, name="edit_traits_view"),
    path('heatmap/', views.trait_heatmap_view, name='trait_heatmap_view'),

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
    path("snapshot/<str:plant_id>/pdf/", views.download_snapshot_pdf, name="download_snapshot_pdf"),
    path("snapshot/<str:plant_id>/upload/", views.upload_snapshot_csv, name="upload_snapshot_csv"),

    # Trait Reminder Dashboard
    path('reminder-dashboard/', views.trait_reminder_dashboard, name='trait_reminder_dashboard'),

    # Test Email
    path('test-email/', views.test_email, name='test_email'),
]
