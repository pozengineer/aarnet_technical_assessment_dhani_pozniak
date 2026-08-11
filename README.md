# Network Topology Tracing API

A headless Django REST Framework API for tracking network infrastructure components and the physical or logical connections between them.

## Features

- **CRUD Operations**: Full REST API endpoints for Sites, Devices, Interfaces, and Connections
- **Connection Tracing**: Specialized endpoint to trace all connections through specific infrastructure elements (site, device, or interface)
- **Database Normalization**: Properly normalized relational schema with appropriate constraints and validations
- **Django Admin**: Built-in admin interface for management
- **Docker Support**: Complete Docker and docker-compose configuration for containerized deployment
- **PostgreSQL**: Production-ready database configuration

## Project Structure

```
.
├── network_topology/          # Django project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # URL routing
│   ├── wsgi.py                # WSGI application
│   └── __init__.py
├── topology/                  # Main Django app
│   ├── models.py              # Database models (Site, Device, Interface, Connection)
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # ViewSets and custom views (including TraceConnectionsView)
│   ├── admin.py               # Django admin configuration
│   ├── apps.py                # App configuration
│   └── __init__.py
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image configuration
├── docker-compose.yml         # Docker Compose orchestration
├── .dockerignore              # Docker ignore file
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Data Model

### Site
- `name` (String, unique) - Site identifier
- `description` (Text, optional) - Site description
- `status` (String) - One of: Active, Planned, Decommissioned
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

### Device
- `name` (String, unique) - Device identifier
- `site` (ForeignKey) - Reference to Site
- `serial_number` (String, unique) - Device serial number
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

### Interface
- `name` (String) - Interface identifier (e.g., GigabitEthernet0/1)
- `device` (ForeignKey) - Reference to Device
- `speed` (Integer) - Interface speed in Mbps
- `status` (String) - One of: Up, Down, Maintenance
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp
- **Constraint**: Unique combination of name + device

### Connection
- `connection_id` (String, unique) - Alphanumeric identifier
- `name` (String, optional) - Connection description
- `status` (String) - One of: Connected, Disconnected
- `start_interface` (ForeignKey) - Reference to starting Interface
- `end_interface` (ForeignKey) - Reference to ending Interface
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp

## API Endpoints

### CRUD Operations

All endpoints support standard HTTP methods:

#### Sites
- `GET /api/sites/` - List all sites
- `POST /api/sites/` - Create a new site
- `GET /api/sites/{id}/` - Retrieve a specific site
- `PUT /api/sites/{id}/` - Update a site
- `DELETE /api/sites/{id}/` - Delete a site

#### Devices
- `GET /api/devices/` - List all devices
- `POST /api/devices/` - Create a new device
- `GET /api/devices/{id}/` - Retrieve a specific device
- `PUT /api/devices/{id}/` - Update a device
- `DELETE /api/devices/{id}/` - Delete a device

#### Interfaces
- `GET /api/interfaces/` - List all interfaces
- `POST /api/interfaces/` - Create a new interface
- `GET /api/interfaces/{id}/` - Retrieve a specific interface
- `PUT /api/interfaces/{id}/` - Update an interface
- `DELETE /api/interfaces/{id}/` - Delete an interface

#### Connections
- `GET /api/connections/` - List all connections
- `POST /api/connections/` - Create a new connection
- `GET /api/connections/{id}/` - Retrieve a specific connection
- `PUT /api/connections/{id}/` - Update a connection
- `DELETE /api/connections/{id}/` - Delete a connection

### Connection Tracing Endpoint

**Endpoint**: `GET /api/trace/?type={type}&id={id}`

**Parameters**:
- `type` (required): One of `site`, `device`, or `interface`
- `id` (required): The integer ID of the element

**Tracing Logic**:

1. **Interface**: Returns all connections where the interface is either the start or end node
2. **Device**: Returns all connections directly tied to the device, plus all connections associated with any interface belonging to that device
3. **Site**: Returns all connections tied to the site, including all connections associated with any device or interface within the site

**Example Request**:
```
GET /api/trace/?type=device&id=2
```

**Example Response**:
```json
{
  "traced_object": {
    "type": "device",
    "id": 2,
    "name": "Core-Switch-02",
    "site": {
      "id": 1,
      "name": "London Data Center"
    }
  },
  "connections_count": 2,
  "connections": [
    {
      "id": 12,
      "connection_id": "CONN-1002",
      "name": "Core Switch Uplink",
      "status": "Connected",
      "start_interface": 4,
      "start_target": {
        "site": { "id": 1, "name": "London Data Center" },
        "device": { "id": 1, "name": "London-Router-01" },
        "interface": { "id": 4, "name": "GigabitEthernet0/1" }
      },
      "end_interface": 9,
      "end_target": {
        "site": { "id": 1, "name": "London Data Center" },
        "device": { "id": 2, "name": "Core-Switch-02" },
        "interface": { "id": 9, "name": "GigabitEthernet0/24" }
      }
    }
  ]
}
```

## API Documentation

The API provides interactive documentation endpoints powered by [drf-spectacular](https://drf-spectacular.readthedocs.io/):

- **Swagger UI**: `http://localhost:8000/api/docs/` - Interactive API explorer
- **ReDoc**: `http://localhost:8000/api/redoc/` - Alternative documentation viewer
- **OpenAPI Schema**: `http://localhost:8000/api/schema/` - Raw OpenAPI schema

