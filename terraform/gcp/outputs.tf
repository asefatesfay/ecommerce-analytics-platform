# Outputs for DuckDB Analytics Platform GCP Infrastructure

# Service URLs
output "backend_url" {
  description = "URL of the backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend.uri
  sensitive   = false
}

output "frontend_url" {
  description = "URL of the frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend.uri
  sensitive   = false
}

# Custom domain URLs (production only)
output "production_backend_url" {
  description = "Production backend URL with custom domain"
  value       = var.environment == "prod" ? "https://api.${var.project_name}.com" : null
}

output "production_frontend_url" {
  description = "Production frontend URL with custom domain"
  value       = var.environment == "prod" ? "https://${var.project_name}.com" : null
}

# Storage information
output "data_bucket_name" {
  description = "Name of the data storage bucket"
  value       = google_storage_bucket.data_bucket.name
}

output "data_bucket_url" {
  description = "URL of the data storage bucket"
  value       = google_storage_bucket.data_bucket.url
}

output "static_bucket_name" {
  description = "Name of the static assets bucket"
  value       = google_storage_bucket.static_bucket.name
}

output "static_bucket_url" {
  description = "URL of the static assets bucket"
  value       = google_storage_bucket.static_bucket.url
}

output "backup_bucket_name" {
  description = "Name of the backup bucket"
  value       = google_storage_bucket.backup_bucket.name
}

output "logs_bucket_name" {
  description = "Name of the logs bucket"
  value       = google_storage_bucket.logs_bucket.name
}

# Container Registry information
output "artifact_registry_repository" {
  description = "Artifact Registry repository URL"
  value       = data.google_artifact_registry_repository.app_repo.name
}

output "docker_registry_url" {
  description = "Docker registry URL for pushing images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${data.google_artifact_registry_repository.app_repo.repository_id}"
}

# Service Account information
output "app_service_account_email" {
  description = "Email of the application service account"
  value       = google_service_account.app_sa.email
}

output "cicd_service_account_email" {
  description = "Email of the CI/CD service account"
  value       = google_service_account.cicd_sa.email
}

output "monitoring_service_account_email" {
  description = "Email of the monitoring service account"
  value       = google_service_account.monitoring_sa.email
}

# Network information
output "vpc_network_name" {
  description = "Name of the VPC network"
  value       = var.vpc_config.create_vpc ? google_compute_network.vpc[0].name : null
}

output "vpc_network_id" {
  description = "ID of the VPC network"
  value       = var.vpc_config.create_vpc ? google_compute_network.vpc[0].id : null
}

output "subnet_name" {
  description = "Name of the subnet"
  value       = var.vpc_config.create_vpc ? google_compute_subnetwork.subnet[0].name : null
}

output "vpc_connector_name" {
  description = "Name of the VPC Access Connector"
  value       = var.vpc_config.create_vpc ? google_vpc_access_connector.connector[0].name : null
}

# Load balancer information (production only)
output "load_balancer_ip" {
  description = "Static IP address of the load balancer"
  value       = var.environment == "prod" ? google_compute_global_address.lb_ip[0].address : null
}

output "ssl_certificate_id" {
  description = "ID of the managed SSL certificate"
  value       = var.environment == "prod" ? google_compute_managed_ssl_certificate.ssl_cert[0].id : null
}

# DNS information (production only)
output "dns_zone_name" {
  description = "Name of the DNS managed zone"
  value       = var.environment == "prod" ? google_dns_managed_zone.main[0].name : null
}

output "dns_name_servers" {
  description = "Name servers for the DNS zone"
  value       = var.environment == "prod" ? google_dns_managed_zone.main[0].name_servers : null
}

# Monitoring information
output "dashboard_url" {
  description = "URL of the Cloud Monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.main_dashboard.id}?project=${var.project_id}"
}

output "log_sink_writer_identity" {
  description = "Writer identity for the log sink"
  value       = google_logging_project_sink.app_logs.writer_identity
}

# KMS information
output "storage_kms_key_id" {
  description = "ID of the storage encryption key"
  value       = google_kms_crypto_key.storage_key.id
}

output "kms_keyring_id" {
  description = "ID of the KMS key ring"
  value       = google_kms_key_ring.storage_keyring.id
}

# Environment and project information
output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "resource_suffix" {
  description = "Resource naming suffix"
  value       = random_string.suffix.result
}

# CI/CD Service Account Key (development only)
output "cicd_service_account_key" {
  description = "Base64 encoded service account key for CI/CD (dev environment only)"
  value       = var.environment == "dev" ? google_service_account_key.cicd_key[0].private_key : null
  sensitive   = true
}

# Health check URLs
output "backend_health_check_url" {
  description = "Backend health check URL"
  value       = "${google_cloud_run_v2_service.backend.uri}/health"
}

output "frontend_health_check_url" {
  description = "Frontend health check URL"
  value       = google_cloud_run_v2_service.frontend.uri
}

# Deployment information
output "deployment_timestamp" {
  description = "Timestamp of the deployment"
  value       = timestamp()
}

output "terraform_workspace" {
  description = "Terraform workspace used for deployment"
  value       = terraform.workspace
}

# Summary information
output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    environment        = var.environment
    region             = var.region
    backend_service    = google_cloud_run_v2_service.backend.name
    frontend_service   = google_cloud_run_v2_service.frontend.name
    data_bucket        = google_storage_bucket.data_bucket.name
    monitoring_enabled = var.monitoring_config.enable_cloud_monitoring
    vpc_enabled        = var.vpc_config.create_vpc
    custom_domain      = var.environment == "prod"
  }
}