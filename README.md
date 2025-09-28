# DuckDB E-commerce Analytics Project

A comprehensive e-commerce analytics platform built with DuckDB, FastAPI, and Next.js, organized for easy development and containerization.

## 📁 Project Structure

```
duckdb/
├── backend/                 # FastAPI backend service
│   ├── src/                 # Source code
│   │   ├── api/            # FastAPI application
│   │   ├── database/       # DuckDB connection and queries
│   │   └── models/         # Data models
│   ├── api-requests/       # API test files
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── .dockerignore       # Backend ignore file
│
├── frontend/               # Next.js frontend application
│   ├── src/               # Source code
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   └── lib/          # Utilities
│   ├── package.json       # Node.js dependencies
│   ├── Dockerfile         # Frontend container
│   └── .dockerignore      # Frontend ignore file
│
├── examples/              # Learning and practice files
│   ├── 00_basic_duckdb_example.py
│   ├── 01_basic_duckdb_example.py
│   ├── 02_data_loading_examples.py
│   ├── 03_sql_operations_examples.py
│   ├── 04_integration_examples.py
│   ├── frontend_examples/ # Frontend examples
│   └── requirements.txt   # Example dependencies
│
├── docs/                  # Documentation
│   ├── README.md          # Original documentation
│   ├── API_README.md      # API documentation
│   ├── ADVANCED_FEATURES.md
│   ├── API_SOLUTION_SUMMARY.md
│   └── visualizations/    # Data visualizations
│
├── data/                  # Data files and databases
│   ├── ecommerce.db       # Main DuckDB database
│   └── my_database.db     # Practice database
│
├── venv/                  # Python virtual environment
├── docker-compose.yml     # Container orchestration
└── README.md             # This file
```

## 🏗️ Architecture

### **[📊 Complete Architecture Overview →](docs/ARCHITECTURE_OVERVIEW.md)**
*Comprehensive view of all system diagrams organized by functional areas with detailed explanations*

**Quick Architecture Overview:**
- **[System Architecture](docs/architecture/diagrams/architecture_system.png)**: High-level system design and relationships
- **[Development Environment](docs/architecture/diagrams/architecture_development.png)**: Local development setup and workflow
- **[Data Flow](docs/architecture/diagrams/architecture_dataflow.png)**: End-to-end data processing pipeline
- **[Container Strategy](docs/architecture/diagrams/architecture_containers.png)**: Docker containerization and orchestration
- **[Cloud Deployments](docs/ARCHITECTURE_OVERVIEW.md#-deployment-architectures)**: AWS, GCP, and hybrid cloud strategies

This project features a comprehensive architecture documented as code using visual diagrams generated with the [Diagrams](https://diagrams.mingrammer.com/) library.
- **Development Architecture:** Development environment and workflow
- **Deployment Architecture:** Production deployment strategy

📋 **[View Complete Architecture Documentation](docs/architecture/README.md)**

### Architecture Highlights
- **Microservices Design:** Separate backend and frontend services
- **Containerized Deployment:** Docker containers with health checks
- **Real-time Analytics:** DuckDB for high-performance data analysis
- **Modern Frontend:** Next.js with professional modal system
- **API-First:** RESTful backend with automatic documentation

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Production deployment:**
   ```bash
   docker-compose up -d
   ```
   - Backend API: http://localhost:8000
   - Frontend Dashboard: http://localhost:3000

2. **Development mode:**
   ```bash
   docker-compose --profile dev up -d
   ```
   - Backend API: http://localhost:8001 (with hot reload)
   - Frontend Dashboard: http://localhost:3001 (with hot reload)

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/api/main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Development

### Backend Development
- **Source:** `backend/src/`
- **API Endpoints:** `backend/src/api/main.py`
- **Database:** `backend/src/database/`
- **Models:** `backend/src/models/`

### Frontend Development  
- **Components:** `frontend/src/components/`
- **Pages:** `frontend/src/app/`
- **Services:** `frontend/src/services/`
- **Utilities:** `frontend/src/lib/`

### Practice & Examples
- **DuckDB Examples:** `examples/0*.py`
- **Frontend Examples:** `examples/frontend_examples/`

## 📊 Features

### Backend API
- ✅ FastAPI with automatic OpenAPI docs
- ✅ DuckDB integration with e-commerce data
- ✅ RESTful endpoints for analytics
- ✅ Error handling and validation
- ✅ Containerized deployment

### Frontend Dashboard
- ✅ Next.js 15 with React 19
- ✅ Professional modal system
- ✅ Interactive charts and metrics
- ✅ Time-based filtering
- ✅ Responsive design
- ✅ Real-time API integration

### DevOps
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Development and production profiles
- ✅ Health checks and monitoring
- ✅ Volume persistence for data

## 🛠 Container Commands

```bash
# Start all services
docker-compose up -d

# Start development services
docker-compose --profile dev up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild containers
docker-compose build
docker-compose up -d --force-recreate

# Remove everything (including volumes)
docker-compose down -v --remove-orphans
```

## 📈 API Documentation

When the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🎯 Next Steps

1. **Add monitoring:** Implement logging and metrics collection
2. **Add authentication:** Secure the API with JWT tokens
3. **Add caching:** Redis for improved performance
4. **Add testing:** Unit tests for backend and frontend
5. **Add CI/CD:** GitHub Actions or similar for deployment

## 📝 Notes

- The project maintains separation between development examples and production code
- Data persists in the `data/` directory and Docker volumes
- All services are networked together in Docker for seamless communication
- Environment variables can be customized in `docker-compose.yml`