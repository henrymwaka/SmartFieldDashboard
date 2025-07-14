# dashboard/urls/trait_urls.py

from django.urls import path
from dashboard import views

app_name = "traits"  # ✅ Required for namespacing in {% url 'traits:...' %}

urlpatterns = [
    # 📋 Trait Table & Heatmap
    path("trait-status/", views.trait_status_table, name="trait_status_table"),
    path("trait-heatmap/", views.trait_heatmap_view, name="trait_heatmap_view"),

    # ⏰ Timeline Dashboard
    path("reminder-dashboard/", views.trait_reminder_dashboard, name="trait_reminder_dashboard"),

    # 📝 Trait Editing
    path("edit-traits/", views.edit_traits_view, name="edit_traits_view"),
    path("save-edits/", views.save_trait_edits, name="save_trait_edits"),
    path("update-trait/", views.update_trait_value, name="update_trait_value"),
    path("update-actual-date/", views.update_actual_date_ajax, name="update_actual_date_ajax"),

    # 🔍 Snapshot & History
    path("snapshot/<str:plant_id>/", views.plant_snapshot, name="plant_snapshot"),
    path("snapshot/<str:plant_id>/download/", views.download_plant_history_csv, name="download_plant_history_csv"),
    path("snapshot/<str:plant_id>/pdf/", views.download_snapshot_pdf, name="download_snapshot_pdf"),
    path("snapshot/<str:plant_id>/upload/", views.upload_snapshot_csv, name="upload_snapshot_csv"),
    path("history/<str:plant_id>/", views.plant_trait_history, name="plant_trait_history"),

    # ⬆️ Uploads
    path("upload/", views.upload_csv, name="upload_csv"),
    path("upload-schedule/", views.upload_schedule_csv, name="upload_schedule"),
    path("upload-trait-status-csv/", views.upload_trait_status_csv, name="upload_trait_status_csv"),

    # 📤 Exports
    path("export/", views.export_trait_status_csv, name="export_trait_status_csv"),
    path("export/pdf/", views.export_trait_pdf, name="export_trait_pdf"),
    path("export-trait-reminders-pdf/", views.export_trait_reminders_pdf, name="export_trait_reminders_pdf"),
]
