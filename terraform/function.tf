# Zip the source code
data "archive_file" "source_zip" {
  type        = "zip"
  output_path = "/tmp/function-source.zip"
  source_dir  = "../src"
  excludes = [
    "__pycache__"
  ]
}

# Create a storage bucket for the source code
resource "google_storage_bucket" "function_bucket" {
  name                        = "${var.project_id}-function-source"
  location                    = var.region
  uniform_bucket_level_access = true
}

# Upload the zip object
resource "google_storage_bucket_object" "zip" {
  name   = "source-${data.archive_file.source_zip.output_md5}.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = data.archive_file.source_zip.output_path
}

# Function Service Account
resource "google_service_account" "function_sa" {
  account_id   = "scraper-sa"
  display_name = "Scraper Function Service Account"
}

# Grant Firestore access to the Service Account
resource "google_project_iam_member" "firestore_owner" {
  project = var.project_id
  role    = "roles/datastore.owner"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

# Cloud Function (Gen 2)
resource "google_cloudfunctions2_function" "function" {
  name        = "zaragoza-pools-scraper"
  location    = var.region
  description = "Scrapes Zaragoza pools data and stores in Firestore"

  build_config {
    runtime     = "python310"
    entry_point = "main" # Matches the function name in scraper.py
    environment_variables = {
      GOOGLE_FUNCTION_SOURCE = "scraper.py"
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
    service_account_email = google_service_account.function_sa.email
  }

  depends_on = [google_project_service.apis]
}

output "function_uri" {
  value = google_cloudfunctions2_function.function.service_config[0].uri
}
