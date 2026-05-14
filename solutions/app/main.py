"""FastAPI Workshop — Solution: Complete Ideas API.

This is the reference implementation with all phases completed:
- Modular structure with APIRouter
- Async SQLAlchemy with SQLite
- JWT authentication
- Logging middleware
- CORS configured
- Custom exception handlers
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import engine
from app.models.base import Base
from app.api.v1.router import v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Ideas API",
    description="API for managing startup ideas",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")
    return response


class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, resource_id: int):
        self.resource = resource
        self.resource_id = resource_id


@app.exception_handler(ResourceNotFoundError)
async def not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"{exc.resource} with id {exc.resource_id} not found"},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(v1_router)
