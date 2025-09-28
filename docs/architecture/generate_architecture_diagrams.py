# Architecture Documentation
# Install diagrams: pip install diagrams

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL  # Using PostgreSQL as DuckDB alternative
from diagrams.programming.framework import Fastapi, React
from diagrams.onprem.network import Nginx
from diagrams.generic.storage import Storage
from diagrams.generic.compute import Rack
from diagrams.aws.network import CloudFront
from diagrams.programming.language import Python, Nodejs, TypeScript
from diagrams.onprem.client import Users
from diagrams.onprem.monitoring import Grafana
from diagrams.generic.blank import Blank

# AWS imports
from diagrams.aws.compute import ECS, Fargate, Lambda
from diagrams.aws.database import RDS, DynamodbTable
from diagrams.aws.network import ALB, Route53, CloudFront, ElbApplicationLoadBalancer
from diagrams.aws.storage import S3
from diagrams.aws.analytics import Athena, Quicksight
from diagrams.aws.management import Cloudwatch, Cloudformation
from diagrams.aws.security import IAM

# GCP imports  
from diagrams.gcp.compute import Run, GKE, Functions as GCPFunctions
from diagrams.gcp.database import SQL
from diagrams.gcp.network import LoadBalancing, DNS, CDN
from diagrams.gcp.storage import GCS
from diagrams.gcp.analytics import Datalab, BigQuery
from diagrams.gcp.devtools import GCR
from diagrams.gcp.operations import Monitoring as GCPMonitoring

def create_system_architecture():
    """Create overall system architecture diagram"""
    
    with Diagram("DuckDB E-commerce Analytics - System Architecture", 
                 show=False, 
                 direction="TB",
                 filename="diagrams/architecture_system"):
        
        users = Users("Users")
        
        with Cluster("Docker Environment"):
            with Cluster("Frontend Service"):
                frontend = React("Next.js 15\nDashboard")
                frontend_docker = Docker("Frontend\nContainer")
                
            with Cluster("Backend Service"):
                api = Fastapi("FastAPI\nREST API")
                backend_docker = Docker("Backend\nContainer")
                
            with Cluster("Data Layer"):
                duckdb = PostgreSQL("DuckDB\nDatabase")
                data_volume = Storage("Data\nVolume")
        
        with Cluster("Development"):
            examples = Python("Practice\nExamples")
            docs = Storage("Documentation")
        
        # Connections
        users >> Edge(label="HTTP:3000") >> frontend
        frontend >> Edge(label="API calls") >> api
        api >> Edge(label="SQL queries") >> duckdb
        duckdb - data_volume
        
        # Docker connections
        frontend - frontend_docker
        api - backend_docker

def create_container_architecture():
    """Create containerized architecture diagram"""
    
    with Diagram("DuckDB Analytics - Container Architecture", 
                 show=False, 
                 direction="LR",
                 filename="diagrams/architecture_containers"):
        
        user = Users("User\nBrowser")
        
        with Cluster("Docker Compose Network"):
            with Cluster("Frontend Container\nPort: 3000"):
                nextjs = React("Next.js 15")
                node = Nodejs("Node 20")
                
            with Cluster("Backend Container\nPort: 8000"):
                fastapi = Fastapi("FastAPI")
                uvicorn = Python("Uvicorn\nASGI Server")
                
            with Cluster("Data Persistence"):
                db_file = PostgreSQL("ecommerce.duckdb")
                volume = Storage("Docker\nVolume")
        
        # User interactions
        user >> Edge(label="HTTP:3000\nDashboard") >> nextjs
        nextjs >> Edge(label="API Requests\nHTTP:8000") >> fastapi
        fastapi >> Edge(label="SQL Queries") >> db_file
        
        # Container internals
        nextjs - node
        fastapi - uvicorn
        db_file - volume

def create_data_flow_architecture():
    """Create data flow architecture diagram"""
    
    with Diagram("DuckDB Analytics - Data Flow Architecture", 
                 show=False, 
                 direction="TB",
                 filename="diagrams/architecture_dataflow"):
        
        with Cluster("Data Sources"):
            customers_csv = Storage("customers.csv")
            orders_csv = Storage("orders.csv")
            products_csv = Storage("products.csv")
            sessions_csv = Storage("web_sessions.csv")
            
        with Cluster("Data Processing"):
            etl = Python("Data Generation\n& ETL Scripts")
            
        with Cluster("Database Layer"):
            duckdb_main = PostgreSQL("DuckDB\nAnalytics Engine")
            
        with Cluster("API Layer"):
            endpoints = Fastapi("REST API\nEndpoints")
            models = Python("Pydantic\nModels")
            
        with Cluster("Frontend Layer"):
            dashboard = React("Interactive\nDashboard")
            charts = TypeScript("Chart\nComponents")
            modals = TypeScript("Modal\nSystem")
            
        with Cluster("User Interface"):
            metrics = Blank("Key Metrics")
            analytics = Blank("Revenue Analysis")
            segments = Blank("Customer Segments")
        
        # Data flow connections
        [customers_csv, orders_csv, products_csv, sessions_csv] >> etl
        etl >> duckdb_main
        duckdb_main >> endpoints
        endpoints >> models
        models >> dashboard
        dashboard >> charts
        dashboard >> modals
        
        # Individual connections from UI components to analytics
        charts >> metrics
        charts >> analytics
        modals >> segments

