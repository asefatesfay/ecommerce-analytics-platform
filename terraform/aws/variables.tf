# Input Variables
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "duckdb-analytics"
}

variable "project_owner" {
  description = "Project owner/team"
  type        = string
  default     = "DevOps Team"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "container_cpu" {
  description = "CPU units for containers (1024 = 1 vCPU)"
  type = object({
    backend  = number
    frontend = number
  })
  default = {
    backend  = 512
    frontend = 256
  }
}

variable "container_memory" {
  description = "Memory for containers in MB"
  type = object({
    backend  = number
    frontend = number
  })
  default = {
    backend  = 1024
    frontend = 512
  }
}

variable "auto_scaling" {
  description = "Auto scaling configuration"
  type = object({
    min_capacity = number
    max_capacity = number
    target_cpu   = number
  })
  default = {
    min_capacity = 1
    max_capacity = 10
    target_cpu   = 70
  }
}

variable "domain_name" {
  description = "Domain name for the application (optional)"
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS (optional)"
  type        = string
  default     = ""
}

variable "enable_logging" {
  description = "Enable CloudWatch logging"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

variable "backup_retention_days" {
  description = "S3 data backup retention in days"
  type        = number
  default     = 30
}