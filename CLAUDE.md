# Business Intelligence Engine (BIE) - Project-Specific Development Standards

## Project Overview
**Vision**: Transform traditional job search automation into proactive business opportunity creation through intelligent company research, automation potential detection, and personalized solution delivery.

**Current Phase**: Phase 3B - Offline Processing & Data Pipeline Development

## AI Agent Orchestration Integration

### Enhanced Workflow Commands
This project now features advanced AI agent orchestration for seamless strategic ↔ tactical integration:

```bash
# One-time setup (discovers strategic context, integrates with Taskmaster)
/init

# Daily intelligent workflow (context-aware task management)
/task → /task → /task → /task

# Manual context re-integration (when strategic context changes)
/init --force
```

### Strategic Foundation
The project utilizes a comprehensive memory-bank system with:
- **7 documented modules**: Complete system architecture with dependency tracking
- **Strategic roadmap**: 8-phase evolution from foundation to enterprise platform
- **Implementation plans**: Phase 3B offline processing pipeline details
- **98K+ characters**: Rich context for intelligent task generation

## Development Commands & Standards

### Core Development Workflow
```bash
# Backend Development
make run-dev              # Start FastAPI server with hot reload
make test                 # Run comprehensive test suite with coverage
make lint                 # Code quality validation (black, isort, flake8, mypy)
make format               # Automated code formatting

# Database Management
make init-db              # Initialize database with migrations
make migrate              # Apply new database migrations
alembic revision --autogenerate -m "description"  # Create new migration

# Frontend Development (Dashboard)
cd dashboard && npm run dev    # Start React development server
cd dashboard && npm run build  # Build production dashboard
```

### Node.js Scraping Infrastructure
```bash
# Multi-site scraping with Crawlee
npm run orchestrator      # Multi-site job scraping orchestrator
npm run demo             # Demo scraping with sample data
npm run scrape:indeed    # Target Indeed specifically
npm run scrape:all       # All supported job sites

# Development setup
npm run install-all      # Install all scraping dependencies
npm run install-browsers # Install Playwright browser engines
```

### AI Agent Integration
```bash
# Strategic foundation setup
/architect               # Create comprehensive project structure (if needed)

# AI agent integration
/init                    # Discover context and integrate strategic → tactical
/task                    # Intelligent daily workflow with full project context

# Manual orchestration
python3 /home/ender/.claude/orchestration/context_discovery.py  # Test integration
```

## Technology Stack & Architecture

### Backend (Python)
- **Framework**: FastAPI with async support and auto-documentation
- **Database**: PostgreSQL (production), SQLite (testing)
- **ORM**: SQLAlchemy with Alembic migrations
- **Task Queue**: Celery + Redis for background processing
- **Testing**: pytest with async support and coverage reporting

### Frontend (JavaScript/React)
- **Framework**: React with modern hooks and context
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Modern CSS with responsive design
- **Real-time**: WebSocket integration for live updates

### Data Processing (Node.js)
- **Scraping**: Crawlee framework with anti-detection capabilities
- **Browser Automation**: Playwright with stealth techniques
- **Multi-site Support**: Indeed, LinkedIn, Glassdoor orchestration
- **Data Storage**: Raw data → processed data → database import pipeline

## Module Architecture

### Data Collection Module (`module_data_collection.md`)
- **Purpose**: Web scraping and raw data aggregation
- **Key Components**: Anti-detection browser management, multi-site orchestration
- **Current Status**: BrowserMCP integration with 403 error bypass capabilities

### Intelligence Analysis Module (`module_intelligence_analysis.md`)  
- **Purpose**: Transform raw data into actionable business intelligence
- **Key Components**: HTML parsing, data normalization, duplicate detection
- **Current Status**: Phase 3B implementation in progress

### Database Infrastructure Module (`module_database_infrastructure.md`)
- **Purpose**: Foundational data storage and business intelligence queries
- **Key Components**: PostgreSQL optimization, migration management, analytics
- **Current Status**: Production-ready with comprehensive schema

### Dashboard Interface Module (`module_dashboard_interface.md`)
- **Purpose**: Real-time visualization and system control
- **Key Components**: React components, WebSocket integration, business analytics
- **Current Status**: Operational with responsive design

## Development Standards

