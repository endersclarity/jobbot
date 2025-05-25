# JobBot Project-Specific Development Standards

## Pull Request Workflow

### Required Process for All Changes
1. **Create Feature Branch**: Follow naming convention `feature/phase-X-description`
2. **Develop and Test**: Ensure all tests pass locally before pushing
3. **Create Pull Request**: Use structured PR template with detailed description
4. **Wait for codeRABBIT Review**: Do not merge until automated review is complete
5. **Address Feedback**: Implement any suggestions from codeRABBIT analysis
6. **Merge After Approval**: Only merge to main after codeRABBIT gives positive review

### Pull Request Template
When creating PRs, always include:

```markdown
## Phase X: [Description]

### Summary
Brief overview of changes and purpose

### Changes Made
- Bullet point list of specific changes
- Include new files, modified functionality
- Database schema changes if applicable

### Testing
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

### Phase Success Criteria
- [ ] Criteria 1 from development roadmap
- [ ] Criteria 2 from development roadmap
- [ ] All deliverables completed

### codeRABBIT Review
- [ ] Automated review completed
- [ ] All suggestions addressed
- [ ] Code quality score acceptable
```

### Branch Strategy
- **main**: Stable releases only, protected branch
- **feature/phase-X-name**: Development branches for each phase
- **No direct commits to main**: All changes via PR
- **Delete feature branches**: After successful merge

### Code Quality Standards

#### Database & Models
- All models must have proper relationships and constraints
- Use SQLAlchemy best practices with proper indexing
- Include comprehensive docstrings for all model classes
- Validate all foreign key relationships

#### API Development
- Follow FastAPI best practices and conventions
- Use Pydantic models for all request/response validation
- Include comprehensive error handling with proper HTTP status codes
- Add OpenAPI documentation for all endpoints

#### Testing Requirements
- Minimum 90% code coverage for all new code
- Unit tests for all models and business logic
- Integration tests for all API endpoints
- Performance tests for database queries

#### Security Standards
- Never commit secrets or API keys to a repository
- Use environment variables for all configuration
- Validate and sanitize all user inputs
- Follow OWASP security guidelines

## Technology Stack Decisions

### Backend Requirements
- **Framework**: FastAPI (chosen for async support and auto-documentation)
- **Database**: PostgreSQL (production), SQLite (testing)
- **ORM**: SQLAlchemy with Alembic migrations
- **Task Queue**: Celery + Redis for background jobs
- **Testing**: pytest with async support

### Code Quality Tools
- **Formatting**: black (line length 88)
- **Import Sorting**: isort (compatible with black)
- **Linting**: flake8 with standard configuration
- **Type Checking**: mypy with strict mode
- **Testing**: pytest with coverage reporting

### Development Workflow
- **Makefile**: Use standardized commands for all operations
- **Environment**: Use .env files for local configuration
- **Dependencies**: Pin all versions in requirements.txt
- **Documentation**: Update README for all major changes

## Phase-Specific Guidelines

### ✅ Phase 1: Foundation (COMPLETE)
- Focus on solid architecture and database design
- Comprehensive testing framework setup
- Development workflow establishment

### ✅ Phase 2: Core API (COMPLETE)
- Complete CRUD operations for all models
- Proper error handling and validation
- API documentation and testing

### 🚧 Phase 3: Strategic Pivot & Data Collection (IN PROGRESS)
**3A: Raw Data Collection** ✅ Complete
- Token-efficient scraping without LLM processing
- BrowserMCP anti-detection measures bypassing 403 errors
- Rate limiting and intelligent request delays
- Structured data storage in scraped_data/ directory

**3B: Offline Processing Pipeline** 🚧 Current Focus
- HTML parsing and data extraction without token burn
- Duplicate detection and deduplication algorithms
- Data normalization and field standardization
- Batch processing and database import automation

### 📋 Phase 4: Business Intelligence & Market Creation (PLANNED)
**Strategic Transformation**: JobBot → BusinessBot for market creation
- Local company research and automation opportunity identification
- Value proposition generation and proof-of-concept creation
- Outreach automation and business relationship management
- Transform from reactive job hunting to proactive market creation

## MCP Integration Standards

### Required MCP Servers ✅ Installed and Functional
- **postgres**: Database operations and complex queries
- **filesystem**: File management and scraped data storage
- **fetch**: HTTP requests and API integrations
- **puppeteer**: Advanced web scraping automation (backup)
- **gmail**: Email automation and response monitoring
- **browsermcp**: Real browser automation with anti-detection ✅ PRIMARY SCRAPER
- **desktop-commander**: File operations and command execution
- **exa**: Web search and research capabilities

### MCP Usage Guidelines
- **Primary Scraping**: Use browsermcp for all job board scraping (bypasses 403 errors)
- **Fallback Strategy**: Maintain puppeteer as backup scraping method
- **Data Processing**: Use filesystem MCP for scraped data organization
- **Business Intelligence**: Leverage exa for company research and market analysis
- **Email Automation**: Gmail MCP for outreach campaigns and response monitoring
- **Database Operations**: Postgres MCP for complex queries and business intelligence
- **Development**: Desktop-commander for file operations and CLI automation

## Deployment Standards

### Environment Configuration
- **Development**: Local setup with SQLite and development settings
- **Testing**: CI/CD pipeline with test database
- **Production**: PostgreSQL, Redis, proper security configuration

### Release Process
1. Complete phase development in feature branch
2. Full test suite passes (unit, integration, performance)
3. codeRABBIT review and approval
4. Merge to main via pull request
5. Tag release with semantic versioning
6. Deploy to production environment

---

*This file defines JobBot-specific development standards and must be followed for all contributions.*