resource "google_service_account" "scheduler_sa" {
  account_id   = "scheduler-sa"
  display_name = "Scheduler Service Account"
}

resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloudfunctions2_function.function.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

resource "google_cloud_scheduler_job" "job" {
  name             = "scraper-schedule"
  description      = "Trigger the scraper function every 15 minutes"
  schedule         = "*/15 7-21 * * *"
  time_zone        = "Europe/Madrid"
  attempt_deadline = "320s"

  http_target {
    http_method = "GET"
    uri         = google_cloudfunctions2_function.function.service_config[0].uri

    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
      audience              = "${google_cloudfunctions2_function.function.service_config[0].uri}/"
    }
  }
}
