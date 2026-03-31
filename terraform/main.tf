terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0.0"
    }
  }

  backend "gcs" {
    bucket = "tf-state-zaragoza-pools"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
}

variable "region" {
  description = "The region to deploy resources to"
  type        = string
  default     = "europe-west1"
}

# Enable necessary APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "firestore.googleapis.com",
    "cloudscheduler.googleapis.com",
    "cloudbuild.googleapis.com",       # Required for Gen 2 functions
    "artifactregistry.googleapis.com", # Required for Gen 2 functions
    "run.googleapis.com"               # Required for Gen 2 functions
  ])

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}
