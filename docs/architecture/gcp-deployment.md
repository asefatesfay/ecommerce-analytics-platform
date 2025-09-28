# Google Cloud Platform (GCP) Deployment Guide

This guide covers deploying the DuckDB E-commerce Analytics application to Google Cloud Platform (GCP).

## 🏗️ GCP Architecture Overview

The GCP deployment uses the following services:
- **Cloud Run:** Fully managed serverless containers
- **Cloud Load Balancing:** Global load balancer with SSL termination
- **Cloud DNS:** Managed DNS service
- **Cloud CDN:** Global content delivery network
- **Cloud Storage:** Object storage for data files
- **BigQuery:** Serverless data warehouse (DuckDB alternative for cloud scale)
- **Cloud Monitoring:** Observability and alerting
- **Cloud IAM:** Identity and access management

## 📋 Prerequisites

### 1. Google Cloud SDK Setup
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Set project and region
gcloud config set project YOUR_PROJECT_ID
gcloud config set run/region us-central1
```

### 2. Enable Required APIs
```bash
# Enable necessary GCP APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable dns.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### 3. Setup Artifact Registry
```bash
# Create Artifact Registry repository
gcloud artifacts repositories create duckdb-analytics \
  --repository-format=docker \
  --location=us-central1 \
  --description="DuckDB Analytics containers"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 4. Create Cloud Storage Bucket
```bash
# Create bucket for data storage
gsutil mb -l us-central1 gs://duckdb-analytics-data-$(gcloud config get-value project)

# Upload sample data
gsutil -m cp -r data/ gs://duckdb-analytics-data-$(gcloud config get-value project)/data/
```

## 🚀 Deployment Steps

### 1. Build and Push Container Images

```bash
# Navigate to project root
cd /path/to/duckdb-project

# Build and push backend image
gcloud builds submit ./backend \
  --tag us-central1-docker.pkg.dev/$(gcloud config get-value project)/duckdb-analytics/backend

# Build and push frontend image  
gcloud builds submit ./frontend \
  --tag us-central1-docker.pkg.dev/$(gcloud config get-value project)/duckdb-analytics/frontend
```

### 2. Deploy Backend to Cloud Run

```bash
# Deploy backend service
gcloud run deploy duckdb-backend \
  --image us-central1-docker.pkg.dev/$(gcloud config get-value project)/duckdb-analytics/backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="GCS_BUCKET=duckdb-analytics-data-$(gcloud config get-value project)" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)"
```

### 3. Deploy Frontend to Cloud Run

```bash
# Get backend service URL
BACKEND_URL=$(gcloud run services describe duckdb-backend --region=us-central1 --format='value(status.url)')

# Deploy frontend service
gcloud run deploy duckdb-frontend \
  --image us-central1-docker.pkg.dev/$(gcloud config get-value project)/duckdb-analytics/frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars="API_URL=${BACKEND_URL}"
```

### 4. Setup Load Balancer and SSL

**Create backend service:**
```bash
# Create backend service for Cloud Run
gcloud compute backend-services create duckdb-backend-service \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED

gcloud compute backend-services create duckdb-frontend-service \
  --global \
  --load-balancing-scheme=EXTERNAL_MANAGED
```

**Create NEG (Network Endpoint Groups):**
```bash
# Create serverless NEG for backend
gcloud compute network-endpoint-groups create duckdb-backend-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=duckdb-backend

# Create serverless NEG for frontend
gcloud compute network-endpoint-groups create duckdb-frontend-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=duckdb-frontend
```

**Add NEGs to backend services:**
```bash
# Add NEGs as backends
gcloud compute backend-services add-backend duckdb-backend-service \
  --global \
  --network-endpoint-group=duckdb-backend-neg \
  --network-endpoint-group-region=us-central1

gcloud compute backend-services add-backend duckdb-frontend-service \
  --global \
  --network-endpoint-group=duckdb-frontend-neg \
  --network-endpoint-group-region=us-central1
