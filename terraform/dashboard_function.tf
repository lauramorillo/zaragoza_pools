# Dashboard Function Service Account
resource "google_service_account" "dashboard_sa" {
  account_id   = "dashboard-sa"
  display_name = "Dashboard Function Service Account"
}

# Grant Firestore access to the Service Account (viewer only)
resource "google_project_iam_member" "dashboard_firestore_viewer" {
  project = var.project_id
  role    = "roles/datastore.viewer"
  member  = "serviceAccount:${google_service_account.dashboard_sa.email}"
}

# Cloud Function (Gen 2) for Visual Dashboard
resource "google_cloudfunctions2_function" "dashboard" {
  name        = "zaragoza-pools-dashboard"
  location    = var.region
  description = "Visual Dashboard for Zaragoza pools data"

  build_config {
    runtime     = "python310"
    entry_point = "render_dashboard" # Matches the function name in dashboard.py
    environment_variables = {
      GOOGLE_FUNCTION_SOURCE = "dashboard.py"
    }
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.zip.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "256M"
    timeout_seconds       = 60
    service_account_email = google_service_account.dashboard_sa.email
  }

  depends_on = [
    google_project_service.apis,
    google_project_iam_member.dashboard_firestore_viewer
  ]
}

# Make the dashboard publicly accessible
resource "google_cloud_run_service_iam_member" "dashboard_invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloudfunctions2_function.dashboard.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "dashboard_uri" {
  value       = google_cloudfunctions2_function.dashboard.service_config[0].uri
  description = "Public URL for the Visual Dashboard"
}
