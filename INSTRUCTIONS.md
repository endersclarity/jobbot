# JobBot Setup & Development Instructions

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ with pip
- PostgreSQL database server
- Redis server (for task queue)
- Git for version control
- Node.js (for frontend development in later phases)

### Initial Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/endersclarity/jobbot
   cd jobbot
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   make install
   # OR manually: pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb jobbot
   
   # Run migrations
   make init-db
   # OR manually: alembic revision --autogenerate -m "Initial migration" && alembic upgrade head
   ```

6. **Start Development Server**
   ```bash
   make run-dev
   # OR manually: uvicorn app.main:app --reload
   ```

7. **Verify Installation**
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health
   - Run tests: `make test`

## 🔧 Development Workflow

### Daily Development
```bash
# Start your day
git checkout main
git pull origin main
git checkout feature/your-branch-name

# Development cycle
make format          # Format code
make lint           # Check code quality
make test           # Run test suite
git add .
git commit -m "Your changes"
git push origin feature/your-branch-name

# Create PR when ready
gh pr create --title "Your PR Title" --body "Description"
```

### Available Commands
```bash
make help           # Show all available commands
make install        # Install dependencies
make dev            # Install development dependencies
make run-dev        # Run development server with hot reload
make test           # Run test suite with coverage
make lint           # Run code linting (flake8, mypy)
make format         # Format code (black, isort)
make init-db        # Initialize database with migrations
make migrate        # Run database migrations
make clean          # Clean up temporary files
```

### Testing Strategy
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and database operations
- **Performance Tests**: Ensure database queries are optimized
- **Coverage**: Maintain minimum 90% code coverage

## 📊 Database Management

### Local Development Database
```bash
# Using SQLite for development
export DATABASE_URL="sqlite:///./jobbot_dev.db"
python -c "from app.core.database import engine; from app.models import Base; Base.metadata.create_all(engine)"
```

### PostgreSQL Production Setup
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu
brew install postgresql                              # macOS

# Create database and user
sudo -u postgres psql
CREATE DATABASE jobbot;
CREATE USER jobbot WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE jobbot TO jobbot;
\q

# Update .env file
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=jobbot
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=jobbot
```

### Migration Management
```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS

# Check connection
psql -h localhost -U jobbot -d jobbot

# Reset database
dropdb jobbot && createdb jobbot
alembic upgrade head
```

#### Import Errors
```bash
# Ensure virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Test Failures
```bash
# Run specific test
pytest tests/test_models.py::test_job_creation -v

# Run with debugging
pytest tests/ --pdb

# Check coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

#### Development Server Issues
```bash
# Kill existing processes
pkill -f uvicorn

# Check port availability
lsof -i :8000

# Run with debug logging
uvicorn app.main:app --reload --log-level debug
```

### Performance Issues

#### Slow Database Queries
```bash
# Enable query logging in PostgreSQL
# Add to postgresql.conf:
log_statement = 'all'
log_duration = on

# Use database query profiling
python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('EXPLAIN ANALYZE SELECT * FROM jobs LIMIT 10'))
    print(result.fetchall())
"
```

#### Memory Usage
```bash
# Monitor memory usage
top -p $(pgrep -f uvicorn)

# Profile memory usage
pip install memory_profiler
python -m memory_profiler app/main.py
```

## 🔒 Security Configuration

### Environment Variables
Never commit these to Git:
```bash
SECRET_KEY=your-very-secure-secret-key
POSTGRES_PASSWORD=secure_database_password
GMAIL_APP_PASSWORD=your-gmail-app-password
API_KEYS=your-external-api-keys
```

### SSL/TLS Setup
```bash
# Generate self-signed certificate for development
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Run with HTTPS
uvicorn app.main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

## 📖 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### API Testing
```bash
# Using curl
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/api/v1/jobs"

# Using httpie
http GET localhost:8000/health
http GET localhost:8000/api/v1/jobs

# Using Python requests
python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(response.json())
"
```

## 🚀 Deployment Instructions

### Docker Deployment
```bash
# Build Docker image
docker build -t jobbot .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Load balancer configured
- [ ] Security headers configured

---

*This file provides comprehensive setup and troubleshooting guidance for JobBot development and deployment.*