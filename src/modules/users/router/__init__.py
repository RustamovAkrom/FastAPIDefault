from fastapi import APIRouter

from .api.v1 import *  # noqa

router = APIRouter(prefix="/users", tags=["Users"])

# There should your api routers