Use these endpoints to explore and test all available API operations with automatic request/response examples.

## Setup & Installation

### Prerequisites
- Docker and Docker Compose (recommended)
- Python 3.13+ (for local development)
- PostgreSQL 15+ (if running without Docker)

### Branch Management

> ⚠️ **Important**: Always develop on the `dev` branch. The `main` branch is reserved for production deployments only.

When starting development:
```bash
git checkout dev
```

Only merge to `main` after thorough testing and when ready for production release.

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aarnet_technical_assessment_dhani_pozniak
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` if needed (defaults are suitable for local development):
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here-change-in-production
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=network_topology
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   ```

3. **Build and run containers**:
   ```bash
   docker-compose up --build
   ```

4. **The API will be available at**:
   - API: `http://localhost:8000/api/`
   - Admin: `http://localhost:8000/admin/` (credentials: admin/admin - create via management command)
   - Database: PostgreSQL on `localhost:5432`

### Docker-Specific Commands

#### Create a Superuser in Docker

Create an admin superuser in the running Docker container:

```bash
docker-compose exec -T web python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@localhost.local', 'admin123'); print('Admin user created successfully')"
```

Or use the interactive shell:
```bash
docker-compose exec web python manage.py createsuperuser
```

#### Run Unit Tests in Docker

Run all tests with coverage in Docker:
```bash
docker-compose exec -T web pytest topology/tests/ --cov=topology --cov-report=term-missing -v
```

Run tests with HTML coverage report:
```bash
docker-compose exec -T web pytest topology/tests/ --cov=topology --cov-report=html --cov-report=term-missing
```

Run a specific test file:
```bash
docker-compose exec -T web pytest topology/tests/test_models.py -v
```

Run a specific test class:
```bash
docker-compose exec -T web pytest topology/tests/test_models.py::SiteModelTests -v
```

#### Execute Django Management Commands

Run migrations:
```bash
docker-compose exec -T web python manage.py migrate
```

Access Django shell:
```bash
docker-compose exec web python manage.py shell
```

Query the database:
```bash
docker-compose exec -T db psql -U postgres -d network_topology -c "SELECT * FROM topology_site;"
```

### Option 2: Local Development Setup

