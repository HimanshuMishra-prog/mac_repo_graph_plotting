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

\\\

                        CLIENT LAYER                              
                   (Web Browser Interface)                         

                         
                          HTTP/HTTPS
                         

                      NGINX REVERSE PROXY (Port 8080)             
                  (Request Routing & Load Balancing)              

                         
        
                                        
                                        
  
  FLASK APP         PROMETHEUS      GRAFANA    
  (Port 5000)       (Port 9090)    (Port 3000) 
                                               
  User Auth        Metrics DB    Dashboards 
  Log Upload       Time-Series   Alerting   
  Job Mgmt                                    
  API Routes                                  
  SSO Handler                                 
  
         
    
                         
                         
   
  SQLite DB          LOKI     
                   (Port 3100)
  Users                      
  Logs            Log Store 
  Metadata        Indexing  
                              
   
\\\

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
   - MAC Logs  Flask Upload  Parser  SQLite + Loki  Prometheus Metrics  Grafana Dashboards

---

## Project Structure and File Descriptions

### Root Directory Files

#### **app.py**
- **Purpose**: Application entry point
- **Functionality**: Creates Flask application instance using factory pattern, initializes all extensions and blueprints
- **Usage**: \python app.py\ to start server

#### **docker-compose.yml**
- **Purpose**: Orchestrates all containerized services
- **Services**: Prometheus, Grafana, Loki, Nginx
- **Network**: atu_net bridge network for service communication

#### **requirements.txt**
- **Purpose**: Python package dependencies
- **Installation**: \pip install -r requirements.txt\

#### **README.md**
- **Purpose**: Project overview and quick reference

---

## Folder Structure and Descriptions

### **flaskr/** (Main Application Package)

#### **flaskr/__init__.py**
- Creates Flask app with factory pattern
- Initializes database (SQLite with SQLAlchemy)
- Sets up Flask-Login for authentication
- Configures PrometheusMetrics for monitoring
- Optimizes SQLite with WAL mode, synchronous settings, and caching
- Registers all route blueprints

#### **flaskr/config.py**
- Centralized configuration management
- **Database**: SQLite with WAL enabled, 30s timeout, 2000 page cache
- **Grafana**: API endpoints, service token, dashboard UID, session expiry
- **Loki**: Batch size (1000), rate limiting (10 RPS), replay delay (0.001s)
- **Security**: Auth proxy secret for SSO

#### **flaskr/logger.py**
- Application-wide logging infrastructure
- Provides audit trail for system events

---

### **flaskr/db/** (Database Layer)

#### **flaskr/db/database.py**
- Creates and configures SQLAlchemy database instance
- Manages connection pooling and engine configuration

#### **flaskr/db/models.py**
Defines three main database models:

**User Model**:
- id (Primary Key)
- username (Unique)
- password (Hashed)
- Inherits from UserMixin for Flask-Login

**Logs Model**:
- sno (Primary Key, auto-increment)
- username (Upload owner)
- filename (Log file name, indexed)
- time (Upload timestamp)
- filelocation (File storage path)
- Unique constraint on (username, filename)

**Metadata Model**:
- sno (Primary Key)
- username (indexed)
- filename (indexed)
- parsing_tag (Log type identifier)
- sector (Cellular sector)
- ue_id (User Equipment ID)
- malperforming (Performance flag)
- created_at (Timestamp)

#### **flaskr/db/database_functions.py**
Database operation abstractions (DAO pattern):
- register_logs() - Create log entries
- delete_logs() - Remove log entries
- get_user_by_id() - User lookup
- get_metadata() - Query log metadata
- update_metadata() - Update parsing results

---

### **flaskr/routes/** (API Routes)

#### **flaskr/routes/__init__.py**
- Imports and aggregates all route blueprints
- Exports blueprints list for main app registration

#### **flaskr/routes/home_route.py**
- GET / - Home page and dashboard
- Displays welcome and summary statistics

#### **flaskr/routes/login_route.py**
- GET/POST /login - User authentication
- Validates credentials and manages sessions
- Template: login.html

