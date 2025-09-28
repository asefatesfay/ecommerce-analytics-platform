# Cloud Storage Configuration for DuckDB Analytics Platform
# Provides data storage, static assets, and backup storage

# Data bucket for DuckDB files and analytics data
resource "google_storage_bucket" "data_bucket" {
  name     = "${local.name_suffix}-data"
  location = var.region

  labels = local.common_labels

  # Storage class and lifecycle
  storage_class = var.storage_config.storage_class

  versioning {
    enabled = var.storage_config.versioning
  }

  # Lifecycle management
  dynamic "lifecycle_rule" {
    for_each = var.storage_config.lifecycle_rules ? [1] : []
    content {
      condition {
        age = var.storage_config.retention_days
      }
      action {
        type = "Delete"
      }
    }
  }

  # Security settings
  uniform_bucket_level_access = true

  # CORS settings for web access
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  # Encryption
  encryption {
    default_kms_key_name = google_kms_crypto_key.storage_key.id
  }
}

# Static assets bucket for frontend
resource "google_storage_bucket" "static_bucket" {
  name     = "${local.name_suffix}-static"
  location = var.region

  labels = local.common_labels

  storage_class = "STANDARD"

  # Public access for static assets
  uniform_bucket_level_access = false

  # Website configuration
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }

  # CORS for web assets
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type", "Cache-Control"]
    max_age_seconds = 86400
  }
}

# Backup bucket
resource "google_storage_bucket" "backup_bucket" {
  name     = "${local.name_suffix}-backup"
  location = var.region

  labels = local.common_labels

  storage_class = "NEARLINE"

  versioning {
    enabled = true
  }

  # Lifecycle for long-term retention
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  uniform_bucket_level_access = true

  encryption {
    default_kms_key_name = google_kms_crypto_key.storage_key.id
  }
}

# Logs bucket for application logs
resource "google_storage_bucket" "logs_bucket" {
  name     = "${local.name_suffix}-logs"
  location = var.region

  labels = local.common_labels

  storage_class = "STANDARD"

  # Lifecycle management for logs
  lifecycle_rule {
    condition {
      age = var.monitoring_config.log_retention_days
    }
    action {
      type = "Delete"
    }
  }

  uniform_bucket_level_access = true
}

# KMS key for bucket encryption
resource "google_kms_key_ring" "storage_keyring" {
  name     = "${local.name_suffix}-storage"
  location = var.region
}

resource "google_kms_crypto_key" "storage_key" {
  name     = "storage-encryption-key"
  key_ring = google_kms_key_ring.storage_keyring.id

  purpose = "ENCRYPT_DECRYPT"

  labels = local.common_labels

  lifecycle {
    prevent_destroy = true
  }
}

# IAM for static bucket public access (if enabled)
resource "google_storage_bucket_iam_member" "static_public" {
  count  = var.storage_config.public_read ? 1 : 0
  bucket = google_storage_bucket.static_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Cloud CDN for static assets
resource "google_compute_backend_bucket" "static_backend" {
  name        = "${local.name_suffix}-static-backend"
  bucket_name = google_storage_bucket.static_bucket.name

  enable_cdn = true

  cdn_policy {
    cache_mode       = "CACHE_ALL_STATIC"
    default_ttl      = 3600
    max_ttl          = 86400
    negative_caching = true

    negative_caching_policy {
      code = 404
      ttl  = 300
    }
  }
}

# Service account for storage access
resource "google_service_account" "storage_sa" {
  account_id   = "${local.name_suffix}-storage"
  display_name = "DuckDB Analytics Storage Service Account"
  description  = "Service account for Cloud Storage operations"
}

# IAM bindings for storage service account
resource "google_storage_bucket_iam_member" "data_bucket_access" {
  bucket = google_storage_bucket.data_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.storage_sa.email}"
}

resource "google_storage_bucket_iam_member" "backup_bucket_access" {
  bucket = google_storage_bucket.backup_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.storage_sa.email}"
}

resource "google_storage_bucket_iam_member" "logs_bucket_access" {
  bucket = google_storage_bucket.logs_bucket.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.storage_sa.email}"
}