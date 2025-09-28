# System Architecture

This diagram shows the high-level system architecture of the DuckDB Analytics Platform, including the user types, application layers, and infrastructure components.

```mermaid
graph TB
    subgraph "Users"
        U1[Data Analyst]
        U2[Business User]
        U3[Developer]
    end

    subgraph "Frontend Layer"
        UI[Next.js Dashboard<br/>React 19 + TypeScript]
        UI --> |Real-time Updates| Chart[Interactive Charts]
        UI --> |User Actions| Filter[Time Filters]
    end

    subgraph "API Layer"
        API[FastAPI Backend<br/>Python 3.11+]
        API --> |Auto Documentation| Docs[Swagger UI]
        API --> |Data Validation| Models[Pydantic Models]
    end

    subgraph "Data Layer"
        DB[(DuckDB<br/>Analytics Database)]
        CSV[CSV Files<br/>Raw Data]
        CSV --> |ETL Process| DB
    end

    subgraph "Infrastructure"
        Docker[Docker Containers]
        CI[GitHub Actions<br/>CI/CD Pipeline]
        GCP[Google Cloud<br/>Artifact Registry]
    end

    %% User Interactions
    U1 --> UI
    U2 --> UI
    U3 --> API

    %% Data Flow
    UI --> |HTTP Requests| API
    API --> |SQL Queries| DB
    
    %% Infrastructure Flow
    Docker --> |Container Images| GCP
    CI --> |Build & Deploy| Docker

    %% Styling
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef data fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef infra fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef users fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class UI,Chart,Filter frontend
    class API,Docs,Models backend
    class DB,CSV data
    class Docker,CI,GCP infra
    class U1,U2,U3 users
```

## Key Components

- **Users**: Different user types with specific needs and access patterns
- **Frontend**: Modern React-based dashboard with real-time capabilities
- **Backend**: FastAPI providing RESTful endpoints with automatic documentation
- **Data**: DuckDB for analytics with CSV data ingestion pipeline
- **Infrastructure**: Containerized deployment with CI/CD automation