#### **flaskr/routes/register_route.py**
- GET/POST /register - New user registration
- Username uniqueness validation
- Password requirement checking
- Template: sign_up.html

#### **flaskr/routes/logout_route.py**
- GET /logout - Session termination
- Requires authentication (@login_required)

#### **flaskr/routes/analyze_route.py**
- GET /analyze - Upload form display
- POST /analyze - Process file uploads
- Accepts multiple files, validates, saves to uploads/
- Creates Logs and Metadata entries
- Error handling with rollback support
- Template: analyze.html

#### **flaskr/routes/jobs_route.py**
- GET /jobs - Display job queue and status
- POST /jobs/process - Trigger log processing
- Shows processing status and results
- Integration with parser and Loki
- Template: jobs.html

#### **flaskr/routes/grafana_sso.py**
- GET/POST /grafana-sso - Grafana single sign-on
- Validates SSO tokens from Flask session
- Creates Grafana sessions via API
- Manages auth proxy flow

---

### **flaskr/scripts/** (Processing and Background Tasks)

#### **flaskr/scripts/parser.py**
Core MAC layer log parsing engine:
- Uses regex patterns to parse 4G and 5G MAC logs
- Supported log types:
  - DPP_BASIC (4G basic metrics)
  - PB_BASIC (4G physical layer)
  - ULCA_PHR_PWR_AL (Power control)
  - UMRC_DP (Resource allocation)
  - URAC_RA (Random access)
  - SCELL_STATE (Secondary cell)
  - PCELL_STATE_CHANGE (Primary cell transitions)
- Extracts: timestamp, slot, cell ID, UE ID, performance metrics, CRC status
- Handles malformed logs gracefully
- Output: Structured JSON/CSV data

#### **flaskr/scripts/metrics.py**
Prometheus metrics definitions:
- LOGS_PROCESSED - Total logs parsed
- DPP_BASIC_LOGS_PROCESSED - 4G basic metrics
- ULCA_PHR_PWR_AL_LOGS_PROCESSED - Power control
- UMRC_DP_LOGS_PROCESSED - Resource allocation
- URAC_RA_LOGS_PROCESSED - Random access
- TOTAL_CRC_FAILS - CRC error count
- SCELL_STATE_ULCA_LOGS_PROCESSED - Secondary cell
- PCELL_STATE_CHANGE_LOGS_PROCESSED - Cell transitions
- PCELL_STATE_ULCA_LOGS_PROCESSED - Primary cell state
- PCELL_STATE_ACT_LOGS_PROCESSED - Cell activation
- Exported via /metrics endpoint

#### **flaskr/scripts/replay_worker.py**
Background job processing:
- Retrieves queued jobs from database
- Invokes parser for each job
- Sends results to Loki for storage
- Updates job status (running, completed, failed)
- Retry logic with exponential backoff (Tenacity)
- Rate limiting (respects LOKI_REQUESTS_PER_SECOND)
- Batch processing with REPLAY_BATCH_SIZE

#### **flaskr/scripts/grafana_session_management.py**
Grafana API interaction:
- Authenticates using service token
- Creates/manages user sessions in Grafana
- Handles organization and team management
- Manages dashboard access and permissions
- Syncs user roles between Flask and Grafana
- Error handling and token refresh on expiration

---

### **flaskr/templates/** (Web Interface)

#### **Layout.html**
- Base HTML template for consistent layout
- Navigation header, user menu, content area
- Includes CSS/JS assets
- Extended by all page templates

#### **login.html**
- User login form
- Username and password inputs
- Remember me option
- Link to registration page

#### **sign_up.html**
- User registration form
- Username with validation
- Password strength feedback
- Confirm password field
- Terms acceptance checkbox

#### **analyze.html**
- Log file upload interface
- Drag-and-drop support
- Multiple file selection
- Analysis type selector (4G/5G)
- Upload progress indicator

#### **jobs.html**
- Job queue and status dashboard
- Uploaded file list
- Processing status for each file
- Progress bars and completion indicators
- Action buttons (process, view, delete)