def create_development_architecture():
    """Create development environment architecture"""
    
    with Diagram("DuckDB Analytics - Development Architecture", 
                 show=False, 
                 direction="TB",
                 filename="diagrams/architecture_development"):
        
        with Cluster("Development Environment"):
            with Cluster("Backend Development"):
                backend_dev = Python("FastAPI\nDev Server")
                api_tests = Storage("API Test\nFiles (.http)")
                
            with Cluster("Frontend Development"):
                frontend_dev = React("Next.js\nDev Server")
                hot_reload = Nodejs("Hot Reload\nEnabled")
                
            with Cluster("Practice & Learning"):
                basic_examples = Python("Basic DuckDB\nExamples")
                integration_examples = Python("Integration\nExamples")
                frontend_examples = Python("Frontend\nExamples")
        
        with Cluster("Production Environment"):
            with Cluster("Docker Containers"):
                prod_backend = Docker("Backend\nContainer")
                prod_frontend = Docker("Frontend\nContainer")
                
            with Cluster("Monitoring"):
                health_checks = Grafana("Health\nChecks")
                logs = Storage("Container\nLogs")
        
        # Development flow
        backend_dev >> Edge(label="Build") >> prod_backend
        frontend_dev >> Edge(label="Build") >> prod_frontend
        hot_reload - frontend_dev
        api_tests - backend_dev
        
        # Examples connection
        [basic_examples, integration_examples, frontend_examples] >> Edge(style="dashed") >> backend_dev

def create_deployment_architecture():
    """Create deployment architecture diagram"""
    
    with Diagram("DuckDB Analytics - Deployment Architecture", 
                 show=False, 
                 direction="LR",
                 filename="diagrams/architecture_deployment"):
        
        with Cluster("Local Development"):
            dev_env = Rack("Developer\nMachine")
            vscode = Storage("VS Code\nIDE")
            
        with Cluster("Containerization"):
            docker_compose = Docker("Docker\nCompose")
            
            with Cluster("Multi-Stage Builds"):
                frontend_build = Docker("Frontend\nBuilder")
                backend_build = Docker("Backend\nImage")
                
        with Cluster("Production Ready"):
            with Cluster("Service Mesh"):
                load_balancer = Nginx("Load\nBalancer")
                
            with Cluster("Scalable Services"):
                frontend_instances = [Docker("Frontend\nInstance 1"), 
                                    Docker("Frontend\nInstance 2")]
                backend_instances = [Docker("Backend\nInstance 1"), 
                                   Docker("Backend\nInstance 2")]
                
            with Cluster("Data Persistence"):
                persistent_volume = Storage("Persistent\nVolume")
                backup = Storage("Backup\nStorage")
        
        # Deployment flow
        dev_env >> vscode
        vscode >> docker_compose
        docker_compose >> [frontend_build, backend_build]
        [frontend_build, backend_build] >> load_balancer
        load_balancer >> frontend_instances
        load_balancer >> backend_instances
        backend_instances >> persistent_volume
        persistent_volume >> backup

def create_aws_deployment_architecture():
    """Create AWS cloud deployment architecture"""
    
    with Diagram("DuckDB Analytics - AWS Cloud Deployment", 
                 show=False, 
                 direction="TB",
                 filename="diagrams/architecture_aws_deployment"):
        
        users = Users("Users")
        
        with Cluster("AWS Cloud"):
            # DNS and CDN
            with Cluster("Edge Services"):
                route53 = Route53("Route 53\nDNS")
                cloudfront = CloudFront("CloudFront\nCDN")
                
            # Load Balancing
            with Cluster("Load Balancing"):
                alb = ElbApplicationLoadBalancer("Application\nLoad Balancer")
                
            # Container Services
            with Cluster("Container Platform"):
                ecs_cluster = ECS("ECS Cluster")
                
                with Cluster("Backend Service"):
                    backend_fargate = Fargate("FastAPI\nFargate Tasks")
                    
                with Cluster("Frontend Service"):
                    frontend_fargate = Fargate("Next.js\nFargate Tasks")
            
            # Data Services
            with Cluster("Data Layer"):
                s3_data = S3("S3\nData Lake")
                athena = Athena("Athena\nDuckDB Alternative")
                
            # Monitoring & Management
            with Cluster("Operations"):
                cloudwatch = Cloudwatch("CloudWatch\nMonitoring")
                iam = IAM("IAM\nSecurity")
                
        # Connections
        users >> route53
        route53 >> cloudfront
        cloudfront >> alb
        alb >> [backend_fargate, frontend_fargate]
        backend_fargate >> athena
        athena >> s3_data
        cloudwatch - [backend_fargate, frontend_fargate]

