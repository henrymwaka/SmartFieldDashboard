from django.urls import path
from dashboard import views

urlpatterns = [
    path("upload-csv/", views.upload_csv, name="upload_csv"),
    path("upload-schedule/", views.upload_schedule_csv, name="upload_schedule"),
    path("export/", views.export_trait_status_csv, name="export_trait_status_csv"),
    path("export/pdf/", views.export_trait_pdf, name="export_trait_pdf"),
    path("export-trait-reminders-pdf/", views.export_trait_reminders_pdf, name="export_trait_reminders_pdf"),
    path("export-trait-status-pdf/", views.export_trait_status_pdf, name="export_trait_status_pdf"),
    path("upload-trait-status-csv/", views.upload_trait_status_csv, name="upload_trait_status_csv"),

]
