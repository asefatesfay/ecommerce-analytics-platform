# GCP Terraform Configuration for DuckDB Analytics Platform
# Provides Cloud Run, Cloud Storage, and Monitoring infrastructure

terraform {
  required_version = ">= 1.13"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }

  # Backend configuration - comment out for local development
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket-gcp"
  #   prefix = "terraform/state"
  # }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Random suffix for unique naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# Data sources for project information
data "google_project" "current" {
  project_id = var.project_id
}

data "google_client_config" "current" {}

# Local values for resource naming
locals {
  name_suffix = "${var.project_name}-${var.environment}-${random_string.suffix.result}"

  common_labels = {
    environment = var.environment
    project     = var.project_name
    managed-by  = "terraform"
  }
}