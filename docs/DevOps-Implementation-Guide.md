# DevOps Implementation Guide

This document provides comprehensive guidance for implementing DevOps practices with the DuckDB Analytics Platform using Terraform Infrastructure as Code and GitHub Actions CI/CD.

## Architecture Overview

### Multi-Cloud Infrastructure
- **AWS**: ECS Fargate, Application Load Balancer, S3, RDS (optional)
- **GCP**: Cloud Run, Cloud Storage, Cloud SQL (optional)
- **Shared**: Container Registry, Monitoring, Logging

### CI/CD Pipeline
- **Source Control**: GitHub with branch protection
- **Build**: Docker multi-stage builds
- **Test**: Unit tests, integration tests, security scanning
- **Deploy**: Terraform automation, blue-green deployments
- **Monitor**: Health checks, metrics, alerts

## Quick Start

### 1. Prerequisites

#### Required Tools
```bash
# Install required CLI tools
brew install terraform
brew install --cask google-cloud-sdk
brew install awscli
brew install docker
```

#### Required Accounts
- GitHub repository with Actions enabled
- AWS account with appropriate permissions
- GCP project with billing enabled

### 2. Repository Setup

#### Clone and Initialize
```bash
git clone <your-repo-url>
cd duckdb-analytics
```

#### Environment Variables
Create `.env.example` for local development:
```bash
# Local Development
ENVIRONMENT=dev
PROJECT_NAME=duckdb-analytics

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# GCP Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

### 3. GitHub Secrets Setup

Configure the following secrets in GitHub repository settings:

#### AWS Secrets
```
AWS_ACCESS_KEY_ID          # AWS access key for deployment
AWS_SECRET_ACCESS_KEY      # AWS secret key
TERRAFORM_STATE_BUCKET     # S3 bucket for Terraform state
```

#### GCP Secrets
```
GCP_PROJECT_ID            # Google Cloud project ID
GCP_SA_KEY                # Service account key (JSON)
GCP_STATE_BUCKET          # GCS bucket for Terraform state
```

#### Notification Secrets (Optional)
```
SLACK_WEBHOOK_URL         # Slack notifications
DISCORD_WEBHOOK_URL       # Discord notifications
```

## Infrastructure Deployment

### AWS Deployment

#### 1. Initialize Terraform
```bash
cd terraform/aws
terraform init \
  -backend-config="bucket=your-terraform-state-bucket" \
  -backend-config="key=duckdb-analytics/dev/terraform.tfstate" \
  -backend-config="region=us-east-1"
```

#### 2. Plan Deployment
```bash
terraform plan \
  -var="environment=dev" \
  -var="project_name=duckdb-analytics" \
  -out=tfplan
```

#### 3. Apply Infrastructure
```bash
terraform apply tfplan
```

#### 4. Verify Deployment
```bash
# Check ECS services
aws ecs list-services --cluster duckdb-analytics-dev-cluster

# Check load balancer
aws elbv2 describe-load-balancers
```

### GCP Deployment

#### 1. Initialize Terraform
```bash
cd terraform/gcp
terraform init \
  -backend-config="bucket=your-terraform-state-bucket" \
  -backend-config="prefix=duckdb-analytics/dev"
```

#### 2. Plan Deployment
```bash
terraform plan \
  -var="project_id=your-project-id" \
  -var="environment=dev" \
  -out=tfplan
```

#### 3. Apply Infrastructure
```bash
terraform apply tfplan
```

#### 4. Verify Deployment
```bash
# Check Cloud Run services
gcloud run services list --region=us-central1

