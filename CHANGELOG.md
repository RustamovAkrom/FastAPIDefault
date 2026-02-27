# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features under development

### Changed
- Updates to existing features

### Fixed
- Bug fixes in development

### Deprecated
- Features to be removed

### Removed
- Features that have been removed

### Security
- Security fixes

---

## [1.0.0] - 2024-02-23

### Added
- ✨ Initial production-ready release of FastAPI-Default template
- 🔥 FastAPI 0.115.12 with async/await support
- 🗄️ SQLAlchemy 2.0.41 with async engine and connection pooling
- 📦 Alembic 1.15.2 for database migrations management
- 🐘 PostgreSQL 16 with Docker support and health checks
- 📊 Prometheus 2.50.1 metrics collection and monitoring
- 📈 Grafana 10.3.1 with pre-configured dashboards
- 🔔 Sentry 2.29.1 for error tracking and performance monitoring
- 🛡️ SQLAdmin 0.23.0 with RBAC (Role-Based Access Control)
- 📝 Loguru 0.7.3 for structured logging
- 🔐 Bcrypt password hashing with Passlib 1.7.4
- 🐳 Docker & Docker Compose with multi-stage builds
- ⚡ Taskfile for development command automation
- 🧪 Pytest with fixtures and fixtures for testing
- 📚 Comprehensive documentation (README, ARCHITECTURE, DEPLOYMENT, OBSERVABILITY)
- 🔄 Alembic database migrations with version control

### Core Features
- Application factory pattern (create_app())
- Modular project structure with separation of concerns
- Async-first design with SQLAlchemy async support
- Centralized configuration management via Pydantic Settings
- Dependency injection throughout application
- Custom exception handlers with proper HTTP status codes
- Health check endpoints (/healthcheck, /status, /version)
- Metrics endpoint with security key protection
- Admin panel with user RBAC
- Database connection pooling and optimization
- Request/response logging with structured format
- CORS configuration support

### Deployment Features
- Non-root Docker containers for security
- Resource limits (CPU/memory) in Docker Compose
- Capability dropping for reduced attack surface
- PostgreSQL health checks
- Prometheus scraping configuration
- Grafana data source provisioning
- Loki log aggregation setup
- Promtail log shipping configuration

### Documentation
- README.md with quick start guides (Docker & local)
- ARCHITECTURE.md with system design and file structure
- DEPLOYMENT.md with production deployment strategies
- OBSERVABILITY.md with monitoring setup guide
- CONTRIBUTING.md for community contributions
- TEMPLATE_USAGE.md for using as project template
- PUBLISHING.md for PyPI distribution

### Development Tools
- GitHub Actions workflows for CI/CD
- Pre-configured ruff for code linting
- MyPy for type checking
- Pytest configuration with asyncpg support
- Docker Compose for local development
- .env.example with all required variables

### Configuration
- Environment-based settings (development, staging, production)
- Database pool configuration (size, overflow, recycle)
- CORS configuration
- Logging levels and format
- Sentry integration with sample rates
- Admin panel security settings

### Dependencies
- Core: FastAPI, Uvicorn, SQLAlchemy, Alembic
- Database: Asyncpg, Psycopg2
- Monitoring: Prometheus-client, Sentry-SDK
- Admin: SQLAdmin
- Logging: Loguru
- Security: Bcrypt, Passlib
- Validation: Pydantic, Pydantic-settings

---

## [1.0.1] - Planned

### To be released
- CLI tool for scaffolding new projects
- Application template generator
- Additional example models
- Webhook integration support
- Full-text search capabilities
- Caching layer with Redis

---

## Version History Summary

| Version | Release Date | Status | Key Changes |
|---------|-------------|--------|-------------|
| 1.0.0 | 2024-02-23 | Latest | Production-ready release with full stack |
| 0.1.0 | 2024-01-15 | Archived | Initial development version |

---

## Release Guidelines

### Major Version (X.0.0)
- Breaking API changes
- Database schema changes
- Dependency upgrades with incompatibility

### Minor Version (0.X.0)
- New features (backward compatible)
- New endpoints or modules
- New configuration options

### Patch Version (0.0.X)
- Bug fixes
- Security patches
- Documentation improvements
- Performance optimizations

---

## Upgrade Guide

### From 0.1.0 to 1.0.0
1. Backup your database
2. Update `pyproject.toml` dependencies
3. Run `pip install -e ".[dev,test]" -U`
4. Run database migrations: `alembic upgrade head`
5. Review `.env` for new required variables
6. Restart application

### From 1.0.0 to 1.0.1 (when available)
1. Backup database
2. Update package: `pip install fastapi-default -U`
3. Review changelog for any breaking changes
4. Test in development environment
5. Deploy to production

---

## Deprecation Timeline

- **3 months**: Feature announced as deprecated
- **6 months**: Deprecation warning in code
- **9 months**: Feature removed in next major version

---

## Security

For security vulnerabilities, please see [SECURITY.md](SECURITY.md).

---

## Credits

**Framework & Libraries:**
- [FastAPI](https://fastapi.tiangolo.com/) - ASGI web framework
- [SQLAlchemy](https://docs.sqlalchemy.org/) - ORM and database toolkit
- [PostgreSQL](https://www.postgresql.org/) - Open source database
- [Docker](https://www.docker.com/) - Containerization platform

**Monitoring & Observability:**
- [Prometheus](https://prometheus.io/) - metrics database
- [Grafana](https://grafana.com/) - visualization
- [Sentry](https://sentry.io/) - error tracking
- [Loki](https://grafana.com/loki/) - log aggregation

**Contributors:**
- Community contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