#### **grafana_open.html**
- Grafana dashboard embedding
- Iframe container with SSO context
- Loading indicators and error handling

---

### **flaskr/static/** (Front-end Assets)

#### **css/login_style.css**
- Styling for login and registration forms
- Input field styling, button animations
- Responsive mobile optimization

#### **css/toast_style.css**
- Toast notification styling
- Success, error, warning, info styles
- Fade in/out and slide animations

#### **js/script.js**
- Main application interactivity
- Form validation and submission
- File upload and drag-and-drop handling
- Status polling for job updates
- Error handling and navigation

#### **js/toast_msg.js**
- Toast notification system
- showToast(message, type) function
- Auto-dismiss with timeout
- Message stacking capability

---

### **grafana_data/** (Grafana Persistent Storage)

#### **grafana_data/plugins/**
- grafana-exploretraces-app - Distributed trace visualization
- grafana-lokiexplore-app - Loki log exploration interface
- grafana-metricsdrilldown-app - Metrics drill-down analysis
- grafana-pyroscope-app - Continuous profiling integration

#### **grafana_data/csv/, pdf/, png/**
- Export storage for dashboard reports and visualizations

---

### **loki-config/** (Loki Configuration)

#### **loki-config/config.yml**
- Loki service configuration
- Auth settings, ingester configuration
- Storage backend (BoltDB, filesystem)
- Index schema and query optimization
- Data retention policies

---

### **prometheus-config/** (Prometheus Configuration)

#### **prometheus-config/prometheus.yml**
- Scrape configuration for Flask /metrics endpoint
- Prometheus self-monitoring
- Scrape intervals and retention policies

---

### **migrations/** (Database Migrations)

#### **alembic.ini, env.py, script.py.mako**
- Alembic framework for database schema management
- Auto-generates migration scripts
- Enables version control of database changes

---

### **nginx/** (Reverse Proxy Configuration)

#### **nginx/nginx.conf**
- Routes traffic from port 8080 to Grafana (3000)
- Handles CORS headers
- Request buffering and compression

---

## Data Flow

### Log Processing Pipeline
1. **Upload**: User uploads logs via web interface
2. **Validation**: File format, size, duplicate checks
3. **Storage**: Files saved to uploads/ directory
4. **Registration**: Metadata stored in SQLite Logs table
5. **Parsing**: Background worker processes logs with regex engine
6. **Enrichment**: Metadata extraction (sector, UE ID, performance flags)
7. **Loki Push**: Indexed logs stored in Loki
8. **Metrics Export**: Performance metrics exported to Prometheus
9. **Visualization**: Grafana queries and displays data in dashboards

---

## Installation and Setup

### Docker Deployment
\\\ash
cd mac_log_grafana_loki-main
docker-compose up -d

# Services available at:
# Flask: http://localhost:8080
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# Loki: http://localhost:3100
\\\

### Local Development
\\\ash
python -m venv venv
# Windows: venv\\Scripts\\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
python app.py
# Available at http://localhost:5000
\\\

---

## Database Schema

### Users Table
\\\sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);
\\\

### Logs Table
\\\sql
CREATE TABLE logs (
    sno INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(250) NOT NULL,
    filename VARCHAR(50) NOT NULL,
    time VARCHAR(100),
    filelocation VARCHAR(500) NOT NULL,
    UNIQUE(username, filename)
);
\\\

### Metadata Table
\\\sql
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
\\\

---

## Key Features

### Real-time Monitoring
- Prometheus metrics updated on each parse
- Grafana dashboards refresh at configured intervals
- WebSocket support for live updates (if implemented)

### Multi-user Support
- Isolated user sessions via Flask-Login
- Per-user log storage and metadata
- Role-based Grafana access

### Scalable Log Processing
- Batch processing (1000 logs per batch)
- Rate limiting (10 requests/second to Loki)
- Configurable replay delay for backpressure

### Log Retention
- Configurable retention in Loki
- SQLite metadata for historical queries
- Export capabilities (CSV, PDF, PNG)

---

**Document Version**: 1.0
**Last Updated**: January 2026