### Code Quality Requirements
- **Python**: black (line length 88), isort, flake8, mypy with strict settings
- **JavaScript**: ESLint + Prettier with modern ES6+ standards
- **Testing**: 90%+ coverage requirement for all new code
- **Documentation**: Comprehensive docstrings and inline comments

### Database Development
- **Migrations**: Always use Alembic for schema changes
- **Models**: Include proper relationships, constraints, and indexes
- **Queries**: Optimize for performance with proper indexing
- **Backup**: Regular automated backups with point-in-time recovery

### Security & Performance
- **Environment Variables**: All sensitive configuration externalized
- **Input Validation**: Comprehensive validation on all API endpoints
- **Rate Limiting**: Respectful web scraping with circuit breakers
- **Caching**: Redis integration for performance optimization

## Phase 3B Development Focus

### Current Implementation Priority
1. **HTML Parser & Data Extractor** - Parse raw scraped content into structured data
2. **Duplicate Detection System** - Sophisticated deduplication with fuzzy matching
3. **Data Normalization Pipeline** - Standardize salary, location, job type fields
4. **Batch Processing System** - Orchestrate processing workflows
5. **Database Import System** - Efficient bulk data import with conflict handling

### Task Management Integration
The project utilizes Taskmaster for intelligent task management:
- **Context-Aware Tasks**: Generated from comprehensive strategic documentation
- **Phase 3B Focus**: Tasks specifically aligned with offline processing pipeline
- **Dependency Management**: Proper task sequencing and priority handling
- **Progress Tracking**: Bidirectional sync between tactical tasks and strategic documentation

## Testing Strategy

### Multi-Layer Testing Approach
```bash
# Backend API Testing
pytest tests/test_api_endpoints.py     # Comprehensive API validation
pytest tests/test_models.py           # Database model testing
pytest tests/test_scraper_direct.py   # Scraping infrastructure testing

# Frontend Testing
cd dashboard && npm test              # React component testing
cd dashboard && npm run test:e2e      # End-to-end dashboard testing

# Integration Testing
python tests/run_all_tests.py        # Master test runner with reporting
```

### Quality Assurance
- **Automated Testing**: GitHub Actions CI/CD pipeline
- **Code Coverage**: Minimum 90% coverage requirement
- **Performance Testing**: Database query optimization validation
- **Security Testing**: Input validation and injection prevention

## Production Deployment

### Environment Configuration
- **Development**: Local setup with SQLite and hot reload
- **Staging**: Docker containers with PostgreSQL and Redis
- **Production**: Kubernetes deployment with load balancing and monitoring

### Deployment Pipeline
```bash
# Local development
make run-dev              # Development server with hot reload

# Production build
docker-compose build      # Build all services
docker-compose up -d      # Start production stack

# Database migration
make migrate             # Apply pending migrations
```

## Business Intelligence Strategy

### Strategic Transformation
This project has evolved from traditional job search to business opportunity creation:
- **Market Intelligence**: Comprehensive company research and analysis
- **Opportunity Detection**: Automated identification of automation potential
- **Solution Generation**: Proof-of-concept creation and value demonstration
- **Outreach Automation**: Personalized communication with working solutions

### Success Metrics
- **Data Quality**: >95% accuracy in processed job information
- **Processing Efficiency**: <30 seconds per 100-job batch
- **Deduplication Rate**: <5% duplicate entries in processed data
- **Pipeline Reliability**: >99% uptime for processing workflows

## AI Agent Orchestration Benefits

### Seamless Development Experience
- **Strategic Vision**: Architect creates comprehensive project foundation
- **Tactical Execution**: Taskmaster provides intelligent, context-aware tasks
- **Daily Workflow**: `/task` command enables frictionless development rhythm
- **Bidirectional Intelligence**: Discoveries flow back to strategic documentation

### Context Preservation
- **98,319 characters**: Comprehensive project context vs basic manifest
- **Semantic Translation**: Strategic documentation → Tactical requirements
- **Full Integration**: Memory-bank intelligence drives daily task decisions
- **Automatic Sync**: Task progress updates strategic documentation

---

**Development Philosophy**: Strategic intelligence drives tactical execution through seamless AI agent orchestration, enabling focus on building great software while AI handles workflow management.