from fastapi import APIRouter

from app.api.v1.endpoints import auth, ideas

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth.router)
v1_router.include_router(ideas.router)
