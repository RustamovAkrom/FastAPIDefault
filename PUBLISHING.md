# Publishing FastAPI-Default to PyPI

This guide explains how to build and publish the `fastapi-default` package to PyPI (Python Package Index) so users can install it via `pip install fastapi-default`.

## Prerequisites

1. **Python 3.11+** with pip/uv installed
2. **Build tools**: `pip install build twine`
3. **PyPI Account**: Create account at [pypi.org](https://pypi.org/) (and optionally [test.pypi.org](https://test.pypi.org/))
4. **GitHub Account**: For repository hosting and release management

## Step 1: Update Project Metadata

### 1.1 Update `pyproject.toml`

Ensure your package metadata is complete (already configured):

```toml
[project]
name = "fastapi-default"
version = "1.0.0"
description = "Production-ready FastAPI template..."
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
```

**Important**: Update `authors`, `repository`, and `issues` URLs:

```toml
[project.urls]
Homepage = "https://github.com/RustamovAkrom/FastAPIDefault"
Documentation = "https://github.com/RustamovAkrom/FastAPIDefault#readme"
Repository = "https://github.com/RustamovAkrom/FastAPIDefault.git"
Issues = "https://github.com/RustamovAkrom/FastAPIDefault/issues"
```

### 1.2 Maintain README.md

The README must be comprehensive and appeal to senior developers. It's displayed on PyPI homepage:
- Clear feature list
- Quick start guide
- Architecture overview
- Configuration examples
- Links to deployment docs

Current README is already well-formatted ✅

### 1.3 Verify LICENSE

Ensure LICENSE file includes correct year and copyright holder:

```plaintext
MIT License

Copyright (c) 2024 FastAPI Default Contributors

Permission is hereby granted, free of charge...
```

Current LICENSE is already valid ✅

## Step 2: Create GitHub Repository

### 2.1 Initialize Git Repository (if not already done)

```bash
cd d:\Applications\FastAPI-Default
git init
git add .
git commit -m "Initial commit: FastAPI-Default template project"
```

### 2.2 Push to GitHub

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/fastapi-default.git
git branch -M main
git push -u origin main
```

### 2.3 Create Release Tags

Version control using git tags:

```bash
# Tag current version
git tag -a v1.0.0 -m "Release version 1.0.0: Production-ready FastAPI template"
git push origin v1.0.0
```

**Semantic Versioning**: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Step 3: Build Distribution Packages

### 3.1 Install Build Tools

```bash
# Using pip
pip install build twine

# OR using uv (faster)
uv pip install build twine
```

### 3.2 Build Wheel and Source Distributions

From project root directory:

```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build both source distribution (.tar.gz) and wheel (.whl)
python -m build
```

This creates:
- `dist/fastapi-default-1.0.0.tar.gz` - Source distribution
- `dist/fastapi-default-1.0.0-py3-none-any.whl` - Universal wheel

### 3.3 Verify Distribution Contents

```bash
# List contents of wheel
python -m zipfile -l dist/fastapi-default-1.0.0-py3-none-any.whl

# List contents of source distribution
tar -tzf dist/fastapi-default-1.0.0.tar.gz
```

## Step 4: Test on TestPyPI (Recommended)

**Always test before publishing to production PyPI!**

### 4.1 Create TestPyPI API Token

1. Go to [test.pypi.org](https://test.pypi.org/)
2. Create account (if not exists)
3. Go to **Account Settings -> API tokens**
4. Create token with scope **"Entire repository"**
5. Copy token (it won't be shown again)

### 4.2 Create `~/.pypirc` Configuration

Create file `~/.pypirc` (Windows: `%APPDATA%\pip\pip.ini`):

```ini
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Your TestPyPI token

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Your PyPI token
```

**Security Note**: Never commit `.pypirc` to version control!

### 4.3 Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

Expected output:
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading fastapi-default-1.0.0-py3-none-any.whl
Uploading fastapi-default-1.0.0.tar.gz
```

### 4.4 Test Installation from TestPyPI

```bash
# Create test virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ fastapi-default

# Verify installation
python -c "import fastapi_default; print(fastapi_default.__version__)"
```

### 4.5 Verify Package on TestPyPI

Visit: `https://test.pypi.org/project/fastapi-default/`

Check:
- ✅ README displayed correctly
- ✅ Dependencies listed
- ✅ All metadata visible
- ✅ Project URLs working

## Step 5: Publish to Production PyPI

### 5.1 Create PyPI Account

1. Go to [pypi.org](https://pypi.org/)
2. Create account or use existing
3. Go to **Account Settings -> API tokens**
4. Create token with scope **"Entire repository"**
5. Add to `~/.pypirc` (see Step 4.2)

### 5.2 Upload to Production PyPI

```bash
twine upload dist/*
```

Check that both files upload successfully:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading fastapi-default-1.0.0-py3-none-any.whl
Uploading fastapi-default-1.0.0.tar.gz
```

### 5.3 Verify on PyPI

Visit: `https://pypi.org/project/fastapi-default/`

Allow 1-2 minutes for indexing. Then:

### 5.4 Test Installation from Production PyPI

```bash
# Create fresh virtual environment
python -m venv prod_test_env
source prod_test_env/bin/activate  # On Windows: prod_test_env\Scripts\activate

# Install from production PyPI
pip install fastapi-default

# Verify
python -c "import src.core.settings; print('Installation successful!')"
```

## Step 6: Automate Publishing with GitHub Actions

### 6.1 Create `.github/workflows/publish.yml`

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - "v*"  # Trigger on version tags (v1.0.0, v1.1.0, etc.)

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build distributions
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

### 6.2 Add PyPI Token to GitHub Secrets

1. Go to repository **Settings -> Secrets and variables -> Actions**
2. Click **New repository secret**
3. Name: `PYPI_API_TOKEN`
4. Value: Your PyPI API token
5. Save

### 6.3 Publish New Versions

```bash
# Update version in pyproject.toml
# Edit pyproject.toml: version = "1.1.0"

# Commit changes
git add .
git commit -m "Bump version to 1.1.0"

# Create and push tag
git tag -a v1.1.0 -m "Version 1.1.0: Add feature X"
git push origin main
git push origin v1.1.0

# GitHub Actions automatically builds and publishes!
```

## Step 7: Version Management

### 7.1 Update Version for New Releases

Before building, update `pyproject.toml`:

```toml
[project]
version = "1.1.0"  # Increment version
```

Also update in `src/__init__.py` (optional but good practice):

```python
__version__ = "1.1.0"
```

### 7.2 Versioning Strategy

Follow Semantic Versioning 2.0.0:

| Version | When | Example |
|---------|------|---------|
| MAJOR | Breaking API changes | 1.0.0 → 2.0.0 |
| MINOR | New features (backward compatible) | 1.0.0 → 1.1.0 |
| PATCH | Bug fixes | 1.0.0 → 1.0.1 |

### 7.3 Changelog Management

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2024-02-23

### Added
- New advanced monitoring dashboard
- Support for Redis caching layer
- Enhanced security with JWT refresh tokens

### Fixed
- Critical bug in connection pooling
- Database migration race condition

### Changed
- Updated dependencies to latest versions

## [1.0.0] - 2024-02-22

### Added
- Initial production-ready release
- Full Docker/Docker Compose setup
- Prometheus + Grafana monitoring
- Sentry error tracking
```

## Step 8: Documentation and Discovery

### 8.1 Package Documentation

Update `README.md` with PyPI instruction:

```markdown
## Installation

### Via pip (Recommended)

```bash
pip install fastapi-default
```

### From source

```bash
git clone https://github.com/yourusername/fastapi-default.git
cd fastapi-default
pip install -e .
```
```

### 8.2 Submit to Awesome Lists

- [Awesome FastAPI](https://github.com/mjhea0/awesome-fastapi)
- [Awesome Python](https://github.com/vinta/awesome-python)
- [Awesome Python Templates](https://github.com/topics/fastapi-template)

### 8.3 Add PyPI Badge to README

```markdown
[![PyPI Version](https://img.shields.io/pypi/v/fastapi-default.svg)](https://pypi.org/project/fastapi-default/)
[![Python Versions](https://img.shields.io/badge/python-3.11%2B-blue)](https://pypi.org/project/fastapi-default/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
```

## Troubleshooting

### Issue: `twine upload` fails with "401 Client Error: Unauthorized"

**Solution**: 
- Verify PyPI token is correct
- Ensure token is added to `~/.pypirc`
- Check token is scoped to entire repository

### Issue: Package name already taken on PyPI

**Solution**:
- Choose different name in `pyproject.toml`
- Check PyPI policy on package naming
- Contact PyPI support for disputes

### Issue: "Invalid distribution on upload"

**Solution**:
- Run: `twine check dist/*`
- Verify all required fields in `pyproject.toml`
- Check `README.md` for rendering errors (use ReStructuredText or Markdown)

### Issue: Dependencies not working after pip install

**Solution**:
- Verify `dependencies` list in `pyproject.toml`
- Test with fresh virtual environment
- Run: `pip install fastapi-default[all]` for optional dependencies

## Quick Reference: Publishing Checklist

```bash
# Initial setup (one-time)
☐ Create GitHub account and repository
☐ Create PyPI and TestPyPI accounts
☐ Generate API tokens for both
☐ Create ~/.pypirc with credentials
☐ Set up GitHub Actions workflow

# For each release
☐ Update version in pyproject.toml
☐ Update CHANGELOG.md
☐ Test locally with pytest
☐ Commit changes: git commit -m "Release v1.x.x"
☐ Create git tag: git tag -a v1.x.x -m "Release description"
☐ Push to GitHub: git push origin main && git push origin v1.x.x
☐ GitHub Actions automatically builds and publishes
☐ Verify package at pypi.org/project/fastapi-default/
☐ Test installation: pip install fastapi-default

# Post-release
☐ Create GitHub release with changelog
☐ Announce on Twitter/LinkedIn/etc.
☐ Submit to awesome-lists
☐ Update documentation with new features
```

## Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging Authority](https://www.pypa.io/)
- [TestPyPI](https://test.pypi.org/)

## Next Steps

1. ✅ Update `pyproject.toml` metadata
2. ✅ Create GitHub repository
3. ✅ Build distribution packages
4. ✅ Test on TestPyPI
5. ✅ Publish to production PyPI
6. ✅ Set up GitHub Actions automation
7. ✅ Update documentation
8. ✅ Submit to awesome-lists

---

**Your package will be installable via: `pip install fastapi-default`** 🚀
