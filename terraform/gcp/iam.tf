# IAM Configuration for DuckDB Analytics Platform
# Provides service accounts and IAM policies for secure operations

# Service account for Cloud Run applications
resource "google_service_account" "app_sa" {
  account_id   = "${local.name_suffix}-app"
  display_name = "DuckDB Analytics Application Service Account"
  description  = "Service account for Cloud Run applications"
}

# Service account for monitoring and logging
resource "google_service_account" "monitoring_sa" {
  account_id   = "${local.name_suffix}-monitoring"
  display_name = "DuckDB Analytics Monitoring Service Account"
  description  = "Service account for monitoring and logging operations"
}

# Service account for CI/CD pipeline
resource "google_service_account" "cicd_sa" {
  account_id   = "${local.name_suffix}-cicd"
  display_name = "DuckDB Analytics CI/CD Service Account"
  description  = "Service account for CI/CD operations"
}

# IAM roles for application service account

# Cloud Storage permissions
resource "google_project_iam_member" "app_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Cloud Logging permissions
resource "google_project_iam_member" "app_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Cloud Monitoring permissions
resource "google_project_iam_member" "app_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Cloud Trace permissions
resource "google_project_iam_member" "app_trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Cloud Error Reporting permissions
resource "google_project_iam_member" "app_error_writer" {
  project = var.project_id
  role    = "roles/errorreporting.writer"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# KMS permissions for encryption
resource "google_project_iam_member" "app_kms_decrypt" {
  project = var.project_id
  role    = "roles/cloudkms.cryptoKeyDecrypter"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

resource "google_project_iam_member" "app_kms_encrypt" {
  project = var.project_id
  role    = "roles/cloudkms.cryptoKeyEncrypter"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# IAM roles for monitoring service account
resource "google_project_iam_member" "monitoring_admin" {
  project = var.project_id
  role    = "roles/monitoring.admin"
  member  = "serviceAccount:${google_service_account.monitoring_sa.email}"
}

resource "google_project_iam_member" "logging_admin" {
  project = var.project_id
  role    = "roles/logging.admin"
  member  = "serviceAccount:${google_service_account.monitoring_sa.email}"
}

# IAM roles for CI/CD service account

# Cloud Run permissions
resource "google_project_iam_member" "cicd_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cicd_sa.email}"
}

# Artifact Registry permissions
resource "google_project_iam_member" "cicd_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.cicd_sa.email}"
}

# Cloud Build permissions
resource "google_project_iam_member" "cicd_build_editor" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.editor"
  member  = "serviceAccount:${google_service_account.cicd_sa.email}"
}

# Service account user permission for deploying
resource "google_project_iam_member" "cicd_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cicd_sa.email}"
}

# Storage admin for CI/CD artifacts
resource "google_project_iam_member" "cicd_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.cicd_sa.email}"
}

# IAM policy for cross-service communication
resource "google_project_iam_member" "app_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Custom IAM role for DuckDB operations
resource "google_project_iam_custom_role" "duckdb_operator" {
  role_id     = replace("${local.name_suffix}_duckdb_operator", "-", "_")
  title       = "DuckDB Analytics Operator"
  description = "Custom role for DuckDB Analytics operations"

  permissions = [
    "storage.objects.create",
    "storage.objects.delete",
    "storage.objects.get",
    "storage.objects.list",
    "storage.objects.update",
    "storage.buckets.get",
    "logging.logEntries.create",
    "monitoring.metricDescriptors.create",
    "monitoring.metricDescriptors.get",
    "monitoring.metricDescriptors.list",
    "monitoring.monitoredResourceDescriptors.get",
    "monitoring.monitoredResourceDescriptors.list",
    "monitoring.timeSeries.create",
  ]
}

# Assign custom role to application service account
resource "google_project_iam_member" "app_custom_role" {
  project = var.project_id
  role    = google_project_iam_custom_role.duckdb_operator.id
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# Workload Identity for GKE (if needed in future)
resource "google_service_account_iam_member" "workload_identity" {
  count              = var.environment == "prod" ? 1 : 0
  service_account_id = google_service_account.app_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[default/duckdb-analytics]"
}

# Service account keys for external access (use with caution)
resource "google_service_account_key" "cicd_key" {
  count              = var.environment == "dev" ? 1 : 0
  service_account_id = google_service_account.cicd_sa.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# IAM conditions for environment-specific access
resource "google_project_iam_member" "app_conditional_access" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.app_sa.email}"

  condition {
    title       = "Environment Specific Access"
    description = "Allow access only to environment-specific resources"
    expression  = "resource.name.startsWith('projects/${var.project_id}/buckets/${local.name_suffix}')"
  }
}