```

**Create URL map and load balancer:**
```bash
# Create URL map
gcloud compute url-maps create duckdb-loadbalancer \
  --default-service=duckdb-frontend-service

# Add path matcher for API
gcloud compute url-maps add-path-matcher duckdb-loadbalancer \
  --path-matcher-name=api-matcher \
  --default-service=duckdb-frontend-service \
  --path-rules="/api/*=duckdb-backend-service"

# Create SSL certificate
gcloud compute ssl-certificates create duckdb-ssl-cert \
  --domains=your-domain.com

# Create HTTPS proxy
gcloud compute target-https-proxies create duckdb-https-proxy \
  --ssl-certificates=duckdb-ssl-cert \
  --url-map=duckdb-loadbalancer

# Create global forwarding rule
gcloud compute forwarding-rules create duckdb-https-rule \
  --global \
  --target-https-proxy=duckdb-https-proxy \
  --ports=443
```

## 🔧 Infrastructure as Code

### Terraform Configuration

Create `gcp-infrastructure/main.tf`:

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Storage bucket for data
resource "google_storage_bucket" "data_bucket" {
  name          = "duckdb-analytics-data-${var.project_id}"
  location      = var.region
  force_destroy = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}

# BigQuery dataset for analytics
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "duckdb_analytics"
  location   = var.region
  
  description = "DuckDB Analytics Dataset"
}

# Cloud Run service for backend
resource "google_cloud_run_service" "backend" {
  name     = "duckdb-backend"
  location = var.region
  
  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/duckdb-analytics/backend"
        
        ports {
          container_port = 8000
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
        
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.data_bucket.name
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
      }
      
      container_concurrency = 100
      timeout_seconds      = 300
      
      service_account_name = google_service_account.cloud_run.email
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Cloud Run service for frontend
resource "google_cloud_run_service" "frontend" {
  name     = "duckdb-frontend"
  location = var.region
  
  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/duckdb-analytics/frontend"
        
        ports {
          container_port = 3000
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
        
        env {
          name  = "API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }
      }
      
      container_concurrency = 100
      timeout_seconds      = 300
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "5"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Service account for Cloud Run
resource "google_service_account" "cloud_run" {
  account_id   = "duckdb-cloud-run"
  display_name = "DuckDB Cloud Run Service Account"
}

# IAM bindings for Cloud Run service account
resource "google_storage_bucket_iam_member" "cloud_run_storage" {
  bucket = google_storage_bucket.data_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_bigquery_dataset_iam_member" "cloud_run_bigquery" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Load Balancer
resource "google_compute_global_address" "default" {
  name = "duckdb-lb-ip"
}

resource "google_compute_managed_ssl_certificate" "default" {
  name = "duckdb-ssl-cert"
  
  managed {
    domains = [var.domain_name]
  }
}

resource "google_compute_url_map" "default" {
  name            = "duckdb-url-map"
  default_service = google_compute_backend_service.frontend.id
  
  host_rule {
    hosts        = [var.domain_name]
    path_matcher = "allpaths"
  }
  
  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.frontend.id
    
    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.backend.id
    }
  }
}

# Backend services
resource "google_compute_backend_service" "backend" {
  name                  = "duckdb-backend-service"
  protocol              = "HTTP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  backend {
    group = google_compute_region_network_endpoint_group.backend.id
  }
}

resource "google_compute_backend_service" "frontend" {
  name                  = "duckdb-frontend-service"
  protocol              = "HTTP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  backend {
    group = google_compute_region_network_endpoint_group.frontend.id
  }
}

# Network Endpoint Groups for Cloud Run
resource "google_compute_region_network_endpoint_group" "backend" {
  name                  = "duckdb-backend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  
  cloud_run {
    service = google_cloud_run_service.backend.name
  }
}

resource "google_compute_region_network_endpoint_group" "frontend" {
  name                  = "duckdb-frontend-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  
  cloud_run {
    service = google_cloud_run_service.frontend.name
  }
}

# HTTPS proxy
resource "google_compute_target_https_proxy" "default" {
  name             = "duckdb-https-proxy"
  url_map          = google_compute_url_map.default.id
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}

# Global forwarding rule
resource "google_compute_global_forwarding_rule" "default" {
  name       = "duckdb-https-rule"
  target     = google_compute_target_https_proxy.default.id
  port_range = "443"
  ip_address = google_compute_global_address.default.address
}

# Cloud CDN
resource "google_compute_backend_service" "frontend_cdn" {
  name                  = "duckdb-frontend-cdn"
  protocol              = "HTTP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  
  enable_cdn = true
  
  cdn_policy {
    cache_mode       = "CACHE_ALL_STATIC"
    default_ttl      = 3600
    client_ttl       = 3600
    max_ttl          = 86400
    negative_caching = true
    
    cache_key_policy {
      include_host         = true
      include_protocol     = true
      include_query_string = false
    }
  }
  
  backend {
    group = google_compute_region_network_endpoint_group.frontend.id
  }
}
```

