# Contributing to FastAPI-Default

Thank you for your interest in contributing! We appreciate contributions from the community, whether they're bug reports, feature suggestions, documentation improvements, or code changes.

## 🎯 How to Contribute

### Reporting Bugs

Found a bug? Please open an issue with:
- **Description**: What's the bug?
- **Steps to reproduce**: How to replicate it?
- **Expected behavior**: What should happen?
- **Actual behavior**: What actually happens?
- **Environment**: OS, Python version, FastAPI version
- **Screenshots/logs**: If applicable

### Suggesting Features

Have an idea? Open an issue with:
- **Description**: What's your suggestion?
- **Motivation**: Why is this useful?
- **Examples**: How would it be used?
- **Alternative solutions**: Any other approaches?

### Improving Documentation

Documentation improvements are always welcome:
- Fix typos or unclear sections
- Add examples or clarifications
- Improve code comments
- Add architecture diagrams
- Create tutorials

### Code Contributions

We welcome code changes for:
- Bug fixes
- New features
- Performance improvements
- Security enhancements
- Test coverage

## 🔧 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/fastapi-default.git
cd fastapi-default

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/fastapi-default.git
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev,test]"
```

### 3. Create Feature Branch

```bash
# Update main
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/bug-description
```

## ✅ Development Workflow

### 1. Make Your Changes

Follow these guidelines:

- **Code style**: Follow PEP 8 (enforced by ruff)
- **Type hints**: Add type hints to all functions
- **Docstrings**: Add docstrings in Google format
- **Tests**: Write tests for new functionality
- **Async**: Keep async first design principle

### 2. Run Local Tests

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type checking
mypy src/

# Run tests
pytest tests/ -v --cov=src

# Run with Docker
docker compose up -d
pytest tests/ -v
```

### 3. Commit Changes

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "feat: add async connection pooling configuration"
git commit -m "fix: correct SQLAlchemy pool_max_overflow parameter"
git commit -m "docs: update deployment guide with Kubernetes examples"
git commit -m "test: add integration tests for admin panel"
git commit -m "perf: optimize database query performance"

# Format: <type>: <description>
# Types: feat, fix, docs, test, perf, refactor, chore
```

### 4. Keep Branch Updated

```bash
git fetch upstream
git rebase upstream/main
git push origin feature/your-feature-name --force-with-lease
```

### 5. Submit Pull Request

1. Push your branch to your fork
2. Go to GitHub and create Pull Request
3. Fill in the PR template with:
   - **Description**: What changes?
   - **Type**: Feature/Fix/Docs/etc
   - **Related issues**: Closes #123
   - **Testing**: How to test?
   - **Screenshots**: If UI changes

## 📋 Pull Request Checklist

Before submitting PR, ensure:

- ✅ Code follows project style (ruff, mypy)
- ✅ All tests pass (`pytest`)
- ✅ New features have tests
- ✅ Documentation is updated
- ✅ No breaking changes (or documented)
- ✅ Commit messages are clear
- ✅ Branch is up-to-date with main

## 🏗️ Project Structure

Key directories for contributions:

```
src/
├── api/              # API endpoints (add routes here)
├── core/             # Core functionality (config, security, monitoring)
├── db/               # Database models and CRUD operations
├── schemas/          # Request/Response models
└── admin/            # Admin panel customization

tests/               # Add tests here
└── test_*.py        # Test files matching feature

docs/                # Documentation files
├── ARCHITECTURE.md  # System design
├── DEPLOYMENT.md    # Production setup
└── OBSERVABILITY.md # Monitoring guide
```

## 🎓 Code Examples

### Adding a New Endpoint

```python
# src/api/api_v1/my_feature.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(tags=["my-feature"])

@router.get("/my-endpoint")
async def get_my_endpoint(
    db: asyncpg.Connection = Depends(get_db)
) -> dict:
    """
    Get data from my endpoint.
    
    Args:
        db: Database connection
        
    Returns:
        Dictionary with data
    """
    result = await db.fetch("SELECT * FROM my_table")
    return {"data": result}
```

### Adding a Database Model

```python
# src/db/models/my_model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base

class MyModel(Base):
    """My data model."""
    
    __tablename__ = "my_table"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    
    def __repr__(self) -> str:
        return f"<MyModel(id={self.id}, name='{self.name}')>"
```

## 🧪 Testing Guidelines

- Use `pytest` for all tests
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use fixtures for common setup
- Aim for 80%+ code coverage
- Test both happy path and error cases

```python
# Example test
import pytest
from src.api.api_v1 import my_feature

@pytest.mark.asyncio
async def test_get_my_endpoint(async_client):
    """Test getting my endpoint."""
    response = await async_client.get("/api/v1/my-endpoint")
    assert response.status_code == 200
    assert "data" in response.json()
```

## 📚 Documentation Guidelines

- Use clear, concise language
- Add code examples where helpful
- Update README.md if needed
- Keep docs in sync with code
- Use Markdown formatting
- Link to related sections

## ✨ Code Review Process

1. **Automated checks**: GitHub Actions runs tests and linting
2. **Maintainer review**: We review code, structure, and design
3. **Feedback**: We'll request changes if needed
4. **Approval**: Once approved, we'll merge

## 🛡️ Code of Conduct

This project adheres to [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). By participating, you agree to uphold these standards.

## ❓ Questions?

- **Issues**: Open an issue for bugs/features
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact via issues (we monitor them)

## 📖 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Guide](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Semantic Versioning](https://semver.org/)

## 🙏 Thank You!

Contributing takes time and effort. We genuinely appreciate your dedication to making FastAPI-Default better for everyone!