> **Important**: This option requires PostgreSQL to be running. You must start the Docker database container before proceeding:
> ```bash
> docker-compose up db -d
> ```
> This starts only the database service, allowing you to run the Django development server locally while using PostgreSQL in Docker.

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aarnet_technical_assessment_dhani_pozniak
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file from example**:
   ```bash
   cp .env.example .env
   ```

   The `.env` file is configured for PostgreSQL by default:
   ```
   DEBUG=True
   SECRET_KEY=dev-secret-key-change-in-production
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=network_topology
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - API: `http://localhost:8000/api/`
   - Admin: `http://localhost:8000/admin/`

## Usage Examples

### Create a Site
```bash
curl -X POST http://localhost:8000/api/sites/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "London Data Center",
    "description": "Primary data center in London",
    "status": "Active"
  }'
```

### Create a Device
```bash
curl -X POST http://localhost:8000/api/devices/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "London-Router-01",
    "site": 1,
    "serial_number": "ABC123456789"
  }'
```

### Create an Interface
```bash
curl -X POST http://localhost:8000/api/interfaces/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GigabitEthernet0/1",
    "device": 1,
    "speed": 1000,
    "status": "Up"
  }'
```

### Create a Connection
```bash
curl -X POST http://localhost:8000/api/connections/ \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "CONN-1001",
    "name": "Link to Core Switch",
    "status": "Connected",
    "start_interface": 1,
    "end_interface": 2
  }'
```

### Retrieve All Sites
```bash
curl http://localhost:8000/api/sites/
```

### Retrieve a Specific Site
```bash
curl http://localhost:8000/api/sites/1/
```

### Retrieve All Devices
```bash
curl http://localhost:8000/api/devices/
```

### Retrieve a Specific Device
```bash
curl http://localhost:8000/api/devices/1/
```

### Retrieve All Interfaces
```bash
curl http://localhost:8000/api/interfaces/
```

### Retrieve a Specific Interface
```bash
curl http://localhost:8000/api/interfaces/1/
```

### Retrieve All Connections
```bash
curl http://localhost:8000/api/connections/
```

### Retrieve a Specific Connection
```bash
curl http://localhost:8000/api/connections/1/
```

### Trace Connections by Device
```bash
curl http://localhost:8000/api/trace/?type=device&id=1
```

### Trace Connections by Interface
```bash
curl http://localhost:8000/api/trace/?type=interface&id=1
```

### Trace Connections by Site
```bash
curl http://localhost:8000/api/trace/?type=site&id=1
```

## Assumptions

1. **Point-to-Point Connections**: All connections are strictly point-to-point between two different interfaces. A connection cannot start and end at the same interface.

2. **Database**: The application uses PostgreSQL in production (Docker) and SQLite for local development by default. Database configuration is determined by environment variables.

