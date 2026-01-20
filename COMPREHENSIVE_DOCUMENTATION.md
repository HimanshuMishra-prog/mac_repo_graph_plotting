# MAC Layer Log Visualization and Monitoring System
## Comprehensive Technical Documentation

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [Project Structure and File Descriptions](#project-structure-and-file-descriptions)
5. [Key Components](#key-components)
6. [Data Flow](#data-flow)
7. [Installation and Setup](#installation-and-setup)
8. [API Routes](#api-routes)
9. [Database Schema](#database-schema)
10. [Configuration](#configuration)

---

## Executive Summary

The MAC Layer Log Visualization and Monitoring System is a comprehensive enterprise-grade solution designed to ingest, parse, analyze, and visualize 4G LTE and 5G MAC (Medium Access Control) layer logs. The system provides real-time monitoring capabilities, historical log analysis, and performance insights through an interactive web-based interface powered by Grafana dashboards.

### Key Capabilities:
- **Log Ingestion**: Support for 4G LTE and 5G MAC layer logs
- **Real-time Visualization**: Interactive Grafana dashboards with time-series data
- **Performance Analysis**: Metrics-driven insights into MAC layer performance
- **User Management**: Multi-user support with role-based access control
- **Historical Data**: Complete audit trail and historical log storage
- **Scalable Architecture**: Docker-based containerization for easy deployment

---

## Technology Stack

### Backend Framework
- **Flask 3.0.3**: Lightweight Python web framework for REST API and web interface
- **Python 3.x**: Core programming language
- **SQLAlchemy 2.0.41**: ORM for database abstraction
- **Flask-Login 0.6.3**: User session and authentication management
- **Flask-Migrate 4.1.0**: Database migration management using Alembic
- **Flask-SQLAlchemy 3.1.1**: Flask integration for SQLAlchemy

### Monitoring and Metrics
- **Prometheus 0.19.0**: Metrics collection and time-series database
- **prometheus-flask-exporter 0.23.0**: Flask integration for Prometheus metrics export
- **Grafana**: Visualization and dashboarding platform (containerized)

### Log Aggregation
- **Loki**: Lightweight log aggregation system optimized for multi-tenancy and cost-effectiveness
- **Promtail**: Log shipper for collecting logs and pushing to Loki

### Infrastructure
- **Docker & Docker Compose**: Container orchestration and service management
- **SQLite**: Lightweight embedded database with WAL (Write-Ahead Logging) optimization
- **Nginx 1.25**: Reverse proxy and web server for request routing

### Supporting Libraries
- **Requests 2.32.4**: HTTP client library for external API calls
- **Jinja2 3.1.6**: Template engine for HTML rendering
- **WTForms 3.1.2**: Form validation and rendering
- **Werkzeug 3.0.6**: WSGI utilities and request/response handling
- **Tenacity 9.1.2**: Retry logic for resilient API calls
- **Alembic 1.16.1**: Database migration framework

---

## System Architecture

### High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│                   (Web Browser Interface)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      NGINX REVERSE PROXY (Port 8080)             │
│                  (Request Routing & Load Balancing)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ↓                ↓                ↓
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│  FLASK APP      │ │  PROMETHEUS  │ │   GRAFANA    │
│  (Port 5000)    │ │  (Port 9090) │ │  (Port 3000) │
│                 │ │              │ │              │
│ • User Auth     │ │ • Metrics DB │ │ • Dashboards │
│ • Log Upload    │ │ • Time-Series│ │ • Alerting   │
│ • Job Mgmt      │ │              │ │              │
│ • API Routes    │ │              │ │              │
│ • SSO Handler   │ │              │ │              │
└────────┬────────┘ └──────────────┘ └──────────────┘
         │
    ┌────┴────────────────┐
    │                     │
    ↓                     ↓
┌──────────────┐   ┌─────────────┐
│  SQLite DB   │   │    LOKI     │
│              │   │  (Port 3100)│
│ • Users      │   │             │
│ • Logs       │   │ • Log Store │
│ • Metadata   │   │ • Indexing  │
│              │   │             │
└──────────────┘   └─────────────┘
```

### Component Interactions

1. **User Authentication Flow**:
   - User logs in through web interface
   - Flask validates credentials against SQLite database
   - Session is created and managed via Flask-Login
   - Grafana SSO integration enables seamless Grafana access

2. **Log Processing Pipeline**:
   - User uploads MAC layer logs through web interface
   - Logs are persisted in uploads folder
   - Parser script processes raw logs into structured format
   - Parsed data is stored in both SQLite (metadata) and Loki (logs)
   - Metrics are exported to Prometheus via prometheus-client

3. **Visualization Layer**:
   - Grafana queries Prometheus for metrics
   - Grafana queries Loki for logs and traces
   - Dashboards display real-time MAC layer performance
   - Historical data available for trend analysis

4. **Data Flow**:
   - MAC Logs → Flask Upload → Parser → SQLite + Loki → Prometheus Metrics → Grafana Dashboards

---

## Project Structure and File Descriptions

### Root Directory

```
mac_log_grafana_loki/
```

#### **app.py**
- **Purpose**: Application entry point
- **Functionality**: 
  - Creates Flask application instance using factory pattern
  - Initializes all extensions and blueprints
  - Configures debug mode and host bindings
  - Serves on 0.0.0.0:5000 for containerized deployment
- **Key Code**:
  ```python
  from flaskr import create_app
  app = create_app()
  app.secret_key = 'anything'
  if __name__ == "__main__":
      app.run(host="0.0.0.0", debug=False)
  ```

#### **docker-compose.yml**
- **Purpose**: Orchestrate all containerized services
- **Services Defined**:
  - **Prometheus**: Metrics collection (port 9090)
  - **Grafana**: Visualization platform (port 3000)
  - **Loki**: Log aggregation system (port 3100)
  - **Nginx**: Reverse proxy (port 8080)
- **Network**: `atu_net` bridge network for inter-container communication
- **Volumes**: Persistent storage for database, logs, and Grafana configuration

#### **requirements.txt**
- **Purpose**: Python dependency specifications
- **Content**: Complete list of pip packages with pinned versions
- **Usage**: `pip install -r requirements.txt`

#### **grafana.env**
- **Purpose**: Environment variables for Grafana container
- **Configuration**: Authentication, plugin settings, admin credentials

#### **documentation.txt**
- **Purpose**: Legacy or supplementary documentation
- **Content**: Project-specific notes and setup instructions

#### **README.md**
- **Purpose**: Quick reference guide
- **Current Content**: Brief project description

---

### flaskr/ (Main Application Package)

#### **flaskr/__init__.py**
- **Purpose**: Flask application factory and initialization
- **Responsibilities**:
  - Creates Flask app instance with configuration
  - Initializes database (SQLite with SQLAlchemy)
  - Sets up Flask-Migrate for schema management
  - Configures Flask-Login for user session management
  - Initializes PrometheusMetrics for metrics collection
  - Registers all route blueprints
  - Optimizes SQLite with WAL mode, synchronous settings, and caching
- **Key Features**:
  - Implements `NoPrometheus` filter to exclude `/metrics` from logs
  - Configures database connection pooling and timeouts
  - Provides user loader for session authentication

#### **flaskr/config.py**
- **Purpose**: Centralized configuration management
- **Database Configuration**:
  ```
  SQLite with WAL (Write-Ahead Logging) enabled
  Connection timeout: 30 seconds
  Pool pre-ping to validate connections
  Cache size: 2000 pages (~8MB)
  Temporary store: In-memory
  ```
- **Grafana Integration**:
  - **GRAFANA_HOST**: Nginx reverse proxy URL
  - **GRAFANA_API_HOST**: Direct Grafana API endpoint
  - **GRAFANA_SERVICE_TOKEN**: API authentication token
  - **LOGIN_EXPIRY**: Extended session duration
  - **DASHBOARD_UID**: Default dashboard identifier
- **Loki Configuration**:
  - **REPLAY_BATCH_SIZE**: 1000 logs per batch
  - **REQUESTS_PER_SECOND**: Rate limiting (10 RPS)
  - **REPLAY_DELAY**: 0.001 second delay between requests
- **Security**:
  - Auth proxy secret for SSO integration

#### **flaskr/logger.py**
- **Purpose**: Centralized logging configuration
- **Functionality**:
  - Sets up application-wide logging infrastructure
  - Configures log levels, formatters, and handlers
  - Integrates with Flask's logger
  - Provides audit trail for application events
- **Usage**: Imported in `__init__.py` for initialization

---

### flaskr/db/ (Database Layer)

#### **flaskr/db/database.py**
- **Purpose**: Database connection and initialization
- **Responsibilities**:
  - Creates SQLAlchemy instance
  - Manages database engine configuration
  - Handles connection pooling
- **Key Function**:
  ```python
  def create_database():
      # Returns configured SQLAlchemy instance
  ```

#### **flaskr/db/models.py**
- **Purpose**: SQLAlchemy ORM models for data persistence
- **Models Defined**:

  **User Model**:
  - `id`: Primary key (Integer, auto-increment)
  - `username`: Unique username (String 250)
  - `password`: Hashed password (String 250)
  - **Purpose**: User account management and authentication
  - **Relationships**: Inherits from UserMixin for Flask-Login integration

  **Logs Model**:
  - `sno`: Serial number, primary key (Integer)
  - `username`: User who uploaded (String 250)
  - `filename`: Original log file name (String 50, indexed)
  - `time`: Timestamp of upload (String 100)
  - `filelocation`: Path to stored file (String 500)
  - **Constraints**: Unique constraint on (username, filename) pair
  - **Purpose**: Track all uploaded log files and metadata

  **Metadata Model**:
  - `sno`: Serial number, primary key (Integer)
  - `username`: User reference (String 250, indexed)
  - `filename`: Associated log file (String 50, indexed)
  - `parsing_tag`: Log type identifier (String 100)
  - `sector`: Cellular sector ID (Integer)
  - `ue_id`: User Equipment ID (Integer)
  - `malperforming`: Performance flag (Boolean)
  - `created_at`: Creation timestamp (DateTime)
  - **Purpose**: Store parsed log metadata for queries and analysis

#### **flaskr/db/database_functions.py**
- **Purpose**: Database operation abstractions
- **Key Functions**:
  - `register_logs()`: Create new log entry in database
  - `delete_logs()`: Remove log entries
  - `get_user_by_id()`: Retrieve user by ID for Flask-Login
  - `get_metadata()`: Query metadata for specific logs
  - `update_metadata()`: Update parsing results
- **Design Pattern**: DAO (Data Access Object) pattern for database isolation

---

### flaskr/routes/ (Application Routes)

#### **flaskr/routes/__init__.py**
- **Purpose**: Route blueprint aggregation and registration
- **Functionality**:
  - Imports all route blueprints
  - Aggregates them into `blueprints` list
  - Exported for registration in main app factory
- **Blueprints Registered**:
  - `analyze_bp`: Log analysis interface
  - `home_bp`: Home page
  - `jobs_bp`: Job management
  - `login_bp`: User login
  - `logout_bp`: User logout
  - `register_bp`: User registration
  - `grafana_sso`: Grafana single sign-on

#### **flaskr/routes/home_route.py**
- **Purpose**: Home page and dashboard entry point
- **Routes**:
  - `GET /`: Renders home page
- **Functionality**:
  - Displays welcome/dashboard
  - Provides navigation to other sections
  - May display summary statistics
- **Template**: `templates/Layout.html` (main layout wrapper)

#### **flaskr/routes/login_route.py**
- **Purpose**: User authentication and session management
- **Routes**:
  - `GET/POST /login`: Login form and validation
- **Functionality**:
  - Validates username/password credentials
  - Creates user session via Flask-Login
  - Redirects authenticated users to home
  - Redirects unauthenticated to login page
- **Template**: `templates/login.html`
- **Security**: Password validation and session management

#### **flaskr/routes/register_route.py**
- **Purpose**: New user account creation
- **Routes**:
  - `GET/POST /register`: Registration form and processing
- **Functionality**:
  - Validates user input and password requirements
  - Creates new user in database
  - Prevents duplicate usernames
  - Redirects to login on successful registration
- **Template**: `templates/sign_up.html`
- **Validation**: Username uniqueness, password strength

#### **flaskr/routes/logout_route.py**
- **Purpose**: User session termination
- **Routes**:
  - `GET /logout`: Logout action
- **Functionality**:
  - Terminates current user session
  - Clears session data
  - Redirects to login page
- **Decorator**: `@login_required` ensures only authenticated users can logout

#### **flaskr/routes/analyze_route.py**
- **Purpose**: Log file upload and analysis initiation
- **Routes**:
  - `GET /analyze`: Displays upload form
  - `POST /analyze`: Processes uploaded files
- **Functionality**:
  - Accepts multiple log files via form
  - Validates file uploads
  - Saves files to `uploads/` directory
  - Registers files in database via `Logs` model
  - Creates metadata entries for each upload
  - Redirects to jobs page for processing
- **File Handling**:
  - Supports batch uploads (multiple files)
  - Error handling for failed saves
  - File path storage in database
- **Template**: `templates/analyze.html`
- **Error Handling**: 
  - Invalid filename handling
  - File size validation
  - Rollback on save failure

#### **flaskr/routes/jobs_route.py**
- **Purpose**: Job queue and processing management
- **Routes**:
  - `GET /jobs`: Display job list and status
  - `POST /jobs/process`: Trigger log processing
- **Functionality**:
  - Lists all uploaded logs for current user
  - Initiates background processing jobs
  - Tracks job status and progress
  - Displays processing results
- **Integration**: 
  - Triggers parser for each job
  - Sends parsed data to Loki
  - Exports metrics to Prometheus
- **Template**: `templates/jobs.html`

#### **flaskr/routes/grafana_sso.py**
- **Purpose**: Grafana single sign-on (SSO) integration
- **Routes**:
  - `GET/POST /grafana-sso`: SSO handler
- **Functionality**:
  - Validates SSO token from Flask session
  - Creates Grafana session via API
  - Handles auth proxy flow
  - Manages user context transfer to Grafana
- **Security**:
  - Auth proxy secret validation
  - Token-based authentication
  - Session synchronization

---

### flaskr/scripts/ (Processing and Background Tasks)

#### **flaskr/scripts/parser.py**
- **Purpose**: Core MAC layer log parsing engine
- **Functionality**:
  - Uses regular expressions to parse 4G and 5G MAC logs
  - Supports multiple log formats:
    - DPP_BASIC (4G logs)
    - PB_BASIC (4G logs)
    - ULCA_PHR_PWR_AL (Power control logs)
    - UMRC_DP (Resource allocation)
    - URAC_RA (Random access)
    - SCELL_STATE (Secondary cell state)
    - PCELL_STATE_CHANGE (Primary cell transitions)
  - Extracts key fields:
    - Timestamp and slot information
    - Cell and UE identifiers
    - Performance metrics (CRC, throughput, etc.)
    - Resource allocation details
- **Processing**:
  - Cleans and validates extracted data
  - Converts raw values to usable formats
  - Handles malformed log lines gracefully
- **Output**: Structured JSON/CSV for storage
- **Performance**: Batch processing with configurable sizes
- **Metrics**: Tracks parsing statistics via Prometheus metrics

#### **flaskr/scripts/metrics.py**
- **Purpose**: Prometheus metrics definition and export
- **Metrics Exposed**:
  - `LOGS_PROCESSED`: Total logs parsed
  - `DPP_BASIC_LOGS_PROCESSED`: 4G basic metrics
  - `ULCA_PHR_PWR_AL_LOGS_PROCESSED`: Power control logs
  - `UMRC_DP_LOGS_PROCESSED`: Resource allocation
  - `URAC_RA_LOGS_PROCESSED`: Random access attempts
  - `TOTAL_CRC_FAILS`: CRC error count
  - `SCELL_STATE_ULCA_LOGS_PROCESSED`: Secondary cell metrics
  - `PCELL_STATE_CHANGE_LOGS_PROCESSED`: Cell state transitions
  - `PCELL_STATE_ULCA_LOGS_PROCESSED`: Primary cell state
  - `PCELL_STATE_ACT_LOGS_PROCESSED`: Cell activation events
- **Type**: Counter and histogram metrics
- **Usage**: Exported via `/metrics` endpoint
- **Integration**: prometheus-flask-exporter

#### **flaskr/scripts/replay_worker.py**
- **Purpose**: Background job worker for log replay and processing
- **Functionality**:
  - Retrieves queued jobs from database
  - Invokes parser for each job
  - Sends results to Loki for log storage
  - Updates job status (running, completed, failed)
  - Handles retries with exponential backoff (Tenacity)
- **Processing Pipeline**:
  1. Read log file from uploads directory
  2. Parse using regex patterns
  3. Enrich with metadata
  4. Push to Loki for indexing
  5. Export metrics to Prometheus
  6. Update database status
- **Error Handling**:
  - Graceful degradation on parse errors
  - Retry logic for transient failures
  - Error logging for debugging
- **Rate Limiting**: Respects LOKI_REQUESTS_PER_SECOND setting
- **Batch Processing**: Uses REPLAY_BATCH_SIZE for efficient processing

#### **flaskr/scripts/grafana_session_management.py**
- **Purpose**: Grafana API interaction and session management
- **Functionality**:
  - Authenticates with Grafana API using service token
  - Creates/manages user sessions in Grafana
  - Handles organization and team management
  - Manages dashboard access and permissions
  - Syncs user roles between Flask and Grafana
- **API Methods**:
  - `create_grafana_session()`: Create new authenticated session
  - `get_grafana_user()`: Retrieve user information
  - `update_grafana_permissions()`: Manage access control
  - `manage_dashboard_access()`: Grant dashboard permissions
- **Error Handling**: 
  - Connection retry with Tenacity
  - Token refresh on expiration
  - Fallback mechanisms
- **Configuration**: Uses settings from `config.py`

---

### flaskr/templates/ (Web Interface)

#### **Layout.html**
- **Purpose**: Base HTML template for consistent page layout
- **Components**:
  - Navigation header with logo
  - User menu and logout button
  - Content area placeholder
  - Footer with links
  - CSS/JS asset inclusion
- **Inheritance**: Extended by all page templates using Jinja2 `{% block %}` syntax
- **Styling**: Bootstrap or custom CSS framework

#### **login.html**
- **Purpose**: User login page
- **Form Fields**:
  - Username input
  - Password input
  - Remember me checkbox
  - Submit button
  - Link to registration page
- **Features**:
  - Client-side validation
  - Error message display
  - Responsive design

#### **sign_up.html**
- **Purpose**: User registration page
- **Form Fields**:
  - Username input with validation
  - Password input with strength indicator
  - Confirm password field
  - Email (optional)
  - Terms acceptance checkbox
  - Submit button
- **Features**:
  - Password strength feedback
  - Duplicate username detection
  - Success/error notifications

#### **analyze.html**
- **Purpose**: Log file upload interface
- **Components**:
  - File input with drag-and-drop support
  - File list preview
  - Analysis type selector (4G/5G)
  - Upload progress indicator
  - Submit button
- **Features**:
  - Multiple file selection
  - File validation (size, type)
  - Progress tracking
  - Error handling and user feedback

#### **jobs.html**
- **Purpose**: Job queue and processing status dashboard
- **Components**:
  - List of uploaded files
  - Processing status for each file
  - Progress bars and completion indicators
  - Action buttons (process, view results, delete)
  - Sorting and filtering options
- **Features**:
  - Real-time status updates via polling/WebSocket
  - Job history view
  - Result downloading
  - Job cancellation

#### **grafana_open.html**
- **Purpose**: Iframe container for embedding Grafana dashboards
- **Functionality**:
  - Embeds Grafana dashboard in Flask page
  - Handles SSO context transfer
  - Provides seamless navigation between Flask and Grafana
- **Components**:
  - Grafana iframe with responsive sizing
  - Loading indicators
  - Error handling for connectivity issues

---

### flaskr/static/ (Front-end Assets)

#### **flaskr/static/css/login_style.css**
- **Purpose**: Styling for login and registration pages
- **Features**:
  - Responsive form layout
  - Input field styling
  - Button animations
  - Color scheme and branding
  - Mobile optimization

#### **flaskr/static/css/toast_style.css**
- **Purpose**: Toast notification styling
- **Components**:
  - Success notification styles
  - Error notification styles
  - Warning and info styles
  - Animation effects (fade in/out, slide)
  - Positioning and sizing

#### **flaskr/static/js/script.js**
- **Purpose**: Main application JavaScript for interactivity
- **Functionality**:
  - Form validation and submission
  - File upload handling
  - Drag-and-drop support
  - Status polling for job updates
  - Navigation and routing
  - Error handling

#### **flaskr/static/js/toast_msg.js**
- **Purpose**: Toast notification system
- **Functions**:
  - `showToast(message, type)`: Display notification
  - Auto-dismiss after timeout
  - Multiple toast queue handling
  - Message stacking
- **Usage**: Called from backend flash messages

---

### grafana_data/ (Grafana Persistent Storage)

#### **grafana_data/plugins/**
- **Purpose**: Grafana plugin directory
- **Plugins Included**:
  - **grafana-exploretraces-app**: Distributed trace visualization
  - **grafana-lokiexplore-app**: Loki log exploration interface
  - **grafana-metricsdrilldown-app**: Drill-down analysis for metrics
  - **grafana-pyroscope-app**: Continuous profiling integration
- **Structure**: Each plugin has compiled assets, README, LICENSE, and configuration

#### **grafana_data/csv/, pdf/, png/**
- **Purpose**: Export storage for dashboards
- **Usage**: Stores exported reports and visualizations

---

### loki-config/ (Loki Configuration)

#### **loki-config/config.yml**
- **Purpose**: Loki service configuration
- **Key Sections**:
  - `auth_enabled`: Security settings
  - `ingester`: Log ingestion configuration
  - `storage_config`: Backend storage configuration (BoltDB, filesystem)
  - `schema_config`: Index schema definition
  - `chunk_retention_period`: Data retention policy
  - `table_manager`: Index lifecycle management
  - `query_range`: Query performance settings
- **Storage Backend**: BoltDB with filesystem for log chunks
- **Indexing**: Custom schema for log query optimization

---

### prometheus-config/ (Prometheus Configuration)

#### **prometheus-config/prometheus.yml**
- **Purpose**: Prometheus scrape configuration
- **Targets**:
  - Flask app metrics endpoint (`/metrics`)
  - Prometheus self-monitoring
  - Grafana metrics (if exposed)
- **Scrape Intervals**: Configurable (default typically 15s)
- **Retention Policy**: Data retention duration settings

---

### migrations/ (Database Migration Scripts)

#### **migrations/alembic.ini**
- **Purpose**: Alembic configuration file
- **Settings**: SQL dialect, logging, script location

#### **migrations/env.py**
- **Purpose**: Alembic environment setup
- **Functionality**: Auto migration script generation

#### **migrations/script.py.mako**
- **Purpose**: Template for generated migration files

---

### nginx/ (Reverse Proxy Configuration)

#### **nginx/nginx.conf**
- **Purpose**: Nginx reverse proxy configuration
- **Functions**:
  - Routes traffic from port 8080 to Grafana (port 3000)
  - Handles CORS headers
  - Request buffering and compression
  - Load balancing (if multiple backends)

---

### instance/ (Flask Instance Data)

#### **instance/default.db**
- **Purpose**: SQLite database file
- **Contents**: User accounts, log metadata, job status
- **Location**: Generated on first run
- **Backup**: Should be regularly backed up for production

---

## Key Components

### Authentication System
- **Framework**: Flask-Login
- **Storage**: SQLite User table
- **Session Duration**: Configured in `config.py` (GRAFANA_LOGIN_EXPIRY)
- **Features**:
  - User registration and login
  - Password storage (implementation-dependent, should be hashed)
  - Session management
  - Grafana SSO integration

### Log Processing Pipeline
1. **Upload**: User uploads logs via web interface
2. **Validation**: File size, format, and duplicate checks
3. **Storage**: Files saved to `uploads/` directory
4. **Registration**: Log metadata stored in SQLite
5. **Parsing**: Background worker processes logs
6. **Enrichment**: Metadata extraction (sector, UE ID, etc.)
7. **Storage**: Parsed logs indexed in Loki
8. **Metrics**: Performance metrics exported to Prometheus
9. **Visualization**: Grafana queries and displays data

### Metrics Export
- **Framework**: prometheus-client via prometheus-flask-exporter
- **Endpoint**: `/metrics`
- **Metrics Types**:
  - Counters: Cumulative metrics (logs processed, errors)
  - Histograms: Distribution metrics (processing time)
- **Labels**: Organized by log type and parsing tag
- **Scrape Integration**: Prometheus periodically collects metrics

### Dashboard Management
- **Platform**: Grafana 3000
- **Data Sources**:
  - Prometheus: Metrics queries
  - Loki: Log queries and traces
- **Dashboard UID**: `07102025-srib-mac-default` (configurable)
- **Refresh Rate**: Real-time or configurable intervals

---

## Data Flow

### End-to-End Log Processing Flow

```
┌──────────────────┐
│  User Uploads    │
│  MAC Layer Logs  │
└────────┬─────────┘
         │
         ↓
┌──────────────────────────────┐
│  Flask Analyze Route         │
│  • Validates file            │
│  • Saves to uploads/         │
│  • Creates Logs entry (DB)   │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│  Replay Worker Job Queue     │
│  • Retrieves log file        │
│  • Invokes parser.py         │
└────────┬─────────────────────┘
         │
         ↓
┌──────────────────────────────┐
│  Parser.py (Regex Engine)    │
│  • Matches log patterns      │
│  • Extracts fields           │
│  • Creates structured JSON   │
└────────┬─────────────────────┘
         │
    ┌────┴─────────────┐
    │                  │
    ↓                  ↓
┌──────────────┐  ┌──────────────────┐
│  Loki Push   │  │  Metrics Export  │
│  • Index     │  │  • Increment     │
│  • Store     │  │    counters      │
│  • Query     │  │  • Record time   │
└──────────────┘  │    series        │
    │             └──────────────────┘
    │                    │
    └────────┬───────────┘
             │
             ↓
        ┌──────────────────────────────┐
        │  Metadata Store (SQLite)     │
        │  • Update Metadata entry     │
        │  • Store parsing_tag         │
        │  • Set malperforming flag    │
        └────────┬─────────────────────┘
                 │
        ┌────────┴──────────┐
        │                   │
        ↓                   ↓
   ┌──────────┐      ┌─────────────────┐
   │ Grafana  │      │  Prometheus     │
   │ Loki     │      │  (Metrics DB)   │
   │ Queries  │      └─────────────────┘
   └──────────┘             │
        │                   ↓
        │          ┌─────────────────┐
        └─────────→│  Grafana Charts │
                   │  & Dashboards   │
                   └─────────────────┘
```

### Query Path for Visualization

```
User Browser
    │
    ↓
Grafana Dashboard (Port 3000)
    │
    ├─→ Prometheus Query (Metrics)
    │   └─→ Flask /metrics endpoint
    │
    ├─→ Loki Query (Logs)
    │   └─→ Loki API (Port 3100)
    │
    └─→ Display Panels
        • Time-series graphs
        • Heatmaps
        • Tables
        • Stat cards
```

---

## Installation and Setup

### Prerequisites
- Docker and Docker Compose installed
- Python 3.8+ (for local development)
- 4GB+ RAM, 10GB+ storage recommended

### Deployment via Docker Compose

```bash
# Navigate to project directory
cd mac_log_grafana_loki-main

# Build and start all services
docker-compose up -d

# Services will be available at:
# Flask App: http://localhost:8080
# Grafana: http://localhost:3000 (default admin/admin)
# Prometheus: http://localhost:9090
# Loki: http://localhost:3100
```

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Run application
python app.py

# Application available at http://localhost:5000
```

### Database Initialization
```bash
# Create tables from models
flask db upgrade

# Create initial admin user (manual or via registration page)
```

### Configuration for Production
1. Update `config.py`:
   - Change `secret_key` from 'anything' to secure random value
   - Update `GRAFANA_SERVICE_TOKEN` with actual token
   - Update database URIs if using PostgreSQL/MySQL
   - Update Loki settings for retention policy

2. Set environment variables for sensitive data:
   ```bash
   export FLASK_SECRET_KEY="secure-random-key"
   export GRAFANA_ADMIN_PASSWORD="secure-password"
   export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
   ```

3. Configure SSL/TLS in Nginx configuration

4. Set up regular backups for SQLite database

---

## API Routes

### Authentication Routes
- **POST /login** - User login with credentials
- **POST /register** - New user registration
- **GET /logout** - User logout (requires login)

### Content Routes
- **GET /** - Home/dashboard page
- **GET /analyze** - Upload logs page
- **POST /analyze** - Process uploaded logs
- **GET /jobs** - View processing jobs
- **POST /jobs/process** - Trigger job processing

### Metrics & Monitoring
- **GET /metrics** - Prometheus metrics endpoint (for scraping)

### Grafana Integration
- **GET/POST /grafana-sso** - Grafana single sign-on handler

### Data Formats
All POST requests expect form-data (file uploads) or JSON
All responses are HTML (web) or JSON (API)

---

## Database Schema

### Users Table (User Model)
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);
```

### Logs Table
```sql
CREATE TABLE logs (
    sno INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(250) NOT NULL,
    filename VARCHAR(50) NOT NULL,
    time VARCHAR(100),
    filelocation VARCHAR(500) NOT NULL,
    UNIQUE(username, filename)
);
```

### Metadata Table
```sql
CREATE TABLE metadata (
    sno INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(250) NOT NULL,
    filename VARCHAR(50) NOT NULL,
    parsing_tag VARCHAR(100) NOT NULL,
    sector INTEGER,
    ue_id INTEGER,
    malperforming BOOLEAN,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
- `username` on Metadata table (for user queries)
- `filename` on Logs and Metadata tables (for log lookup)

---

## Configuration

### Environment Variables
```bash
FLASK_ENV=production              # development or production
FLASK_SECRET_KEY=<secure-key>    # Session encryption
DATABASE_URL=<db-connection>     # Database connection string
GRAFANA_HOST=http://localhost:8080
GRAFANA_API_HOST=http://localhost:3000
GRAFANA_SERVICE_TOKEN=<token>    # API authentication
LOKI_HOST=http://localhost:3100  # Loki endpoint
PROMETHEUS_HOST=http://localhost:9090
```

### Application Settings (config.py)
- SQLite WAL mode enabled for better concurrency
- Connection timeout: 30 seconds
- Pool pre-ping: Validates connections before use
- Cache size: 2000 pages (~8MB)
- Log replay batch size: 1000 logs
- Loki rate limit: 10 requests/second

### Grafana Configuration (grafana.env)
- Default admin credentials: admin/admin (change in production)
- Installed plugins: Loki Explore, Pyroscope, Trace Exploration, Metrics Drill-down
- Data sources pre-configured for Prometheus and Loki

---

## Performance Considerations

### Database Optimization
- WAL mode reduces lock contention in SQLite
- Connection pooling with pre-ping validation
- Indexed queries on username and filename
- Careful batch size tuning for log processing

### Log Processing
- Batch processing (1000 logs per batch) reduces API calls
- Rate limiting (10 RPS) prevents overwhelming Loki
- Configurable replay delay (0.001s) for backpressure handling

### Metrics Collection
- `/metrics` endpoint filtered from logging to reduce noise
- Prometheus scrape interval configurable (default ~15s)
- Metrics exported as counters and histograms for efficiency

### Monitoring Best Practices
1. Set up alerting rules in Prometheus for:
   - High error rates
   - Processing delays
   - Database connection issues

2. Monitor Grafana logs for SSO/authentication errors

3. Track Loki ingestion rate and storage usage

4. Monitor Flask app memory and CPU usage

---

## Troubleshooting

### Common Issues

**Issue**: Port conflicts on startup
- **Solution**: Check for existing services on 3000, 3100, 8080, 9090
- **Resolution**: `docker-compose down` and retry

**Issue**: Database locked errors
- **Solution**: WAL mode corruption or SQLite lock timeout
- **Resolution**: Delete `instance/default.db` and reinitialize (loses data!)

**Issue**: Logs not appearing in Grafana
- **Solution**: Verify Loki datasource connection
- **Resolution**: Check Loki logs, verify network connectivity

**Issue**: Metrics not updating
- **Solution**: Prometheus scrape configuration
- **Resolution**: Verify `/metrics` endpoint accessibility

**Issue**: Grafana SSO not working
- **Solution**: Token validation or session mismatch
- **Resolution**: Update `GRAFANA_SERVICE_TOKEN`, verify auth proxy secret

---

## Security Recommendations

1. **Change default credentials**: Update Grafana and Flask passwords immediately

2. **Use HTTPS**: Implement TLS certificates for production

3. **Password hashing**: Ensure passwords are hashed with bcrypt or similar

4. **API token rotation**: Rotate Grafana service token regularly

5. **Network isolation**: Run services in private network, expose only Nginx

6. **Database backups**: Implement automated backup strategy

7. **Log retention**: Configure appropriate retention policies in Loki

8. **Access control**: Implement role-based access control for sensitive operations

---

## Conclusion

This MAC Layer Log Visualization and Monitoring System provides a comprehensive platform for analyzing and visualizing 4G LTE and 5G MAC layer performance. By combining Flask's flexibility, Loki's log aggregation capabilities, Prometheus's metrics collection, and Grafana's visualization prowess, the system delivers real-time insights into cellular network performance.

The modular architecture allows for easy extension with additional log types, custom parsing logic, and enhanced analytics capabilities. Docker-based deployment ensures consistency across environments and simplifies operations.

For questions or issues, refer to the code comments and inline documentation within each module.

---

**Document Version**: 1.0
**Last Updated**: January 2026
**Project**: MAC Layer Log Grafana Loki Monitoring System
