# JobBot - Automated Job Search System

## Overview

JobBot is a comprehensive job search automation platform that streamlines the entire job application process from discovery to tracking. The system intelligently scrapes job postings, generates tailored resumes and cover letters, submits applications automatically, and tracks all responses and follow-ups.

## Phase 1 Status: ✅ COMPLETE

**Foundation & Database Setup** - All core infrastructure is now in place:

- ✅ Project structure with proper Python packaging
- ✅ FastAPI application with CORS and health checks  
- ✅ PostgreSQL database models with comprehensive schema
- ✅ Alembic migration system configured
- ✅ Environment configuration with secure defaults
- ✅ Testing framework with pytest and fixtures
- ✅ Development tooling (Makefile, linting, formatting)

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (for task queue)

### Setup

1. **Clone and navigate to project:**
   ```bash
   git clone https://github.com/endersclarity/jobbot
   cd jobbot
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   make install
   # or: pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

5. **Initialize database:**
   ```bash
   make init-db
   # This creates initial migration and applies it
   ```

6. **Run development server:**
   ```bash
   make run-dev
   # or: uvicorn app.main:app --reload
   ```

7. **Run tests:**
   ```bash
   make test
   # or: pytest
   ```

## API Documentation

Once running, visit:
- **Interactive API docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **API v1 root:** http://localhost:8000/api/v1/

## Development Commands

```bash
make help           # Show all available commands
make install        # Install dependencies
make run-dev        # Run development server with hot reload
make test           # Run test suite with coverage
make lint           # Run code linting
make format         # Format code with black and isort
make init-db        # Initialize database with migrations
make migrate        # Run database migrations
make clean          # Clean up temporary files
```

## Architecture

### Database Models
- **Jobs**: Job postings with full metadata and scraping info
- **Applications**: Application tracking with integrity monitoring
- **Employer Responses**: Response parsing and sentiment analysis
- **References**: Reference management with usage tracking
- **Experience Claims**: Credibility monitoring system

### API Structure
- **FastAPI** backend with automatic OpenAPI documentation
- **SQLAlchemy** ORM with Alembic migrations
- **Pydantic** models for request/response validation
- **CORS** enabled for frontend integration

### Testing
- **pytest** with async support
- **Test database** isolation with SQLite
- **Coverage reporting** with html output
- **Fixtures** for database and client setup

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Database**: PostgreSQL (production), SQLite (testing)
- **Task Queue**: Celery + Redis
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Code Quality**: black, isort, flake8, mypy
- **Scraping**: Selenium, BeautifulSoup (planned for Phase 3)

## Development Roadmap

- ✅ **Phase 1**: Foundation & Database Setup (COMPLETE)
- 🚧 **Phase 2**: Core API & Basic Job Management (NEXT)
- 📋 **Phase 3**: Job Scraping Foundation
- 📋 **Phase 4**: Basic Web UI
- 📋 **Phase 5**: Email Automation
- 📋 **Phase 6**: Resume Generation & Optimization
- 📋 **Phase 7**: Credibility & Integrity Tracking
- 📋 **Phase 8**: Advanced Features & Analytics
- 📋 **Phase 9**: Production Deployment

## Security & Ethics

- **Environment variables** for all sensitive configuration
- **Input validation** on all API endpoints
- **Integrity tracking** to maintain application honesty
- **Reference consent** tracking and permission management
- **Rate limiting** for respectful web scraping

## Contributing

1. Create feature branch from main
2. Follow existing code style and patterns
3. Add tests for new functionality
4. Run full test suite before committing
5. Update documentation as needed

## License

MIT License - see LICENSE file for details

---

**Status**: Phase 1 Complete | **Next**: Implementing Core API endpoints for job management