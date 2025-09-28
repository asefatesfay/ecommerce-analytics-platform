# Cloud Run Configuration for DuckDB Analytics Platform
# Provides serverless container deployment for backend and frontend services

# Container Registry repositories
resource "google_artifact_registry_repository" "app_repo" {
  repository_id = "${local.name_suffix}-repo"
  location      = var.region
  format        = "DOCKER"
  description   = "Docker repository for DuckDB Analytics containers"

  labels = local.common_labels
}

# Backend Cloud Run service
resource "google_cloud_run_v2_service" "backend" {
  name     = "${local.name_suffix}-backend"
  location = var.region

  labels = local.common_labels

  template {
    # Environment-specific scaling
    scaling {
      min_instance_count = try(
        var.environment_configs[var.environment].auto_scaling.min_instances,
        var.auto_scaling.min_instances
      )

      max_instance_count = try(
        var.environment_configs[var.environment].auto_scaling.max_instances,
        var.auto_scaling.max_instances
      )
    }

    # Service account
    service_account = google_service_account.app_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app_repo.repository_id}/backend:latest"

      # Resource configuration
      resources {
        limits = {
          cpu = try(
            var.environment_configs[var.environment].cloud_run_config.backend.cpu,
            var.cloud_run_config.backend.cpu
          )

          memory = try(
            var.environment_configs[var.environment].cloud_run_config.backend.memory,
            var.cloud_run_config.backend.memory
          )
        }

        cpu_idle          = true
        startup_cpu_boost = var.environment == "prod"
      }

      # Environment variables
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "DATA_BUCKET"
        value = google_storage_bucket.data_bucket.name
      }

      env {
        name  = "BACKUP_BUCKET"
        value = google_storage_bucket.backup_bucket.name
      }

      # Health check configuration
      ports {
        container_port = 8000
        name           = "http1"
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3
      }

      # Volume mounts for temporary data
      volume_mounts {
        name       = "tmp"
        mount_path = "/tmp"
      }
    }

    # Volumes
    volumes {
      name = "tmp"
      empty_dir {
        medium     = "MEMORY"
        size_limit = "1Gi"
      }
    }

    # Timeout and concurrency
    timeout                          = "${var.auto_scaling.request_timeout}s"
    max_instance_request_concurrency = var.auto_scaling.concurrency

    # VPC access (if configured)
    dynamic "vpc_access" {
      for_each = var.vpc_config.create_vpc ? [1] : []
      content {
        connector = google_vpc_access_connector.connector[0].id
        egress    = "ALL_TRAFFIC"
      }
    }

    # Annotations for auto scaling
    annotations = {
      "autoscaling.knative.dev/minScale"         = tostring(var.auto_scaling.min_instances)
      "autoscaling.knative.dev/maxScale"         = tostring(var.auto_scaling.max_instances)
      "run.googleapis.com/cpu-throttling"        = "false"
      "run.googleapis.com/execution-environment" = "gen2"
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [
    google_project_service.required_apis

  ]
}

# Frontend Cloud Run service
resource "google_cloud_run_v2_service" "frontend" {
  name     = "${local.name_suffix}-frontend"
  location = var.region

  labels = local.common_labels

  template {
    scaling {
      min_instance_count = try(
        var.environment_configs[var.environment].auto_scaling.min_instances,
        var.auto_scaling.min_instances
      )

      max_instance_count = try(
        var.environment_configs[var.environment].auto_scaling.max_instances,
        var.auto_scaling.max_instances
      )
    }

    service_account = google_service_account.app_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app_repo.repository_id}/frontend:latest"

      resources {
        limits = {
          cpu    = var.cloud_run_config.frontend.cpu
          memory = var.cloud_run_config.frontend.memory
        }

        cpu_idle = true
      }

      # Environment variables
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.backend.uri
      }

      env {
        name  = "NEXT_PUBLIC_ENVIRONMENT"
        value = var.environment
      }

      ports {
        container_port = 3000
        name           = "http1"
      }

      startup_probe {
        http_get {
          path = "/"
          port = 3000
        }
        initial_delay_seconds = 5
        timeout_seconds       = 3
        period_seconds        = 5
        failure_threshold     = 3
      }
    }

    timeout                          = "300s"
    max_instance_request_concurrency = var.auto_scaling.concurrency

    annotations = {
      "autoscaling.knative.dev/minScale"         = tostring(var.auto_scaling.min_instances)
      "autoscaling.knative.dev/maxScale"         = tostring(var.auto_scaling.max_instances)
      "run.googleapis.com/execution-environment" = "gen2"
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [
    google_project_service.required_apis

  ]
}

# IAM policy for Cloud Run services (public access)
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  name     = google_cloud_run_v2_service.frontend.name
  location = google_cloud_run_v2_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Custom domain mapping (optional)
resource "google_cloud_run_domain_mapping" "backend_domain" {
  count    = var.environment == "prod" ? 1 : 0
  name     = "api.${var.project_name}.com"
  location = var.region

  metadata {
    namespace = var.project_id
    labels    = local.common_labels
  }

  spec {
    route_name = google_cloud_run_v2_service.backend.name
  }
}

resource "google_cloud_run_domain_mapping" "frontend_domain" {
  count    = var.environment == "prod" ? 1 : 0
  name     = "${var.project_name}.com"
  location = var.region

  metadata {
    namespace = var.project_id
    labels    = local.common_labels
  }

  spec {
    route_name = google_cloud_run_v2_service.frontend.name
  }
}