3. **Authentication**: The API is currently open (no authentication required). For production deployment, consider implementing token-based authentication (e.g., DRF's TokenAuthentication).

4. **Timestamps**: All models include `created_at` and `updated_at` fields for auditing purposes.

5. **Unique Constraints**:
   - Site names must be unique across the system
   - Device names must be unique across the system
   - Device serial numbers must be unique
   - Connection IDs must be unique
   - Interface names must be unique within a device

6. **Cascade Delete**: When a Site is deleted, all associated Devices are deleted. When a Device is deleted, all associated Interfaces are deleted. When an Interface is deleted, any Connections referencing it are also deleted.

7. **Connection Tracing Performance**: For large networks with many connections, the tracing endpoint may take longer for site-level queries. Consider adding database indexes or caching for production deployments.

8. **Status Enumerations**: Status values are limited to predefined choices:
   - **Site Status**: Active, Planned, Decommissioned
   - **Interface Status**: Up, Down, Maintenance
   - **Connection Status**: Connected, Disconnected

## High-Level Design

### Architecture

The application follows a standard Django REST Framework architecture:

```
┌─────────────────────────────────────────┐
│         API Clients (HTTP/REST)         │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│   Django REST Framework Endpoints       │
│  (DRF Routers & Custom Views)           │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│     Serializers & Validators            │
│  (Input validation & transformation)    │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        Django ORM & Models              │
│  (Business logic & constraints)         │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│   PostgreSQL / SQLite Database          │
│  (Persistent data storage)              │
└─────────────────────────────────────────┘
```

### Key Design Decisions

1. **Serializer-Based Validation**: DRF serializers handle input validation before reaching the database, ensuring data integrity.

2. **Custom Tracing View**: The `TraceConnectionsView` uses Django's QuerySet API with `Q` objects for efficient connection filtering at the database level, rather than loading all data into memory.

3. **Separation of Concerns**:
   - Models define data structure and constraints
   - Serializers handle API representation and validation
   - ViewSets handle CRUD operations
   - Custom views handle specialized logic

4. **Connection Representation**: Connections include full target information (site, device, interface) in the response for convenience, minimizing the need for additional API calls.

5. **Relationship Model**: All relationships use Django's ForeignKey with CASCADE delete to maintain referential integrity.

6. **Containerization**: Docker and docker-compose ensure consistent environments across development, testing, and production.

### Performance Considerations

1. **Database Indexing**: The application uses Django's default indexing for ForeignKeys and unique fields. For large datasets, consider adding database indexes on:
   - `Connection.start_interface_id`
   - `Connection.end_interface_id`
   - `Interface.device_id`
   - `Device.site_id`

2. **Query Optimization**: The tracing endpoints use Django's `select_related()` and `prefetch_related()` concepts implicitly through the serializers. For production, consider explicit optimization:
   ```python
   connections.select_related('start_interface__device__site', 'end_interface__device__site')
   ```

3. **Pagination**: The default pagination is set to 100 results per page. This can be adjusted in `settings.py`.

## Troubleshooting

### Container Issues

**Port already in use**:
```bash
docker-compose down
docker-compose up --build
```

**Database connection errors**:
Ensure the database container is healthy:
```bash
docker-compose ps
```

**Migrations not applied**:
The docker-compose configuration automatically runs migrations on startup. For manual migration:
```bash
docker-compose exec web python manage.py migrate
```

### Local Development Issues

**ModuleNotFoundError**:
Ensure virtual environment is activated:
```bash
source .venv/bin/activate
```

**Database locked (SQLite)**:
SQLite is limited for concurrent access. For development, consider using PostgreSQL locally:
```bash
pip install psycopg2-binary
# Update .env to use PostgreSQL
```

## Production Deployment

For production deployment:

1. **Update environment variables**:
   - Set `DEBUG=False`
   - Generate a secure `SECRET_KEY`
   - Configure `ALLOWED_HOSTS` appropriately
   - Use PostgreSQL instead of SQLite

2. **Security measures**:
   - Enable HTTPS/TLS
   - Implement API authentication
   - Add rate limiting
   - Set up proper logging and monitoring

3. **Database**:
   - Use a managed PostgreSQL service (e.g., AWS RDS, Azure Database for PostgreSQL)
   - Enable automated backups
   - Configure connection pooling

4. **Deployment**:
   - Use a container orchestration platform (Kubernetes, Docker Swarm, etc.)
   - Set up proper health checks
   - Configure auto-scaling policies
   - Use a reverse proxy (Nginx, HAProxy)

## Development

### Logging

The application includes comprehensive logging for API operations:

- **Log Level**: INFO
- **Logger**: `topology` module logger
- **Output**: Console output (StreamHandler)

**Logged Operations**:
- Device retrieval: Logs device ID when retrieving a specific device
- Device listing: Logs count of devices returned

**Configuration**: Logging is configured in `network_topology/settings.py` with the `LOGGING` dictionary.

**Example Log Output**:
```
INFO:topology.views:Fetching all devices
INFO:topology.views:Retrieved 4 devices
```

### Code Quality

The project uses industry-standard linting and formatting tools:

#### Flake8 (Linting)

Configuration file: `.flake8`

Ignored rules:
- `E501`: Line too long
- `W504`: Line break after binary operator

Run linting check:
```bash
flake8 topology/ network_topology/
```

#### isort (Import Sorting)

Configuration file: `.isort.cfg`

Automatically sorts imports and skips migration files.

Run import check:
```bash
isort topology/ network_topology/ --check-only
```

Auto-fix imports:
```bash
isort topology/ network_topology/
```

### Running Tests

#### Using pytest (Recommended)

Run all tests with coverage reporting:
```bash
pytest topology/tests/ --cov=topology --cov-report=term-missing -v
```

Run tests with HTML coverage report:
```bash
pytest topology/tests/ --cov=topology --cov-report=html --cov-report=term-missing
```

Run a specific test file:
```bash
pytest topology/tests/test_models.py -v
```

Run a specific test class:
```bash
pytest topology/tests/test_models.py::SiteModelTests -v
```

Run a specific test method:
```bash
pytest topology/tests/test_models.py::SiteModelTests::test_site_creation -v
```

#### Using Django's default test runner

```bash
python manage.py test
```

### Creating Test Data

You can use the Django shell to create test data:

```bash
python manage.py shell
```

```python
from topology.models import Site, Device, Interface, Connection

# Create a site
site = Site.objects.create(name="Test DC", status="Active")

# Create devices
device1 = Device.objects.create(name="Router-01", site=site, serial_number="SN001")
device2 = Device.objects.create(name="Switch-01", site=site, serial_number="SN002")

# Create interfaces
iface1 = Interface.objects.create(name="Eth0/0", device=device1, speed=1000, status="Up")
iface2 = Interface.objects.create(name="Eth0/1", device=device2, speed=1000, status="Up")

# Create connection
conn = Connection.objects.create(
    connection_id="CONN-001",
    name="Link",
    status="Connected",
    start_interface=iface1,
    end_interface=iface2
)
```

## CI/CD Workflows

This project uses GitHub Actions for continuous integration and deployment.

### Workflows

#### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggered on**: Push to `dev` or `main`, Pull Requests

**Steps**:
- Sets up Python 3.13 with PostgreSQL service
- Installs dependencies
- Runs code quality checks (flake8, isort, black)
- Executes full test suite with coverage reporting
- Uploads coverage reports to Codecov
- Builds Docker image (dry-run to verify build succeeds)

**Requirements for passing**:
- ✅ All tests pass (92 tests with 100% coverage)
- ✅ Code coverage ≥ 80% (currently 100%)
- ✅ No linting errors (flake8, isort)
- ✅ Docker image builds successfully

**Test Coverage Details**:
- Unit tests for models, serializers, and views
- Logging tests for device endpoints using `assertLogs`
- Integration tests for API endpoints
- Connection tracing tests

#### 2. Docker Build & Push Workflow (`.github/workflows/docker-build.yml`)

**Triggered on**: Push to `main`, Release published

**Steps**:
- Builds Docker image with optimized cache
- Authenticates with GitHub Container Registry (ghcr.io)
- Pushes image with semantic versioning tags
- Tags include: branch name, semantic version, commit SHA

**Examples**:
- Push to `main`: `ghcr.io/pozengineer/aarnet_technical_assessment_dhani_pozniak:main`
- Release v1.0.0: `ghcr.io/pozengineer/aarnet_technical_assessment_dhani_pozniak:1.0.0`
- Any commit: `ghcr.io/pozengineer/aarnet_technical_assessment_dhani_pozniak:sha-abc123de`

### Workflow Status

Check workflow status in GitHub Actions tab. Failed workflows block PR merges to maintain code quality.

### Local Testing Before Push

Run these commands locally to catch issues before pushing:

```bash
# Run all tests with coverage
pytest topology/tests/ --cov=topology --cov-report=term-missing -v

# Check code quality
flake8 topology/ network_topology/
isort topology/ network_topology/ --check-only

# Auto-fix imports
isort topology/ network_topology/

# Build Docker image
docker build -t network-topology-api:test .
```

## License

This project is provided as-is for educational and assessment purposes.

## Support

For issues or questions, please refer to the Django documentation and Django REST Framework documentation.
