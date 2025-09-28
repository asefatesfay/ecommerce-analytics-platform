# Architecture Documentation

This directory contains comprehensive architecture documentation for the DuckDB E-commerce Analytics project, documented as code using the [Diagrams](https://diagrams.mingrammer.com/) library.

## 📁 Directory Structure

```
docs/architecture/
├── README.md                           # This file
├── generate_architecture_diagrams.py  # Python script to generate all diagrams
├── diagrams/                          # Generated architecture diagrams
│   ├── architecture_system.png        # Overall system architecture
│   ├── architecture_containers.png    # Container architecture
│   ├── architecture_dataflow.png      # Data flow architecture
│   ├── architecture_development.png   # Development environment
│   └── architecture_deployment.png    # Deployment architecture
└── docs/                              # Architecture documentation
    ├── system_overview.md             # System overview documentation
    ├── container_strategy.md          # Containerization strategy
    ├── data_architecture.md           # Data architecture details
    └── deployment_guide.md            # Deployment guidelines
```

## 🚀 Quick Start

### Prerequisites

1. **Install Python dependencies:**
   ```bash
   cd /Users/x3p8/practice/ML/duckdb
   source venv/bin/activate
   pip install diagrams
   ```

2. **Install Graphviz (required by diagrams):**
   ```bash
   # macOS
   brew install graphviz
   
   # Ubuntu/Debian
   sudo apt-get install graphviz
   
   # Windows
   # Download from https://graphviz.org/download/
   ```

### Generate Architecture Diagrams

```bash
cd docs/architecture
python generate_architecture_diagrams.py
```

This will generate all architecture diagrams in the `diagrams/` subdirectory.

## 📊 Architecture Diagrams

### 1. System Architecture (`architecture_system.png`)
**Purpose:** High-level overview of the entire system
**Shows:**
- User interactions
- Frontend (Next.js) and Backend (FastAPI) services
- Database layer (DuckDB)
- Development environment

### 2. Container Architecture (`architecture_containers.png`)
**Purpose:** Detailed view of containerized services
**Shows:**
- Docker container setup
- Network communication between services
- Port mappings and volume mounts
- Service dependencies

### 3. Data Flow Architecture (`architecture_dataflow.png`)
**Purpose:** How data flows through the system
**Shows:**
- Data sources (CSV files)
- ETL processes
- Database operations
- API endpoints
- Frontend components

### 4. Development Architecture (`architecture_development.png`)
**Purpose:** Development environment and workflow
**Shows:**
- Local development setup
- Hot reload capabilities
- Testing frameworks
- Build processes

### 5. Deployment Architecture (`architecture_deployment.png`)
**Purpose:** Local/on-premise deployment strategy
**Shows:**
- CI/CD pipeline
- Container orchestration
- Load balancing
- Monitoring and logging

### 6. AWS Cloud Deployment (`architecture_aws_deployment.png`)
**Purpose:** AWS cloud deployment architecture
**Shows:**
- Route 53 DNS and CloudFront CDN
- Application Load Balancer (ALB)
- ECS with Fargate for container management
- S3 data lake with Athena for analytics
- CloudWatch monitoring and IAM security

### 7. GCP Cloud Deployment (`architecture_gcp_deployment.png`)
**Purpose:** Google Cloud Platform deployment
**Shows:**
- Cloud DNS and Cloud CDN
- Load balancer for traffic distribution
- Cloud Run for serverless containers
- BigQuery for data analytics
- Cloud Monitoring for observability

### 8. Hybrid Deployment (`architecture_hybrid_deployment.png`)
**Purpose:** Multi-cloud and hybrid deployment strategy
**Shows:**
- Local development with Docker
- AWS ECS for production workloads
- GCP BigQuery for analytics processing
- Cross-cloud data flow and integration

## 🏗️ System Components

### Frontend Layer
- **Technology:** Next.js 15 with React 19
- **Features:** 
  - Interactive dashboard
  - Real-time data visualization
  - Professional modal system
  - Time-based filtering

### Backend Layer
- **Technology:** FastAPI with Uvicorn
- **Features:**
  - RESTful API endpoints
  - DuckDB integration
  - Automatic API documentation
  - CORS support for frontend

### Database Layer
- **Technology:** DuckDB
- **Features:**
  - In-process analytical database
  - SQL-compatible interface
  - High-performance analytics
  - File-based storage

### Infrastructure Layer
- **Technology:** Docker & Docker Compose
- **Features:**
  - Containerized services
  - Service orchestration
  - Development and production profiles
  - Health checks and monitoring

## 🔄 Data Flow

1. **Data Ingestion:** CSV files → ETL Scripts → DuckDB
2. **API Layer:** DuckDB → FastAPI → REST Endpoints
3. **Frontend:** API Calls → React Components → User Interface
4. **User Interaction:** Dashboard → API Requests → Database Queries

## 🚀 Deployment Options

### Local Development
```bash
# Development mode (with hot reload)
docker-compose --profile dev up -d
```

### Production Deployment
```bash
# Production mode
docker-compose up -d
```

### Cloud Deployment Options

#### AWS Deployment
```bash
# Deploy to AWS ECS with Fargate
# Prerequisites: AWS CLI configured, ECR repositories created

# Build and push images
docker build -t your-account.dkr.ecr.region.amazonaws.com/duckdb-backend ./backend
docker build -t your-account.dkr.ecr.region.amazonaws.com/duckdb-frontend ./frontend

docker push your-account.dkr.ecr.region.amazonaws.com/duckdb-backend
docker push your-account.dkr.ecr.region.amazonaws.com/duckdb-frontend

# Deploy using AWS CDK, CloudFormation, or Terraform
```

**Key AWS Services:**
- **ECS + Fargate:** Serverless container platform
- **ALB:** Application load balancing with SSL termination
- **S3:** Data lake storage for CSV files and backups
- **Athena:** SQL queries on S3 data (DuckDB alternative)
- **CloudFront:** Global CDN for frontend assets
- **Route 53:** DNS management
- **CloudWatch:** Monitoring, logging, and alerting

#### GCP Deployment
```bash
# Deploy to Google Cloud Run
# Prerequisites: gcloud CLI configured, Artifact Registry setup

# Build and push images
docker build -t gcr.io/your-project/duckdb-backend ./backend
docker build -t gcr.io/your-project/duckdb-frontend ./frontend

docker push gcr.io/your-project/duckdb-backend
docker push gcr.io/your-project/duckdb-frontend

# Deploy to Cloud Run
gcloud run deploy backend --image gcr.io/your-project/duckdb-backend
gcloud run deploy frontend --image gcr.io/your-project/duckdb-frontend
```

**Key GCP Services:**
- **Cloud Run:** Fully managed serverless containers
- **Cloud Load Balancing:** Global load balancer
- **Cloud Storage:** Object storage for data files
- **BigQuery:** Serverless data warehouse (DuckDB alternative)
- **Cloud CDN:** Global content delivery
- **Cloud DNS:** Managed DNS service
- **Cloud Monitoring:** Observability and alerting

#### Hybrid/Multi-Cloud Strategy
```bash
# Development: Local Docker
docker-compose --profile dev up -d

# Production API: AWS ECS
# Analytics: GCP BigQuery + Data Studio
# Data Processing: On-premise DuckDB
```

### Scaling Options
- **Horizontal scaling:** Multiple container instances
- **Load balancing:** Cloud-native load balancers (ALB, GCP LB)
- **Database scaling:** 
  - **Local:** DuckDB clustering (future)
  - **Cloud:** Managed services (Athena, BigQuery)
- **Auto-scaling:** Cloud-native auto-scaling groups

## 📈 Performance Considerations

### Local Development
- **DuckDB:** Optimized for analytical workloads
- **FastAPI:** Async/await support for high concurrency
- **Next.js:** Static generation and client-side rendering
- **Docker:** Multi-stage builds for optimal image size

### Cloud Performance
- **AWS:**
  - **Fargate:** Right-sizing tasks for CPU/memory optimization
  - **ALB:** Connection pooling and SSL termination
  - **CloudFront:** Global edge locations for static assets
  - **Athena:** Columnar storage with automatic partitioning

- **GCP:**
  - **Cloud Run:** Automatic scaling from 0 to 1000+ instances
  - **BigQuery:** Petabyte-scale analytics with slots optimization
  - **Cloud CDN:** Global caching with smart routing
  - **Cloud Load Balancing:** Anycast IP for global performance

## 🛡️ Security Considerations

### Local Development
- **API Security:** CORS configuration, input validation
- **Container Security:** Non-root users, minimal base images
- **Data Security:** File-based database, volume encryption
- **Network Security:** Internal container networking

### Cloud Security

#### AWS Security
- **IAM:** Fine-grained permissions for services
- **VPC:** Private networking with security groups
- **ALB:** SSL/TLS termination with AWS Certificate Manager
- **CloudTrail:** Audit logging for all API calls
- **Secrets Manager:** Secure credential storage
- **GuardDuty:** Threat detection and monitoring

#### GCP Security
- **IAM:** Identity and access management
- **VPC:** Private Google Access and firewall rules
- **Cloud Armor:** DDoS protection and WAF
- **Cloud KMS:** Key management and encryption
- **Security Command Center:** Centralized security dashboard
- **Binary Authorization:** Container image security

### Data Security
- **Encryption at Rest:** Cloud storage encryption (S3, Cloud Storage)
- **Encryption in Transit:** TLS 1.2+ for all communications
- **Data Classification:** Sensitive data identification and protection
- **Backup Strategy:** Cross-region replication and point-in-time recovery

## � Cost Optimization

### AWS Cost Strategy
- **Fargate Spot:** Use Spot instances for development environments
- **S3 Intelligent Tiering:** Automatic storage class optimization
- **CloudWatch Logs:** Set retention periods to avoid excessive charges
- **Reserved Capacity:** For predictable workloads (Athena, ALB)
- **Auto Scaling:** Scale down during off-hours

### GCP Cost Strategy
- **Cloud Run:** Pay-per-request model, automatic scaling to zero
- **BigQuery:** On-demand pricing with query optimization
- **Committed Use Discounts:** For sustained workloads
- **Preemptible Instances:** For batch processing jobs
- **Cloud Storage:** Nearline/Coldline for archival data

### Multi-Cloud Cost Benefits
- **Workload Optimization:** Run workloads on most cost-effective platform
- **Vendor Negotiation:** Leverage competition for better pricing
- **Avoid Lock-in:** Flexibility to migrate based on cost changes
- **Geographic Optimization:** Use regional pricing differences

## �🔧 Maintenance

### Updating Diagrams
1. Modify `generate_architecture_diagrams.py`
2. Run the script to regenerate diagrams
3. Commit both code and generated diagrams

### Architecture Evolution
- Document changes in this README
- Update corresponding diagrams
- Maintain version history

### Cloud Infrastructure Management
- **Infrastructure as Code:** Use Terraform/CDK for reproducible deployments
- **Version Control:** Track infrastructure changes in git
- **Environment Parity:** Maintain consistency across dev/staging/prod
- **Monitoring:** Set up alerts for cost, performance, and security metrics

## 📚 Detailed Deployment Guides

### Cloud Platform Guides
- **[AWS Deployment Guide](aws-deployment.md)** - Complete AWS deployment with ECS, Fargate, ALB, and infrastructure as code
- **[GCP Deployment Guide](gcp-deployment.md)** - Comprehensive GCP deployment with Cloud Run, Load Balancing, and BigQuery

### Infrastructure as Code Examples
- **AWS:** Terraform configurations for ECS, ALB, S3, CloudWatch, and security
- **GCP:** Terraform configurations for Cloud Run, Load Balancing, BigQuery, and monitoring
- **Hybrid:** Multi-cloud strategies and deployment patterns

### CI/CD Pipelines
- **GitHub Actions:** Automated deployments to AWS and GCP
- **Cloud Build:** GCP-native CI/CD with Cloud Build and Artifact Registry
- **Monitoring:** CloudWatch and Cloud Monitoring integration

## 📚 Additional Resources

- [Diagrams Documentation](https://diagrams.mingrammer.com/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Docker Documentation](https://docs.docker.com/)

### Cloud Platform Documentation
- [AWS Container Services](https://aws.amazon.com/containers/)
- [Google Cloud Run](https://cloud.google.com/run)
- [AWS ECS](https://aws.amazon.com/ecs/)
- [BigQuery](https://cloud.google.com/bigquery)
- [AWS Athena](https://aws.amazon.com/athena/)