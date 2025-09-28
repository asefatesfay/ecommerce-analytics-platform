# GCP Variables Configuration

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "duckdb-analytics"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone for zonal resources"
  type        = string
  default     = "us-central1-a"
}

variable "artifact_registry_repo_id" {
  description = "Artifact Registry repository ID (must be pre-created)"
  type        = string
  default     = "duckdb-repo"
}

# Cloud Run configuration
variable "cloud_run_config" {
  description = "Configuration for Cloud Run services"
  type = object({
    backend = object({
      cpu    = string
      memory = string
    })
    frontend = object({
      cpu    = string
      memory = string
    })
  })
  default = {
    backend = {
      cpu    = "1"
      memory = "2Gi"
    }
    frontend = {
      cpu    = "1"
      memory = "1Gi"
    }
  }
}

# Auto scaling configuration
variable "auto_scaling" {
  description = "Auto scaling configuration"
  type = object({
    min_instances   = number
    max_instances   = number
    concurrency     = number
    cpu_utilization = number
    request_timeout = number
  })
  default = {
    min_instances   = 0
    max_instances   = 10
    concurrency     = 80
    cpu_utilization = 60
    request_timeout = 300
  }
}

# Networking configuration
variable "vpc_config" {
  description = "VPC configuration"
  type = object({
    create_vpc              = bool
    vpc_name                = string
    subnet_cidr             = string
    enable_private_ip       = bool
    enable_cloud_sql_access = bool
  })
  default = {
    create_vpc              = true
    vpc_name                = "duckdb-vpc"
    subnet_cidr             = "10.0.0.0/24"
    enable_private_ip       = true
    enable_cloud_sql_access = false
  }
}

# Storage configuration
variable "storage_config" {
  description = "Cloud Storage configuration"
  type = object({
    storage_class   = string
    versioning      = bool
    lifecycle_rules = bool
    retention_days  = number
    public_read     = bool
  })
  default = {
    storage_class   = "STANDARD"
    versioning      = true
    lifecycle_rules = true
    retention_days  = 90
    public_read     = false
  }
}

# Monitoring configuration
variable "monitoring_config" {
  description = "Monitoring and logging configuration"
  type = object({
    enable_cloud_monitoring = bool
    enable_cloud_logging    = bool
    log_retention_days      = number
    enable_alerting         = bool
    notification_channels   = list(string)
  })
  default = {
    enable_cloud_monitoring = true
    enable_cloud_logging    = true
    log_retention_days      = 30
    enable_alerting         = true
    notification_channels   = []
  }
}

# Security configuration
variable "security_config" {
  description = "Security configuration"
  type = object({
    enable_binary_authorization = bool
    enable_vulnerability_scan   = bool
    allowed_ingress_cidrs       = list(string)
    enable_https_redirect       = bool
  })
  default = {
    enable_binary_authorization = false
    enable_vulnerability_scan   = true
    allowed_ingress_cidrs       = ["0.0.0.0/0"]
    enable_https_redirect       = true
  }
}

# Database configuration (for potential Cloud SQL integration)
variable "database_config" {
  description = "Cloud SQL configuration (optional)"
  type = object({
    enabled                = bool
    tier                   = string
    disk_size              = number
    disk_type              = string
    backup_enabled         = bool
    point_in_time_recovery = bool
  })
  default = {
    enabled                = false
    tier                   = "db-f1-micro"
    disk_size              = 20
    disk_type              = "PD_SSD"
    backup_enabled         = true
    point_in_time_recovery = true
  }
}

# Environment-specific overrides
variable "environment_configs" {
  description = "Environment-specific configuration overrides"
  type = map(object({
    auto_scaling = optional(object({
      min_instances   = number
      max_instances   = number
      concurrency     = number
      cpu_utilization = number
    }))
    cloud_run_config = optional(object({
      backend = object({
        cpu    = string
        memory = string
      })
      frontend = object({
        cpu    = string
        memory = string
      })
    }))
    monitoring_config = optional(object({
      log_retention_days = number
    }))
  }))
  default = {
    dev = {
      auto_scaling = {
        min_instances   = 0
        max_instances   = 3
        concurrency     = 80
        cpu_utilization = 70
      }
      monitoring_config = {
        log_retention_days = 7
      }
    }
    staging = {
      auto_scaling = {
        min_instances   = 1
        max_instances   = 5
        concurrency     = 80
        cpu_utilization = 65
      }
      monitoring_config = {
        log_retention_days = 14
      }
    }
    prod = {
      auto_scaling = {
        min_instances   = 2
        max_instances   = 20
        concurrency     = 100
        cpu_utilization = 60
      }
      cloud_run_config = {
        backend = {
          cpu    = "2"
          memory = "4Gi"
        }
        frontend = {
          cpu    = "1"
          memory = "2Gi"
        }
      }
      monitoring_config = {
        log_retention_days = 90
      }
    }
  }
}