### Deploy with Terraform

```bash
# Initialize Terraform
cd gcp-infrastructure
terraform init

# Create terraform.tfvars
cat > terraform.tfvars << EOF
project_id  = "your-project-id"
region      = "us-central1"
domain_name = "your-domain.com"
EOF

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

## 📊 Monitoring and Observability

### Cloud Monitoring Setup

```bash
# Create monitoring workspace (if not exists)
gcloud alpha monitoring workspaces create

# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

### Sample Monitoring Dashboard (monitoring-dashboard.json):
```json
{
  "displayName": "DuckDB Analytics Dashboard",
  "mosaicLayout": {
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run Request Count",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_RATE"
                    }
                  }
                }
              }
            ],
            "yAxis": {
              "label": "Requests/sec"
            }
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run Response Latency",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_PERCENTILE_95"
                    }
                  }
                }
              }
            ],
            "yAxis": {
              "label": "Latency (ms)"
            }
          }
        }
      }
    ]
  }
}
```

### Set up Alerting

```bash
# Create notification channel
gcloud alpha monitoring channels create \
  --display-name="Email Notifications" \
  --type=email \
  --channel-labels=email_address=your-email@domain.com

# Create alert policy
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

### Sample Alert Policy (alert-policy.yaml):
```yaml
displayName: "High Error Rate Alert"
conditions:
- displayName: "Cloud Run Error Rate > 5%"
  conditionThreshold:
    filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'
    comparison: COMPARISON_GREATER_THAN
    thresholdValue: 0.05
    duration: 300s
    aggregations:
    - alignmentPeriod: 60s
      perSeriesAligner: ALIGN_RATE
      crossSeriesReducer: REDUCE_SUM
combiner: OR
enabled: true
notificationChannels:
- "projects/YOUR_PROJECT_ID/notificationChannels/YOUR_CHANNEL_ID"
```

## 🛡️ Security Configuration

### Cloud IAM Setup

**Create custom roles:**
```bash
# Create DuckDB Analytics role
gcloud iam roles create duckdbAnalyticsRole \
  --project=$(gcloud config get-value project) \
  --title="DuckDB Analytics Role" \
  --description="Role for DuckDB Analytics services" \
  --permissions="storage.objects.get,storage.objects.create,storage.objects.delete,bigquery.tables.get,bigquery.tables.create,bigquery.jobs.create"
```

**Service account security:**
```bash
# Create service account for Cloud Run
gcloud iam service-accounts create duckdb-cloud-run \
  --display-name="DuckDB Cloud Run Service Account"

# Assign minimal required permissions
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:duckdb-cloud-run@$(gcloud config get-value project).iam.gserviceaccount.com" \
  --role="projects/$(gcloud config get-value project)/roles/duckdbAnalyticsRole"
```

### Cloud Armor Security

```bash
# Create security policy
gcloud compute security-policies create duckdb-security-policy \
  --description="Security policy for DuckDB Analytics"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy=duckdb-security-policy \
  --expression="true" \
  --action=rate-based-ban \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --ban-duration-sec=600