# Check storage buckets
gcloud storage buckets list
```

## CI/CD Pipeline Usage

### Triggering Deployments

#### Automatic Deployment (Push to main)
```bash
git push origin main
```
- Triggers full CI/CD pipeline
- Runs tests, builds containers, deploys to staging
- Requires manual approval for production

#### Manual Infrastructure Management
Use GitHub Actions workflow dispatch:
1. Go to Actions → Infrastructure Management
2. Select environment (dev/staging/prod)
3. Choose action (plan/apply/destroy)
4. Run workflow

#### Feature Branch Testing
```bash
git checkout -b feature/new-feature
git push origin feature/new-feature
```
- Creates pull request
- Runs tests and security scans
- Provides Terraform plan preview

### Environment Promotion

#### Development → Staging
```bash
# Automatic on main branch push
git checkout main
git merge feature/new-feature
git push origin main
```

#### Staging → Production
```bash
# Manual approval required in GitHub Actions
# 1. Staging deployment completes successfully
# 2. Approve production deployment in GitHub
# 3. Production deployment executes
```

## Configuration Management

### Environment-Specific Configuration

#### Development Environment
```hcl
# terraform/aws/environments/dev.tfvars
environment = "dev"
auto_scaling = {
  min_capacity = 1
  max_capacity = 3
  target_cpu   = 70
}
container_cpu = {
  backend  = 256
  frontend = 256
}
container_memory = {
  backend  = 512
  frontend = 512
}
```

#### Production Environment
```hcl
# terraform/aws/environments/prod.tfvars
environment = "prod"
auto_scaling = {
  min_capacity = 2
  max_capacity = 20
  target_cpu   = 60
}
container_cpu = {
  backend  = 1024
  frontend = 512
}
container_memory = {
  backend  = 2048
  frontend = 1024
}
```

### Application Configuration

#### Backend Environment Variables
```yaml
# docker-compose.yml
environment:
  - ENVIRONMENT=${ENVIRONMENT}
  - DATABASE_URL=${DATABASE_URL}
  - REDIS_URL=${REDIS_URL}
  - AWS_REGION=${AWS_REGION}
  - S3_BUCKET=${S3_BUCKET}
```

#### Frontend Environment Variables
```yaml
environment:
  - NEXT_PUBLIC_API_URL=${API_URL}
  - NEXT_PUBLIC_ENVIRONMENT=${ENVIRONMENT}
  - NEXT_PUBLIC_ANALYTICS_ID=${ANALYTICS_ID}
```

## Monitoring and Observability

### Health Checks

#### Application Health Endpoints
- **Backend**: `GET /health`
- **Frontend**: `GET /` (homepage load)
- **Database**: Connection test in health endpoint

#### Infrastructure Health Checks
- **AWS**: ECS service health, ALB target groups
- **GCP**: Cloud Run instance health, uptime checks

### Monitoring Dashboards

#### AWS CloudWatch
- ECS service metrics
- Application Load Balancer metrics
- Custom application metrics
- Log aggregation and alerts

#### GCP Cloud Monitoring
- Cloud Run metrics
- Storage and networking metrics
- Custom dashboards
- Alert policies

### Logging Strategy

#### Centralized Logging
```yaml
# Application logs
level: INFO
format: JSON
fields:
  - timestamp
  - level  
  - message
  - service
  - trace_id
  - user_id
```

#### Log Retention
- **Development**: 7 days
- **Staging**: 14 days  
- **Production**: 90 days

### Alerting Configuration

#### Critical Alerts
- Service unavailability
- Error rate > 5%
- Response time > 2 seconds
- Infrastructure failures

#### Warning Alerts
- High resource utilization
- Scaling events
- Performance degradation

## Security Best Practices

### Infrastructure Security

#### Network Security
- VPC with private subnets
- Security groups with least privilege
- Web Application Firewall (WAF)
- SSL/TLS encryption

#### Access Management
- IAM roles with minimal permissions
- Service accounts for applications
- No hard-coded credentials
- Regular key rotation

### Application Security

#### Container Security
- Multi-stage Docker builds
- Security scanning in CI/CD
- Minimal base images
- Regular base image updates

#### Runtime Security
- Environment variable encryption
- Secrets management
- Input validation
- SQL injection prevention

### Compliance and Auditing

#### Audit Trails
- All infrastructure changes logged
- Deployment history tracking
- Access logs retention
- Change approval records

## Disaster Recovery

### Backup Strategy

#### Database Backups
- **AWS**: RDS automated backups (7 days)
- **GCP**: Cloud SQL automated backups (7 days)
- Cross-region backup replication

#### Application Data Backups
- S3 versioning and lifecycle policies
- Cloud Storage versioning
- Regular backup testing

### Recovery Procedures

#### Service Recovery
1. Identify failed components
2. Check monitoring dashboards
3. Review recent deployments
4. Rollback if necessary
5. Restore from backups if needed

#### Infrastructure Recovery
1. Terraform state backup
2. Infrastructure rebuild from code
3. Data restoration procedures
4. Service verification

### Business Continuity

#### Multi-Region Deployment
- Active-passive setup
- DNS failover configuration
- Data synchronization
- Regular disaster recovery testing

## Performance Optimization

### Application Performance

#### Backend Optimization
- Connection pooling
- Query optimization
- Caching strategies
- Async processing

#### Frontend Optimization
- Code splitting
- Image optimization
- CDN utilization
- Progressive loading

### Infrastructure Performance

#### Auto Scaling Configuration
```hcl
# Optimized scaling policies
auto_scaling = {
  min_capacity    = 2
  max_capacity    = 20
  target_cpu      = 60
  scale_up_cooldown   = 300  # 5 minutes
  scale_down_cooldown = 600  # 10 minutes
}
```

#### Resource Right-Sizing
- CPU and memory monitoring
- Cost optimization
- Performance testing
- Regular capacity planning

## Troubleshooting Guide

### Common Issues

#### Deployment Failures
```bash
# Check pipeline logs
gh run view --log

