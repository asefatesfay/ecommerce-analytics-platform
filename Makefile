# E-commerce Analytics Platform Makefile
# =====================================
# 
# This Makefile provides commands to build, test, and run the entire platform locally.
# It replicates the CI/CD pipeline steps for local development and testing.

.PHONY: help install install-backend install-frontend clean test test-backend test-frontend \
        build run-backend run-frontend run-full setup-data setup-data-full lint format type-check check-deps \
        docker-build docker-run docker-stop logs

# Default target
help: ## Show this help message
	@echo "E-commerce Analytics Platform - Available Commands:"
	@echo "=================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup      # Install all dependencies and setup data"
	@echo "  make test       # Run all tests"
	@echo "  make run-full   # Start both backend and frontend"

# Variables
PYTHON := python3
NODE := node
NPM := npm
PIP := pip3
BACKEND_DIR := backend
FRONTEND_DIR := frontend
DATA_DIR := data
VENV_DIR := $(BACKEND_DIR)/venv
VENV_PYTHON := $(shell pwd)/$(VENV_DIR)/bin/python
VENV_PIP := $(shell pwd)/$(VENV_DIR)/bin/pip

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
NC := \033[0m # No Color

##@ Setup Commands

setup: clean install setup-data ## Complete setup: install dependencies and generate data
	@echo "$(GREEN)✅ Setup complete! Run 'make test' to verify everything works.$(NC)"

install: install-backend install-frontend ## Install all dependencies (backend + frontend)

install-backend: create-venv ## Install Python backend dependencies
	@echo "$(BLUE)📦 Installing backend dependencies...$(NC)"
	$(VENV_PIP) install -r $(BACKEND_DIR)/requirements.txt
	@echo "$(GREEN)✅ Backend dependencies installed in virtual environment$(NC)"
	@echo "$(YELLOW)To activate manually: source $(VENV_DIR)/bin/activate$(NC)"

create-venv: ## Create Python virtual environment if it doesn't exist
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(BLUE)🐍 Creating Python virtual environment...$(NC)"; \
		cd $(BACKEND_DIR) && $(PYTHON) -m venv venv; \
		echo "$(GREEN)✅ Virtual environment created$(NC)"; \
	fi

install-frontend: ## Install Node.js frontend dependencies  
	@echo "$(BLUE)📦 Installing frontend dependencies...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) ci
	@echo "$(GREEN)✅ Frontend dependencies installed$(NC)"

setup-data: create-venv ## Generate test database for local development
	@echo "$(BLUE)🦆 Generating test database...$(NC)"
	@echo "$(YELLOW)Using minimal dataset for faster setup...$(NC)"
	@rm -f $(BACKEND_DIR)/data/ecommerce.duckdb || true
	cd $(BACKEND_DIR)/src && MINIMAL_DATA=true $(VENV_PYTHON) 01_data_generation.py
	@echo "$(GREEN)✅ Test database created$(NC)"

setup-data-full: create-venv ## Generate full test database with complete dataset
	@echo "$(BLUE)🦆 Generating FULL test database...$(NC)"
	@echo "$(YELLOW)⚠️ This may take several minutes...$(NC)"
	@rm -f $(BACKEND_DIR)/data/ecommerce.duckdb || true
	cd $(BACKEND_DIR)/src && $(VENV_PYTHON) 01_data_generation.py
	@echo "$(GREEN)✅ Full test database created$(NC)"

##@ Testing Commands

test: test-backend test-frontend ## Run all tests (backend + frontend)
	@echo "$(GREEN)🎉 All tests completed!$(NC)"

test-backend: install-backend setup-data ## Run backend API tests
	@echo "$(BLUE)🧪 Running backend tests...$(NC)"
	cd $(BACKEND_DIR) && PYTHONPATH=src $(VENV_PYTHON) -m pytest tests/ -v --tb=short
	@echo "$(GREEN)✅ Backend tests completed$(NC)"

test-frontend: install-frontend ## Run frontend tests and type checking
	@echo "$(BLUE)🧪 Running frontend tests and type checking...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run type-check
	cd $(FRONTEND_DIR) && $(NPM) run lint
	cd $(FRONTEND_DIR) && CI=true $(NPM) run test:ci
	@echo "$(GREEN)✅ Frontend tests completed$(NC)"

test-api-manual: ## Run manual API tests (requires running backend)
	@echo "$(BLUE)🔍 Running manual API tests...$(NC)"
	cd $(BACKEND_DIR)/src/api && $(PYTHON) test_api.py
	@echo "$(GREEN)✅ Manual API tests completed$(NC)"

##@ Code Quality Commands

lint: lint-backend lint-frontend ## Run all linting (Python + JavaScript)
	@echo "$(GREEN)✅ All linting completed$(NC)"

lint-backend: install-backend ## Run Python linting with flake8
	@echo "$(BLUE)🔍 Running Python linting...$(NC)"
	cd $(BACKEND_DIR) && $(VENV_PYTHON) -m flake8 src/
	@echo "$(GREEN)✅ Python linting completed$(NC)"

lint-frontend: install-frontend ## Run JavaScript/TypeScript linting
	@echo "$(BLUE)🔍 Running frontend linting...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run lint
	@echo "$(GREEN)✅ Frontend linting completed$(NC)"

type-check: install-frontend ## Run TypeScript type checking
	@echo "$(BLUE)🔍 Running TypeScript type checking...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run type-check
	@echo "$(GREEN)✅ Type checking completed$(NC)"

format: format-backend ## Format code automatically
	@echo "$(GREEN)✅ Code formatting completed$(NC)"

format-backend: install-backend ## Format Python code with black
	@echo "$(BLUE)🎨 Formatting Python code...$(NC)"
	cd $(BACKEND_DIR) && $(VENV_PYTHON) -m black src/ --line-length 120
	@echo "$(GREEN)✅ Python code formatted$(NC)"

lint-fix: format-backend lint-backend ## Format code and run linting
	@echo "$(GREEN)✅ Code formatted and linted$(NC)"

##@ Development Commands

run-backend: install-backend setup-data ## Start the backend API server
	@echo "$(BLUE)🚀 Starting backend server...$(NC)"
	@echo "$(YELLOW)Backend will be available at: http://localhost:8000$(NC)"
	@echo "$(YELLOW)API docs available at: http://localhost:8000/docs$(NC)"
	cd $(BACKEND_DIR)/src/api && PYTHONPATH=.. $(VENV_PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend: install-frontend ## Start the frontend development server
	@echo "$(BLUE)🚀 Starting frontend server...$(NC)"
	@echo "$(YELLOW)Frontend will be available at: http://localhost:3000$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run dev

run-full: ## Start both backend and frontend (requires 2 terminals)
	@echo "$(BLUE)🚀 To run full stack:$(NC)"
	@echo "$(YELLOW)Terminal 1: make run-backend$(NC)"
	@echo "$(YELLOW)Terminal 2: make run-frontend$(NC)"
	@echo "$(YELLOW)Or use: make docker-run (single command)$(NC)"

##@ Build Commands

build: build-backend build-frontend ## Build both backend and frontend for production

build-backend: ## Build backend Docker image
	@echo "$(BLUE)🔨 Building backend Docker image...$(NC)"
	cd $(BACKEND_DIR) && docker build -t ecommerce-backend .
	@echo "$(GREEN)✅ Backend image built$(NC)"

build-frontend: install-frontend ## Build frontend for production
	@echo "$(BLUE)🔨 Building frontend...$(NC)"
	cd $(FRONTEND_DIR) && $(NPM) run build
	@echo "$(GREEN)✅ Frontend built$(NC)"

##@ Docker Commands

docker-build: ## Build all Docker images
	@echo "$(BLUE)🐳 Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✅ Docker images built$(NC)"

docker-run: ## Run full stack with Docker Compose
	@echo "$(BLUE)🐳 Starting full stack with Docker...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Full stack running! Use 'make docker-stop' to stop.$(NC)"

docker-stop: ## Stop Docker containers
	@echo "$(BLUE)🐳 Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Containers stopped$(NC)"

docker-logs: ## Show Docker container logs
	docker-compose logs -f

##@ Quality & Maintenance Commands

check-deps: ## Check for dependency issues
	@echo "$(BLUE)🔍 Checking dependencies...$(NC)"
	@echo "Python version: $(shell $(PYTHON) --version)"
	@echo "Node version: $(shell $(NODE) --version)"
	@echo "NPM version: $(shell $(NPM) --version)"
	@echo "Backend dependencies:"
	cd $(BACKEND_DIR) && $(PIP) list --format=freeze | grep -E "(fastapi|duckdb|pandas|uvicorn)" || echo "$(RED)❌ Missing backend deps$(NC)"
	@echo "Frontend dependencies:"
	cd $(FRONTEND_DIR) && $(NPM) list --depth=0 | grep -E "(next|react)" || echo "$(RED)❌ Missing frontend deps$(NC)"

clean: ## Clean build artifacts and caches
	@echo "$(BLUE)🧹 Cleaning up...$(NC)"
	# Python caches
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	# Node caches  
	cd $(FRONTEND_DIR) && rm -rf node_modules/.cache .next
	# Build artifacts
	cd $(FRONTEND_DIR) && rm -rf dist build
	# Logs
	rm -f $(BACKEND_DIR)/api.log
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-all: clean clean-venv ## Clean everything including virtual environment
	@echo "$(GREEN)✅ Full cleanup complete$(NC)"

clean-venv: ## Remove Python virtual environment
	@echo "$(BLUE)🗑️ Removing virtual environment...$(NC)"
	rm -rf $(VENV_DIR)
	@echo "$(GREEN)✅ Virtual environment removed$(NC)"

clean-data: ## Remove generated data (use with caution!)
	@echo "$(YELLOW)⚠️ This will remove all generated data files$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf $(DATA_DIR)/*.duckdb $(DATA_DIR)/*.csv; \
		echo "$(GREEN)✅ Data files removed$(NC)"; \
	else \
		echo "$(BLUE)Cancelled$(NC)"; \
	fi

##@ Information Commands

status: ## Show current project status
	@echo "$(BLUE)📊 Project Status$(NC)"
	@echo "=================="
	@echo "Backend dependencies: $(shell cd $(BACKEND_DIR) && $(PIP) list --format=freeze | wc -l) packages"
	@echo "Frontend dependencies: $(shell cd $(FRONTEND_DIR) && $(NPM) list --depth=0 2>/dev/null | grep -c "├──\|└──" || echo "0") packages"
	@echo "Data files: $(shell ls -la $(DATA_DIR)/ 2>/dev/null | grep -E "\.(duckdb|csv)$$" | wc -l) files"
	@echo "Docker images: $(shell docker images | grep ecommerce | wc -l) built"
	@echo ""
	@echo "Quick health check:"
	@$(MAKE) --no-print-directory check-deps

logs: ## Show recent logs
	@echo "$(BLUE)📝 Recent backend logs:$(NC)"
	@tail -20 $(BACKEND_DIR)/api.log 2>/dev/null || echo "No backend logs found"

##@ CI Simulation Commands

ci-test: clean install setup-data test ## Simulate full CI pipeline locally
	@echo "$(GREEN)🎉 CI simulation completed successfully!$(NC)"
	@echo "$(BLUE)This matches what runs in GitHub Actions$(NC)"

quick-test: setup-data test-backend ## Quick backend test (fastest verification)
	@echo "$(GREEN)✅ Quick test completed!$(NC)"