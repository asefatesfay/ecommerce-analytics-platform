# Container Architecture

This diagram shows the containerized architecture using Docker Compose, including development and production profiles.

```mermaid
graph TB
    subgraph "Development Environment"
        DEV["Developer Machine - VS Code + Extensions"]
        LOCAL["Local Testing - http://localhost:3001"]
    end

    subgraph "Container Network: app-network"
        direction TB
        
        subgraph "Frontend Container"
            FE["Next.js Application - Port: 3000/3001"]
            FE_VOL["/app Volume - Hot Reload"]
            FE --> FE_VOL
        end

        subgraph "Backend Container"
            BE["FastAPI Application - Port: 8000/8001"]
            BE_VOL["/app Volume - Hot Reload"]
            BE --> BE_VOL
        end

        subgraph "Data Volume"
            DB_VOL["DuckDB Data - Persistent Storage"]
            CSV_VOL["CSV Files - ./data Volume"]
        end
    end

    subgraph "Docker Compose Services"
        COMP["docker-compose.yml - Service Orchestration"]
        
        subgraph "Profiles"
            PROD_PROF["Production Profile - Port: 3000, 8000"]
            DEV_PROF["Development Profile - Port: 3001, 8001 - Hot Reload Enabled"]
        end
    end

    subgraph "External Network"
        INTERNET["Internet Access - Package Downloads"]
        REGISTRY["Docker Registry - Base Images"]
    end

    %% Developer Workflow
    DEV --> |"docker-compose up"| COMP
    DEV --> |"Code Changes"| FE_VOL
    DEV --> |"Code Changes"| BE_VOL

    %% Container Communication
    FE --> |"API Calls - Port 8000/8001"| BE
    BE --> |"File Access"| DB_VOL
    BE --> |"File Access"| CSV_VOL

    %% Service Management
    COMP --> FE
    COMP --> BE
    COMP --> DB_VOL

    %% Profile Selection
    COMP --> PROD_PROF
    COMP --> DEV_PROF

    %% External Dependencies
    FE --> |"npm install"| INTERNET
    BE --> |"pip install"| INTERNET
    COMP --> |"Pull Images"| REGISTRY

    %% Testing Access
    LOCAL --> FE
    DEV --> LOCAL

    %% Health Checks
    FE -.->|"Health Check - /_next/static"| FE
    BE -.->|"Health Check - /health"| BE

    %% Styling
    classDef dev fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef container fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef volume fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef service fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef external fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef network fill:#f1f8e9,stroke:#689f38,stroke-width:2px

    class DEV,LOCAL dev
    class FE,BE container
    class FE_VOL,BE_VOL,DB_VOL,CSV_VOL volume
    class COMP,PROD_PROF,DEV_PROF service
    class INTERNET,REGISTRY external
```

## Container Services

### Frontend Container
- **Technology**: Next.js with React 19
- **Ports**: 3000 (production), 3001 (development)
- **Features**: Hot reload, static optimization, TypeScript support

### Backend Container
- **Technology**: FastAPI with Python 3.11+
- **Ports**: 8000 (production), 8001 (development)
- **Features**: Auto-reload, API documentation, Pydantic validation

### Data Management
- **DuckDB**: Persistent analytics database
- **CSV Files**: Volume-mounted data sources
- **Hot Reload**: Development-time code synchronization

## Docker Compose Profiles

- **Production**: Optimized builds, standard ports (3000, 8000)
- **Development**: Hot reload enabled, alternate ports (3001, 8001)

## Network Architecture

All containers communicate through the `app-network` bridge network, enabling service discovery and secure inter-container communication.