# Apply to backend service
gcloud compute backend-services update duckdb-backend-service \
  --global \
  --security-policy=duckdb-security-policy
```

## 💰 Cost Optimization

### Strategies
1. **Cloud Run Scaling:** Automatic scale-to-zero saves costs during low usage
2. **BigQuery Slots:** Use on-demand pricing for variable workloads
3. **Cloud Storage Classes:** Use Nearline/Coldline for archival data
4. **Sustained Use Discounts:** Automatic discounts for long-running workloads
5. **Committed Use Discounts:** For predictable resource usage

### Cost Monitoring
```bash
# Set up budget alerts
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="DuckDB Analytics Budget" \
  --budget-amount=100USD \
  --threshold-rules=percent=0.8,spending-basis=CURRENT_SPEND \
  --threshold-rules=percent=1.0,spending-basis=CURRENT_SPEND
```

## 🔄 CI/CD Pipeline

### Cloud Build Configuration

Create `cloudbuild.yaml`:
```yaml
steps:
# Build backend image
- name: 'gcr.io/cloud-builders/docker'
  args: 
  - 'build'
  - '-t'
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/duckdb-analytics/backend:$COMMIT_SHA'
  - './backend'
  
# Build frontend image
- name: 'gcr.io/cloud-builders/docker'
  args:
  - 'build' 
  - '-t'
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/duckdb-analytics/frontend:$COMMIT_SHA'
  - './frontend'

# Push backend image
- name: 'gcr.io/cloud-builders/docker'
  args:
  - 'push'
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/duckdb-analytics/backend:$COMMIT_SHA'
  
# Push frontend image  
- name: 'gcr.io/cloud-builders/docker'
  args:
  - 'push'
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/duckdb-analytics/frontend:$COMMIT_SHA'

# Deploy backend to Cloud Run
- name: 'gcr.io/cloud-builders/gcloud'
  args:
  - 'run'
  - 'deploy'
  - 'duckdb-backend'
  - '--image'
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/duckdb-analytics/backend:$COMMIT_SHA'
  - '--region'
  - '${_REGION}'
  - '--platform'
  - 'managed'

# Deploy frontend to Cloud Run  
- name: 'gcr.io/cloud-builders/gcloud'
  args:
  - 'run'
  - 'deploy' 
  - 'duckdb-frontend'
  - '--image'
  - '${_REGION}-docker.pkg.dev/$PROJECT_ID/duckdb-analytics/frontend:$COMMIT_SHA'
  - '--region'
  - '${_REGION}'
  - '--platform'
  - 'managed'

substitutions:
  _REGION: us-central1

options:
  logging: CLOUD_LOGGING_ONLY
```

### Create Build Trigger
```bash
# Create build trigger for GitHub
gcloud builds triggers create github \
  --repo-name=duckdb-analytics \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## 🚨 Troubleshooting

### Common Issues

1. **Service not accessible:** Check IAM permissions and firewall rules
2. **Cold starts:** Use min-instances > 0 for critical services
3. **Memory limits:** Monitor Cloud Run memory usage and adjust
4. **SSL certificate issues:** Verify domain ownership and DNS configuration

### Debug Commands
```bash
# Check Cloud Run service status
gcloud run services describe duckdb-backend --region=us-central1

# View service logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=duckdb-backend" --limit=50

# Test load balancer health
curl -H "Host: your-domain.com" http://LOAD_BALANCER_IP/api/v1/health

# Check BigQuery jobs
bq ls -j --max_results=10
```

### Performance Optimization
```bash
# Enable Cloud Trace for request tracing
gcloud services enable cloudtrace.googleapis.com

# Enable Cloud Profiler for performance analysis  
gcloud services enable cloudprofiler.googleapis.com
```

This comprehensive GCP deployment guide provides everything needed to deploy your DuckDB analytics application to Google Cloud with enterprise-grade scalability, security, and cost optimization.