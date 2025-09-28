# Monitoring and Logging Configuration for DuckDB Analytics Platform
# Provides comprehensive observability for Cloud Run services

# Log sink for application logs
resource "google_logging_project_sink" "app_logs" {
  name        = "${local.name_suffix}-app-logs"
  destination = "storage.googleapis.com/${google_storage_bucket.logs_bucket.name}"

  filter = <<-EOT
    resource.type="cloud_run_revision"
    resource.labels.service_name=~"${local.name_suffix}-(backend|frontend)"
    severity >= "INFO"
  EOT

  unique_writer_identity = true
}

# Grant sink permission to write to bucket
resource "google_storage_bucket_iam_member" "log_sink_writer" {
  bucket = google_storage_bucket.logs_bucket.name
  role   = "roles/storage.objectCreator"
  member = google_logging_project_sink.app_logs.writer_identity
}

# Log-based metrics
resource "google_logging_metric" "error_rate" {
  name   = "${local.name_suffix}-error-rate"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    resource.labels.service_name=~"${local.name_suffix}-(backend|frontend)"
    severity >= "ERROR"
  EOT

  metric_descriptor {
    metric_kind  = "GAUGE"
    value_type   = "INT64"
    display_name = "Error Rate"
  }

  value_extractor = "EXTRACT(jsonPayload.level)"

  label_extractors = {
    "service" = "EXTRACT(resource.labels.service_name)"
    "region"  = "EXTRACT(resource.labels.location)"
  }
}

resource "google_logging_metric" "response_time" {
  name   = "${local.name_suffix}-response-time"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    resource.labels.service_name=~"${local.name_suffix}-(backend|frontend)"
    httpRequest.requestMethod!=""
  EOT

  metric_descriptor {
    metric_kind  = "GAUGE"
    value_type   = "DOUBLE"
    unit         = "s"
    display_name = "Response Time"
  }

  value_extractor = "EXTRACT(httpRequest.latency)"

  label_extractors = {
    "service" = "EXTRACT(resource.labels.service_name)"
    "method"  = "EXTRACT(httpRequest.requestMethod)"
  }
}

# Cloud Monitoring Alert Policies
resource "google_monitoring_alert_policy" "high_error_rate" {
  count        = var.monitoring_config.enable_alerting ? 1 : 0
  display_name = "${local.name_suffix} High Error Rate"

  documentation {
    content = "Alert when error rate exceeds 5% for 5 minutes"
  }

  conditions {
    display_name = "High Error Rate Condition"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=monitoring.regex.full_match(\"${local.name_suffix}-(backend|frontend)\")"
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.labels.service_name"]
      }

      trigger {
        count = 1
      }
    }
  }

  alert_strategy {
    auto_close = "1800s"
  }

  combiner = "OR"
  enabled  = true

  notification_channels = var.monitoring_config.notification_channels
}

resource "google_monitoring_alert_policy" "high_latency" {
  count        = var.monitoring_config.enable_alerting ? 1 : 0
  display_name = "${local.name_suffix} High Latency"

  documentation {
    content = "Alert when 95th percentile latency exceeds 2 seconds"
  }

  conditions {
    display_name = "High Latency Condition"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=monitoring.regex.full_match(\"${local.name_suffix}-(backend|frontend)\")"
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 2000 # 2 seconds in milliseconds

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_95"
        group_by_fields      = ["resource.labels.service_name"]
      }

      trigger {
        count = 1
      }
    }
  }

  combiner = "OR"
  enabled  = true

  notification_channels = var.monitoring_config.notification_channels
}

resource "google_monitoring_alert_policy" "instance_count" {
  count        = var.monitoring_config.enable_alerting ? 1 : 0
  display_name = "${local.name_suffix} High Instance Count"

  documentation {
    content = "Alert when instance count approaches maximum scaling limit"
  }

  conditions {
    display_name = "High Instance Count Condition"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=monitoring.regex.full_match(\"${local.name_suffix}-(backend|frontend)\")"
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = var.auto_scaling.max_instances * 0.8 # 80% of max instances

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_MAX"
        cross_series_reducer = "REDUCE_MAX"
        group_by_fields      = ["resource.labels.service_name"]
      }
    }
  }

  combiner = "OR"
  enabled  = true

  notification_channels = var.monitoring_config.notification_channels
}

# Custom Dashboard
resource "google_monitoring_dashboard" "main_dashboard" {
  dashboard_json = jsonencode({
    displayName = "${local.name_suffix} Monitoring Dashboard"

    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Request Rate"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=monitoring.regex.full_match(\"${local.name_suffix}-(backend|frontend)\")"
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["resource.labels.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Requests per second"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "Error Rate"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=monitoring.regex.full_match(\"${local.name_suffix}-(backend|frontend)\") AND response_code>=400"
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_RATE"
                        crossSeriesReducer = "REDUCE_SUM"
                        groupByFields      = ["resource.labels.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Error rate"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          yPos   = 4
          widget = {
            title = "Response Latency (95th percentile)"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=monitoring.regex.full_match(\"${local.name_suffix}-(backend|frontend)\")"
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_DELTA"
                        crossSeriesReducer = "REDUCE_PERCENTILE_95"
                        groupByFields      = ["resource.labels.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Latency (ms)"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          yPos   = 4
          widget = {
            title = "Active Instances"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=monitoring.regex.full_match(\"${local.name_suffix}-(backend|frontend)\")"
                      aggregation = {
                        alignmentPeriod    = "60s"
                        perSeriesAligner   = "ALIGN_MAX"
                        crossSeriesReducer = "REDUCE_MAX"
                        groupByFields      = ["resource.labels.service_name"]
                      }
                    }
                  }
                  plotType = "LINE"
                }
              ]
              yAxis = {
                label = "Instance count"
                scale = "LINEAR"
              }
            }
          }
        }
      ]
    }
  })
}

# Uptime checks
resource "google_monitoring_uptime_check_config" "backend_health" {
  display_name = "${local.name_suffix} Backend Health Check"
  timeout      = "10s"
  period       = "60s"

  http_check {
    request_method = "GET"
    path           = "/health"
    port           = "443"
    use_ssl        = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = replace(google_cloud_run_v2_service.backend.uri, "https://", "")
    }
  }

  content_matchers {
    content = "healthy"
    matcher = "CONTAINS_STRING"
  }
}

resource "google_monitoring_uptime_check_config" "frontend_health" {
  display_name = "${local.name_suffix} Frontend Health Check"
  timeout      = "10s"
  period       = "60s"

  http_check {
    request_method = "GET"
    path           = "/"
    port           = "443"
    use_ssl        = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = replace(google_cloud_run_v2_service.frontend.uri, "https://", "")
    }
  }
}

# Error Reporting configuration
resource "google_logging_project_sink" "error_reporting" {
  name        = "${local.name_suffix}-error-reporting"
  destination = "logging.googleapis.com/projects/${var.project_id}/logs/errors"

  filter = <<-EOT
    resource.type="cloud_run_revision"
    resource.labels.service_name=~"${local.name_suffix}-(backend|frontend)"
    severity >= "ERROR"
  EOT

  unique_writer_identity = true
}