# Check Terraform state
terraform state list
terraform show

# Check service logs
aws logs tail /aws/ecs/duckdb-analytics --follow
```

#### Performance Issues
```bash
# Check service metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization

# Check application logs
aws logs filter-log-events \
  --log-group-name /aws/ecs/duckdb-analytics \
  --start-time 1640995200000
```

#### Network Connectivity
```bash
# Test service endpoints
curl -I https://api.duckdb-analytics.com/health

# Check security groups
aws ec2 describe-security-groups \
  --group-ids sg-12345678
```

### Debug Commands

#### Container Debugging
```bash
# ECS task debugging
aws ecs execute-command \
  --cluster duckdb-analytics-cluster \
  --task task-id \
  --command "/bin/bash" \
  --interactive

# Cloud Run debugging  
gcloud run services logs read duckdb-analytics-backend
```

#### Database Debugging
```bash
# Connection testing
psql -h database-endpoint -U username -d database_name

# Query performance
EXPLAIN ANALYZE SELECT * FROM analytics_data;
```

## Cost Optimization

### Resource Management

#### Auto-Shutdown Policies
- Development environment shutdown
- Scheduled scaling policies
- Spot instances for non-critical workloads

#### Cost Monitoring
```bash
# AWS Cost Explorer
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY

# GCP Billing
gcloud billing budgets list
```

### Optimization Strategies

#### Infrastructure Costs
- Reserved instances for predictable workloads
- Spot instances for batch processing
- Right-sizing based on metrics
- Regular cost reviews

#### Storage Costs
- Lifecycle policies for data
- Compression strategies
- Archive policies
- Data retention policies

## Maintenance and Updates

### Regular Maintenance Tasks

#### Weekly Tasks
- Security patch reviews
- Performance metric analysis
- Cost optimization review
- Backup verification

#### Monthly Tasks
- Dependency updates
- Infrastructure capacity planning
- Security audit
- Disaster recovery testing

### Update Procedures

#### Application Updates
1. Feature branch development
2. Pull request review
3. Automated testing
4. Staging deployment
5. Production deployment

#### Infrastructure Updates
1. Terraform plan review
2. Change approval
3. Staging environment testing
4. Production deployment
5. Rollback plan verification

## Support and Documentation

### Getting Help

#### Internal Documentation
- Architecture decisions records (ADRs)
- Runbooks for common procedures
- Troubleshooting guides
- API documentation

#### External Resources
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)

### Contributing

#### Development Workflow
1. Create feature branch
2. Implement changes
3. Add/update tests
4. Update documentation
5. Submit pull request
6. Code review
7. Merge to main

#### Infrastructure Changes
1. Update Terraform code
2. Run terraform plan
3. Document changes
4. Get approval
5. Apply changes
6. Verify deployment
7. Update documentation

---

## Conclusion

This DevOps implementation provides a robust, scalable, and maintainable infrastructure for the DuckDB Analytics Platform. The combination of Infrastructure as Code with Terraform and automated CI/CD with GitHub Actions ensures consistent, reliable deployments across multiple cloud providers.

Key benefits:
- **Consistency**: Infrastructure defined as code
- **Reliability**: Automated testing and deployment
- **Scalability**: Auto-scaling and multi-region support
- **Security**: Best practices and compliance
- **Observability**: Comprehensive monitoring and logging
- **Maintainability**: Clear procedures and documentation

For additional support or questions, refer to the troubleshooting guide or contact the platform team.