def create_gcp_deployment_architecture():
    """Create Google Cloud deployment architecture"""
    
    with Diagram("DuckDB Analytics - GCP Cloud Deployment", 
                 show=False, 
                 direction="TB",
                 filename="diagrams/architecture_gcp_deployment"):
        
        users = Users("Users")
        
        with Cluster("Google Cloud Platform"):
            # DNS and CDN
            with Cluster("Edge Services"):
                dns = DNS("Cloud DNS")
                cdn = CDN("Cloud CDN")
                
            # Load Balancing
            with Cluster("Load Balancing"):
                lb = LoadBalancing("Load Balancer")
                
            # Container Services  
            with Cluster("Container Platform"):
                gke = GKE("GKE Cluster")
                
                with Cluster("Backend Service"):
                    backend_run = Run("FastAPI\nCloud Run")
                    
                with Cluster("Frontend Service"):
                    frontend_run = Run("Next.js\nCloud Run")
            
            # Data Services
            with Cluster("Data Layer"):
                gcs = GCS("Cloud Storage\nData Lake")
                bigquery = BigQuery("BigQuery\nDuckDB Alternative")
                
            # Monitoring & Management
            with Cluster("Operations"):
                monitoring = GCPMonitoring("Cloud Monitoring")
                
        # Connections
        users >> dns
        dns >> cdn
        cdn >> lb
        lb >> [backend_run, frontend_run]
        backend_run >> bigquery
        bigquery >> gcs
        monitoring - [backend_run, frontend_run]

def create_hybrid_deployment_architecture():
    """Create hybrid/multi-cloud deployment architecture"""
    
    with Diagram("DuckDB Analytics - Hybrid Cloud Deployment", 
                 show=False, 
                 direction="TB",
                 filename="diagrams/architecture_hybrid_deployment"):
        
        users = Users("Users")
        
        with Cluster("Local Development"):
            local_docker = Docker("Local Docker\nDevelopment")
            
        with Cluster("AWS Production"):
            aws_ecs = ECS("ECS\nProduction")
            aws_s3 = S3("S3\nData Storage")
            
        with Cluster("GCP Analytics"):
            gcp_bigquery = BigQuery("BigQuery\nAnalytics")
            gcp_datastudio = Datalab("Data Lab\nReporting")
            
        with Cluster("On-Premise"):
            on_prem_db = PostgreSQL("DuckDB\nData Processing")
            
        # Connections
        users >> [local_docker, aws_ecs]
        local_docker >> on_prem_db
        aws_ecs >> aws_s3
        aws_s3 >> gcp_bigquery
        gcp_bigquery >> gcp_datastudio

if __name__ == "__main__":
    print("Generating architecture diagrams...")
    
    create_system_architecture()
    print("✓ System architecture diagram created")
    
    create_container_architecture()
    print("✓ Container architecture diagram created")
    
    create_data_flow_architecture()
    print("✓ Data flow architecture diagram created")
    
    create_development_architecture()
    print("✓ Development architecture diagram created")
    
    create_deployment_architecture()
    print("✓ Deployment architecture diagram created")
    
    create_aws_deployment_architecture()
    print("✓ AWS deployment architecture diagram created")
    
    create_gcp_deployment_architecture()
    print("✓ GCP deployment architecture diagram created")
    
    create_hybrid_deployment_architecture()
    print("✓ Hybrid deployment architecture diagram created")
    
    print("\nAll diagrams generated in diagrams/ directory!")
    print("Files created:")
    print("- diagrams/architecture_system.png")
    print("- diagrams/architecture_containers.png") 
    print("- diagrams/architecture_dataflow.png")
    print("- diagrams/architecture_development.png")
    print("- diagrams/architecture_deployment.png")
    print("- diagrams/architecture_aws_deployment.png")
    print("- diagrams/architecture_gcp_deployment.png")
    print("- diagrams/architecture_hybrid_deployment.png")