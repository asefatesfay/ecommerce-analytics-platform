# Networking Configuration for DuckDB Analytics Platform
# Provides VPC, subnets, and connectivity for Cloud Run services

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudkms.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
  ])

  project = var.project_id
  service = each.key

  disable_dependent_services = false
  disable_on_destroy         = false
}

# VPC Network (conditional creation)
resource "google_compute_network" "vpc" {
  count = var.vpc_config.create_vpc ? 1 : 0

  name                    = "${local.name_suffix}-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460

  description = "VPC network for DuckDB Analytics Platform"
}

# Subnet for Cloud Run VPC connector
resource "google_compute_subnetwork" "subnet" {
  count = var.vpc_config.create_vpc ? 1 : 0

  name          = "${local.name_suffix}-subnet"
  ip_cidr_range = var.vpc_config.subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc[0].id

  description = "Subnet for Cloud Run services"

  # Private Google Access for Cloud APIs
  private_ip_google_access = var.vpc_config.enable_private_ip

  # Secondary ranges for future use (GKE, etc.)
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/16"
  }

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# VPC Access Connector for Cloud Run
resource "google_vpc_access_connector" "connector" {
  count = var.vpc_config.create_vpc ? 1 : 0

  name          = "${local.name_suffix}-connector"
  region        = var.region
  network       = google_compute_network.vpc[0].name
  ip_cidr_range = "10.8.0.0/28"

  min_throughput = 200
  max_throughput = var.environment == "prod" ? 1000 : 300

  depends_on = [
    google_project_service.required_apis
  ]
}

# Cloud Router for NAT
resource "google_compute_router" "router" {
  count = var.vpc_config.create_vpc ? 1 : 0

  name    = "${local.name_suffix}-router"
  region  = var.region
  network = google_compute_network.vpc[0].id

  description = "Cloud Router for NAT Gateway"
}

# Cloud NAT for outbound internet access
resource "google_compute_router_nat" "nat" {
  count = var.vpc_config.create_vpc ? 1 : 0

  name                               = "${local.name_suffix}-nat"
  router                             = google_compute_router.router[0].name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall rules for VPC
resource "google_compute_firewall" "allow_internal" {
  count = var.vpc_config.create_vpc ? 1 : 0

  name    = "${local.name_suffix}-allow-internal"
  network = google_compute_network.vpc[0].name

  description = "Allow internal communication within VPC"

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [var.vpc_config.subnet_cidr]
  target_tags   = ["duckdb-analytics"]
}

resource "google_compute_firewall" "allow_health_checks" {
  count = var.vpc_config.create_vpc ? 1 : 0

  name    = "${local.name_suffix}-allow-health-checks"
  network = google_compute_network.vpc[0].name

  description = "Allow health checks from Google Cloud"

  allow {
    protocol = "tcp"
    ports    = ["8000", "3000"]
  }

  # Google Cloud health check ranges
  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16"
  ]

  target_tags = ["duckdb-analytics"]
}

resource "google_compute_firewall" "allow_ssh" {
  count = var.vpc_config.create_vpc && var.environment != "prod" ? 1 : 0

  name    = "${local.name_suffix}-allow-ssh"
  network = google_compute_network.vpc[0].name

  description = "Allow SSH for debugging (non-prod only)"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["duckdb-analytics-debug"]
}

# Global load balancer (for custom domains)
resource "google_compute_global_address" "lb_ip" {
  count = var.environment == "prod" ? 1 : 0
  name  = "${local.name_suffix}-lb-ip"

  description = "Static IP for load balancer"
}

resource "google_compute_managed_ssl_certificate" "ssl_cert" {
  count = var.environment == "prod" ? 1 : 0
  name  = "${local.name_suffix}-ssl-cert"

  managed {
    domains = [
      "${var.project_name}.com",
      "api.${var.project_name}.com"
    ]
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Network Endpoint Group for Cloud Run services
resource "google_compute_region_network_endpoint_group" "backend_neg" {
  count = var.environment == "prod" ? 1 : 0

  name                  = "${local.name_suffix}-backend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = google_cloud_run_v2_service.backend.name
  }
}

resource "google_compute_region_network_endpoint_group" "frontend_neg" {
  count = var.environment == "prod" ? 1 : 0

  name                  = "${local.name_suffix}-frontend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = google_cloud_run_v2_service.frontend.name
  }
}

# Private Service Connection for future database integration
resource "google_compute_global_address" "private_ip_range" {
  count = var.vpc_config.enable_cloud_sql_access ? 1 : 0

  name          = "${local.name_suffix}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc[0].id
}

resource "google_service_networking_connection" "private_service_connection" {
  count = var.vpc_config.enable_cloud_sql_access ? 1 : 0

  network                 = google_compute_network.vpc[0].id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range[0].name]

  depends_on = [
    google_project_service.required_apis
  ]
}

# DNS Zone for custom domain (production only)
resource "google_dns_managed_zone" "main" {
  count = var.environment == "prod" ? 1 : 0

  name        = "${local.name_suffix}-zone"
  dns_name    = "${var.project_name}.com."
  description = "DNS zone for DuckDB Analytics Platform"

  labels = local.common_labels
}

# DNS records
resource "google_dns_record_set" "a_record" {
  count = var.environment == "prod" ? 1 : 0

  name         = google_dns_managed_zone.main[0].dns_name
  managed_zone = google_dns_managed_zone.main[0].name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_address.lb_ip[0].address]
}

resource "google_dns_record_set" "api_record" {
  count = var.environment == "prod" ? 1 : 0

  name         = "api.${google_dns_managed_zone.main[0].dns_name}"
  managed_zone = google_dns_managed_zone.main[0].name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_address.lb_ip[0].address]
}