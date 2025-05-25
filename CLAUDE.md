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
- Never commit secrets or API keys to repository
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

### Phase 1: Foundation (COMPLETE)
- Focus on solid architecture and database design
- Comprehensive testing framework setup
- Development workflow establishment

### Phase 2: Core API
- Complete CRUD operations for all models
- Proper error handling and validation
- API documentation and testing

### Phase 3: Web Scraping
- Respectful scraping with rate limiting
- Anti-detection measures and proxy rotation
- Robust error handling for network issues

### Future Phases
- Maintain backwards compatibility
- Performance optimization for scale
- Security hardening for production

## MCP Integration Standards

### Required MCP Servers
- **postgres**: Database operations and queries
- **filesystem**: File management and storage
- **fetch**: HTTP requests and API calls
- **puppeteer**: Web scraping automation
- **gmail**: Email automation and monitoring

### MCP Usage Guidelines
- Use MCP servers for external system integration
- Maintain fallback mechanisms for MCP failures
- Log all MCP operations for debugging
- Test MCP integrations thoroughly

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