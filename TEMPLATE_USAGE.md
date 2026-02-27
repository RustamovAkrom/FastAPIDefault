# Using FastAPI-Default as a Project Template

This guide explains how to use `fastapi-default` as a starting point for your new FastAPI projects.

## 📌 Option 1: Clone and Customize (Fastest Method)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/fastapi-default.git my-new-api
cd my-new-api
```

### Step 2: Update Project Metadata

Edit the following files to customize for your project:

#### `pyproject.toml`

```toml
[project]
name = "my-new-api"              # Change package name
description = "My API description here"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]

[project.urls]
Homepage = "https://github.com/your-username/my-new-api"
Repository = "https://github.com/your-username/my-new-api.git"
Issues = "https://github.com/your-username/my-new-api/issues"
```

#### `.env.example`

```env
APP_NAME=my-new-api              # Change app name
APP_TITLE="My New API"           # Change title
POSTGRES_DB=my_new_api_db        # Change DB name
```

#### `README.md`

Update the following sections:
- Project title and description
- GitHub URLs (repository, issues)
- Installation instructions
- API usage examples
- Your contact information

### Step 3: Remove Template Artifacts

```bash
# Remove git history to start fresh
rm -rf .git
git init

# Remove or update these files as needed
rm -f PUBLISHING.md              # Unless you're publishing to PyPI
rm -f docs/BACKEND_ROADMAP.md   # Replace with your roadmap

# Update LICENSE with your name if needed
```

### Step 4: Customize Core Models

#### `src/db/models/`

Replace or extend the `dummy` models with your domain models:

```python
# src/db/models/product.py
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base

class Product(Base):
    """Product model for your domain."""
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    price: Mapped[float] = mapped_column(Float)
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
```

#### `src/db/crud/`

Create CRUD operations for your models:

```python
# src/db/crud/product.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models.product import Product

async def get_products(session: AsyncSession) -> list[Product]:
    """Get all products."""
    result = await session.execute(select(Product))
    return result.scalars().all()

async def create_product(session: AsyncSession, name: str, price: float) -> Product:
    """Create new product."""
    product = Product(name=name, price=price)
    session.add(product)
    await session.commit()
    return product
```

#### `src/schemas/`

Create Pydantic models for request/response:

```python
# src/schemas/product.py
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None

class ProductResponse(ProductBase):
    id: int
    
    class Config:
        from_attributes = True
```

### Step 5: Create API Endpoints

#### `src/api/api_v1/product.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dependencies import get_db
from src.db.crud import product as product_crud
from src.db.models.product import Product
from src.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    """List all products."""
    return await product_crud.get_products(db)

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new product."""
    return await product_crud.create_product(
        db, name=product_in.name, price=product_in.price
    )
```

Register router in `src/api/api_v1/__init__.py`:

```python
from fastapi import APIRouter
from src.api.api_v1 import dummy, product

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(dummy.router)
api_router.include_router(product.router)

__all__ = ["api_router"]
```

### Step 6: Create Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Create product table"

# Review the migration in src/db/migrations/versions/
# Apply migration
alembic upgrade head
```

### Step 7: Update Tests

Create tests for your new endpoints:

```python
# tests/test_product.py
import pytest

@pytest.mark.asyncio
async def test_create_product(async_client):
    """Test creating a product."""
    response = await async_client.post(
        "/api/v1/products/",
        json={"name": "Test Product", "price": 99.99}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Product"
```

### Step 8: Start Development

```bash
# Development with Docker
docker compose up -d

# Or local development
source .venv/bin/activate
uvicorn src.app:create_app --factory --reload
```

## 📌 Option 2: Install from PyPI (When Available)

```bash
pip install fastapi-default
```

Then follow template scaffolding (currently requires manual setup - CLI coming soon).

## 🔄 Syncing with Upstream

Keep your project updated with template improvements:

```bash
# Add upstream remote
git remote add upstream https://github.com/yourusername/fastapi-default.git

# Fetch latest changes
git fetch upstream

# Merge major improvements (careful: may have conflicts)
git merge upstream/main --no-commit --squash

# Review and resolve conflicts
git diff --cached

# Complete merge if satisfied
git commit -m "Merge upstream improvements"
```

## 🎨 Customization Examples

### Add Admin Dashboard

FastAPI-Default already includes SQLAdmin. Register your models:

```python
# src/admin/admin.py
from sqladmin import Admin, ModelView
from src.db.models.product import Product

class ProductAdmin(ModelView, model=Product):
    column_list = [Product.id, Product.name, Product.price]
    column_editable_list = ["name", "price"]
    column_filters = ["name", "price"]
```

### Add Async BG Tasks

```python
# src/services/celery_worker.py (if using Celery)
from celery import Celery

celery = Celery("my-api")

@celery.task
def process_product(product_id: int):
    """Background task processing."""
    pass
```

### Add Logging

Already configured with Loguru:

```python
from src.core.logger import logger

logger.info("Product created", product_id=123, price=99.99)
logger.error("Database error", error="Connection timeout")
```

### Add Caching

Example with Redis:

```python
# src/core/cache.py
import redis.asyncio as redis

cache = await redis.from_url("redis://localhost")
await cache.set("key", "value", ex=3600)  # 1 hour expiry
```

### Add Email Notifications

```python
# src/services/email.py
from fastapi_mail import FastMail, MessageSchema

# Configuration and send implementation
```

## 📚 Project Structure After Customization

```
your-project/
├── src/
│   ├── db/
│   │   ├── models/
│   │   │   ├── product.py       # ← Your models
│   │   │   └── order.py         # ← Your models
│   │   └── crud/
│   │       ├── product.py       # ← Your CRUD ops
│   │       └── order.py         # ← Your CRUD ops
│   ├── api/
│   │   └── api_v1/
│   │       ├── product.py       # ← Your endpoints
│   │       └── order.py         # ← Your endpoints
│   └── schemas/
│       ├── product.py           # ← Your DTOs
│       └── order.py             # ← Your DTOs
├── tests/
│   ├── test_product.py          # ← Your tests
│   └── test_order.py            # ← Your tests
└── docs/
    ├── API.md                   # ← Your API docs
    └── MODELS.md                # ← Your data model docs
```

## ✅ Pre-Launch Checklist

Before deploying your customized project:

- ✅ Update all environment variables in `.env.example`
- ✅ Review and customize configuration in `src/core/settings.py`
- ✅ Create database migrations for all models
- ✅ Write tests for all endpoints (aim for 80%+ coverage)
- ✅ Update README.md with your API documentation
- ✅ Configure SECRET_KEY and other secrets (don't commit!)
- ✅ Update CONTRIBUTING.md for your project
- ✅ Test locally with Docker Compose
- ✅ Set up GitHub Actions for CI/CD (template available)
- ✅ Configure Sentry for error tracking
- ✅ Set up Prometheus/Grafana monitoring

## 🚀 Next Steps

1. **Option 1 Users**: Follow steps 1-8 above
2. **Option 2 Users**: Clone the repository via GitHub
3. Start implementing your domain models
4. Create API endpoints for your use cases
5. Write comprehensive tests
6. Deploy using provided Docker/Kubernetes configs
7. Monitor with Prometheus/Grafana stack

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Happy building! Let us know if you have questions about customizing the template.** 🎉
