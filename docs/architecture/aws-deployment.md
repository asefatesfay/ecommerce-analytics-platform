# AWS Deployment Guide

This guide covers deploying the DuckDB E-commerce Analytics application to Amazon Web Services (AWS).

## 🏗️ AWS Architecture Overview

The AWS deployment uses the following services:
- **ECS + Fargate:** Serverless container orchestration
- **Application Load Balancer (ALB):** Traffic distribution and SSL termination
- **Route 53:** DNS management
- **CloudFront:** Global CDN for static assets
- **S3:** Data lake for CSV files and application data
- **Athena:** SQL analytics on S3 data (DuckDB alternative for cloud scale)
- **CloudWatch:** Monitoring, logging, and alerting
- **IAM:** Security and access management

## 📋 Prerequisites

### 1. AWS CLI Setup
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

### 2. Create ECR Repositories
```bash
# Create repositories for container images
aws ecr create-repository --repository-name duckdb-backend --region us-east-1
aws ecr create-repository --repository-name duckdb-frontend --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### 3. Setup S3 Data Bucket
```bash
# Create S3 bucket for data storage
aws s3 mb s3://duckdb-analytics-data-<unique-suffix>

# Upload sample data
aws s3 cp data/ s3://duckdb-analytics-data-<unique-suffix>/data/ --recursive
```

## 🚀 Deployment Steps

### 1. Build and Push Container Images

```bash
# Navigate to project root
cd /path/to/duckdb-project

# Build backend image
docker build -t <account-id>.dkr.ecr.us-east-1.amazonaws.com/duckdb-backend:latest ./backend

# Build frontend image  
docker build -t <account-id>.dkr.ecr.us-east-1.amazonaws.com/duckdb-frontend:latest ./frontend

# Push images to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/duckdb-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/duckdb-frontend:latest
```

### 2. Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name duckdb-analytics-cluster --capacity-providers FARGATE
```

### 3. Create Task Definitions

**Backend Task Definition (backend-task-def.json):**
```json
{
  "family": "duckdb-backend",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/duckdb-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "S3_BUCKET",
          "value": "duckdb-analytics-data-<unique-suffix>"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/duckdb-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Frontend Task Definition (frontend-task-def.json):**
```json
{
  "family": "duckdb-frontend",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256", 
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/duckdb-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "API_URL",
          "value": "http://duckdb-alb-<random>.us-east-1.elb.amazonaws.com"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/duckdb-frontend", 
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 4. Register Task Definitions

```bash
# Register task definitions
aws ecs register-task-definition --cli-input-json file://backend-task-def.json
aws ecs register-task-definition --cli-input-json file://frontend-task-def.json
```

### 5. Create ALB and Target Groups

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name duckdb-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678

# Create target groups
aws elbv2 create-target-group \
  --name duckdb-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345678 \
  --target-type ip \
  --health-check-path /api/v1/health

aws elbv2 create-target-group \
  --name duckdb-frontend-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-12345678 \
  --target-type ip \
  --health-check-path /
```

### 6. Create ECS Services

```bash
# Create backend service
aws ecs create-service \
  --cluster duckdb-analytics-cluster \
  --service-name duckdb-backend-service \
  --task-definition duckdb-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678,subnet-87654321],securityGroups=[sg-12345678],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:<account-id>:targetgroup/duckdb-backend-tg/<id>,containerName=backend,containerPort=8000

# Create frontend service  
aws ecs create-service \
  --cluster duckdb-analytics-cluster \
  --service-name duckdb-frontend-service \
  --task-definition duckdb-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678,subnet-87654321],securityGroups=[sg-12345678],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:<account-id>:targetgroup/duckdb-frontend-tg/<id>,containerName=frontend,containerPort=3000
```

## 🔧 Infrastructure as Code

### Terraform Configuration

Create `aws-infrastructure/main.tf`:

```hcl
provider "aws" {
  region = var.aws_region
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "duckdb-analytics"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "duckdb-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = var.public_subnet_ids
}

# S3 Bucket for Data
resource "aws_s3_bucket" "data" {
  bucket = "duckdb-analytics-data-${random_string.suffix.result}"
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "ALB-${aws_lb.main.name}"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  enabled = true
  
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "ALB-${aws_lb.main.name}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
}
```

### Deploy with Terraform

```bash
# Initialize Terraform
cd aws-infrastructure
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

## 📊 Monitoring and Observability

### CloudWatch Setup

```bash
# Create log groups
aws logs create-log-group --log-group-name /ecs/duckdb-backend
aws logs create-log-group --log-group-name /ecs/duckdb-frontend

# Create custom metrics dashboard
aws cloudwatch put-dashboard \
  --dashboard-name DuckDBAnalytics \
  --dashboard-body file://cloudwatch-dashboard.json
```

### Sample CloudWatch Dashboard (cloudwatch-dashboard.json):
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", "ServiceName", "duckdb-backend-service"],
          [".", "MemoryUtilization", ".", "."]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Backend Service Metrics"
      }
    },
    {
      "type": "metric", 
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "app/duckdb-alb/<id>"],
          [".", "ResponseTime", ".", "."]
        ],
        "period": 300,
        "stat": "Average", 
        "region": "us-east-1",
        "title": "Load Balancer Metrics"
      }
    }
  ]
}
```

## 🛡️ Security Configuration

### IAM Roles and Policies

**ECS Task Execution Role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**S3 Access Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::duckdb-analytics-data-*",
        "arn:aws:s3:::duckdb-analytics-data-*/*"
      ]
    }
  ]
}
```

## 💰 Cost Optimization

### Strategies
1. **Use Fargate Spot:** 70% cost savings for non-critical workloads
2. **Right-size Tasks:** Monitor CPU/memory usage and adjust
3. **Auto Scaling:** Scale based on demand
4. **S3 Intelligent Tiering:** Automatic storage class optimization
5. **Reserved Capacity:** For predictable ALB and Athena usage

### Monitoring Costs
```bash
# Set up billing alerts
aws budgets create-budget --account-id <account-id> --budget file://budget.json
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow (.github/workflows/aws-deploy.yml):
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
          
      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
        
      - name: Build and push backend
        run: |
          docker build -t $ECR_REGISTRY/duckdb-backend:$GITHUB_SHA ./backend
          docker push $ECR_REGISTRY/duckdb-backend:$GITHUB_SHA
          
      - name: Build and push frontend  
        run: |
          docker build -t $ECR_REGISTRY/duckdb-frontend:$GITHUB_SHA ./frontend
          docker push $ECR_REGISTRY/duckdb-frontend:$GITHUB_SHA
          
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster duckdb-analytics --service duckdb-backend-service --force-new-deployment
          aws ecs update-service --cluster duckdb-analytics --service duckdb-frontend-service --force-new-deployment
```

## 🚨 Troubleshooting

### Common Issues

1. **Tasks not starting:** Check security groups and subnet configuration
2. **Load balancer health checks failing:** Verify health check endpoints
3. **High costs:** Review CloudWatch metrics and right-size resources
4. **Slow performance:** Check ALB metrics and consider CloudFront caching

### Debug Commands
```bash
# Check service status
aws ecs describe-services --cluster duckdb-analytics --services duckdb-backend-service

# View task logs
aws logs get-log-events --log-group-name /ecs/duckdb-backend --log-stream-name <stream-name>

# Monitor ALB health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

This comprehensive AWS deployment guide provides everything needed to deploy your DuckDB analytics application to AWS with enterprise-grade scalability, security, and monitoring.