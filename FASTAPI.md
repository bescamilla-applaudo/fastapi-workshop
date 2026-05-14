# FastAPI: From Zero to AI Engineer
> **Context:** Theoretical reference for building production APIs with FastAPI, SQLAlchemy 2.0 async, JWT, and modular structure. Use INSTRUCTIONS.md as the hands-on guide.
>
> **Your advantage:** FastAPI validates types automatically, generates Swagger documentation effortlessly, and its async API is ideal for modern services. If you know basic Python, you're already 80% of the way there.
>
> **Source:** Plan built with Context7 from official FastAPI documentation (fastapi.tiangolo.com).
>
> **Methodology:** Each phase has real code, a concept explanation, and a practice with measurable success criteria.

---

## The Mental Map: Key FastAPI Concepts

```
Concept                              What it does
──────────────────────────────────────────────────────
@router.get("/users")                Defines a GET endpoint
async def handler(body: Schema)      Typed and validated request body
async def handler(id: int)           Path param with explicit type
async def handler(page: int = 1)     Query param with default value
Depends(my_function)                 Dependency injection (DB, auth)
app.include_router(router)           Mount modular routes
raise HTTPException(404)             HTTP error with specific code
Pydantic BaseModel                   Automatic data validation
/docs (Swagger)                      Automatic interactive documentation
pydantic-settings BaseSettings       Configuration from environment variables
```

---

## Phase 1 — Fundamentals: Your First API
**Estimated duration:** 1-2 days
**Goal:** Functional API with Swagger at `/docs`, validated request bodies, and well-formatted errors.

### 1.1 The minimal app
```python
# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

# lifespan = equivalent to app.listen() + setup/teardown
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up...")   # before receiving requests
    yield
    print("🛑 Shutting down...")  # after the app closes

app = FastAPI(
    title="My API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

```bash
# Run in development
uv run fastapi dev main.py       # with hot reload
# or
uvicorn main:app --reload        # equivalent

# View Swagger: http://localhost:8000/docs
# View OpenAPI JSON: http://localhost:8000/openapi.json
```

### 1.2 Path params, Query params, and Request Body
```python
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

# Path parameter — /items/42
@app.get("/items/{item_id}")
async def get_item(
    item_id: Annotated[int, Path(gt=0, description="Item ID")]
):
    return {"item_id": item_id}

# Query parameters — /items?page=2&limit=10&active=true
@app.get("/items")
async def list_items(
    page: int = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    active: bool | None = None,
):
    return {"page": page, "limit": limit, "active": active}

# Request body (Pydantic) — POST /items with JSON body
class ItemCreate(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.post("/items", status_code=201)
async def create_item(item: ItemCreate):
    # item.name, item.price are automatically validated
    return {"created": item.model_dump()}
```

### 1.3 HTTPException — how to raise errors
```python
from fastapi import HTTPException, status

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    item = fake_db.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item
```

### Practice 1 — Notes API (no database)
```
fastapi-workshop/practice1/
├── main.py           # FastAPI app + lifespan
├── schemas.py        # NoteCreate, NoteResponse (Pydantic)
├── router.py         # APIRouter with GET /notes, POST /notes, DELETE /notes/{id}
└── storage.py        # in-memory dict as "database"
```

**Success criteria:**
- [ ] Swagger at `http://localhost:8000/docs` shows all endpoints
- [ ] POST with invalid body returns 422 automatically (without writing error code)
- [ ] GET for a nonexistent ID returns 404 with a clear message

---

## Phase 2 — Modular Structure
**Estimated duration:** 2 days
**Goal:** Understand why the API has `api/`, `core/`, `schemas/`, `crud/` folders and be able to navigate the code without getting lost.

### 2.1 APIRouter — modular routes
```python
# api/v1/endpoints/notes.py
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/", response_model=list[NoteResponse])
async def list_notes():
    ...

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note_in: NoteCreate):
    ...

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int):
    ...
```

```python
# api/v1/app.py — the "router index"
from fastapi import FastAPI
from .endpoints import notes, users, products

v1_app = FastAPI()
v1_app.include_router(notes.router)
v1_app.include_router(users.router)
v1_app.include_router(products.router)
```

```python
# main.py — mounts v1 as a sub-application
from fastapi import FastAPI
from app.api.v1.app import v1_app

app = FastAPI()
app.mount("/v1", v1_app)

# Result:
# GET /v1/notes/
# POST /v1/notes/
# DELETE /v1/notes/{id}
```

### 2.2 The API structure (and why)
```
app/
├── main.py              # Entry point: creates the app, mounts middlewares, includes routers
├── api/
│   └── v1/
│       ├── app.py       # Groups all v1 routers
│       └── endpoints/   # One file per resource (users.py, products.py)
├── core/
│   ├── config.py        # Settings with pydantic-settings (environment variables)
│   ├── database.py      # AsyncSession factory, get_db dependency
│   └── security.py      # JWT: create token, validate token, get_current_user
├── models/              # SQLAlchemy ORM models (DB tables)
├── schemas/             # Pydantic schemas (request/response bodies)
├── crud/                # DB operations (select, insert, update, delete)
└── services/            # More complex business logic (calls crud + external APIs)
```

**The data flow rule in a professional API:**
```
Request JSON → Schema (Pydantic validates) → Endpoint → CRUD (SQLAlchemy) → DB
                                                    ↓
Response JSON ← Schema (serialization) ← Endpoint ← CRUD ← DB
```

### 2.3 Settings with pydantic-settings (like `app/core/config.py`)
```python
# core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Environment variables — if missing, clear error on startup
    database_url: str
    secret_key: str
    
    # With default values
    api_v1_prefix: str = "/v1"
    access_token_expire_minutes: int = 30
    debug: bool = False

    # Reads automatically from .env
    model_config = {"env_file": ".env", "case_sensitive": False}

# Cached singleton — initialized only once
@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

---

## Phase 3 — Dependency Injection (The Most Powerful Concept)
**Estimated duration:** 2-3 days
**Goal:** Master `Depends()` — the tool that makes FastAPI so elegant.

### 3.1 What is Depends()?
```python
# WITHOUT Depends — repeated code in every endpoint
@router.get("/items")
async def list_items():
    token = request.headers.get("Authorization")  # manual
    user = validate_token(token)                   # manual
    if not user:
        raise HTTPException(401)
    db = get_db_connection()                        # manual
    items = db.query(Item).all()
    db.close()                                      # manual
    return items

# WITH Depends — one line, everything automated
@router.get("/items")
async def list_items(
    current_user = Depends(get_current_active_user),  # automatic auth
    db: AsyncSession = Depends(get_db),               # automatic DB session
):
    return await crud.get_items(db)
```

### 3.2 How it chains in a professional API (Depends within Depends)
```python
# Level 1: extracts the token from the header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

# Level 2: validates the token and looks up the user in DB
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await crud.get_user(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Level 3: verifies that the user is active
async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Endpoint — receives the user already validated through 3 layers
@router.get("/me")
async def read_profile(
    user = Depends(get_current_active_user)
):
    return user
```

### 3.3 DB Dependency with AsyncSession
```python
# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(settings.database_url, echo=settings.debug)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# This is the dependency that all endpoints use
async def get_db():
    async with SessionLocal() as session:
        yield session  # yield delivers the session to the endpoint and cleans up when done
        # The session is automatically closed when the request ends
```

---

## Phase 4 — JWT Authentication
**Estimated duration:** 2-3 days
**Goal:** Implement the same OAuth2 flow as `app/core/security.py`.

### 4.1 Complete authentication flow
```python
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

SECRET_KEY = "your-very-long-secret-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

class Token(BaseModel):
    access_token: str
    token_type: str

# Password hash — like create_password_hash in a professional API
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Create JWT — like create_access_token in a professional API
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Login endpoint — POST /v1/auth/login
@router.post("/auth/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=token, token_type="bearer")
```

---

## Phase 5 — Middleware, CORS, and Background Tasks
**Estimated duration:** 1-2 days
**Goal:** Understand how API security is configured and background processing works.

### 5.1 CORS — why it exists and how to configure it
```python
# main.py — as configured in the API to allow FE requests
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # only the FE in dev
    allow_credentials=True,                   # allows cookies and auth headers
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.2 Custom middleware (request logging)
```python
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")
    return response
```

### 5.3 Background Tasks — run work after responding
```python
from fastapi import BackgroundTasks

# The heavy work (email, notifications, logging to DB)
async def send_welcome_email(email: str, name: str):
    await email_service.send(to=email, subject=f"Welcome {name}")

@router.post("/users", status_code=201)
async def create_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    user = await crud.create_user(db, user_in)
    # The email is sent AFTER the client receives the 201
    background_tasks.add_task(send_welcome_email, user.email, user.name)
    return user
```

### 5.4 Global Exception Handlers
```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Custom 422 — when Pydantic fails
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": exc.body
        }
    )

# Custom exception — for business errors
class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id

@app.exception_handler(ResourceNotFoundError)
async def not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": f"{exc.resource} with id {exc.id} not found"}
    )
```

---

## Phase 6 — Testing FastAPI
**Estimated duration:** 2-3 days
**Goal:** Be able to run `pytest` on the API and understand the existing tests.

### 6.1 Async test setup
```python
# conftest.py — shared fixtures (global setup for all tests)
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import get_db
from app.models.base import Base

# In-memory test DB
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()  # cleans up after each test

@pytest.fixture
async def client(db_session):
    # Override the DB dependency to use the test one
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
```

### 6.2 Endpoint tests
```python
# tests/test_notes.py
import pytest

@pytest.mark.anyio
async def test_create_note(client):
    response = await client.post("/v1/notes/", json={
        "title": "Test Note",
        "content": "Hello World"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert "id" in data

@pytest.mark.anyio
async def test_create_note_invalid_body(client):
    # Invalid body — Pydantic should reject it with 422
    response = await client.post("/v1/notes/", json={"content": ""})
    assert response.status_code == 422

@pytest.mark.anyio
async def test_get_nonexistent_note(client):
    response = await client.get("/v1/notes/99999")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_protected_endpoint_without_token(client):
    response = await client.get("/v1/users/me")
    assert response.status_code == 401
```

---

## Phase 7 — The Final Project: Complete Ideas API
**Estimated duration:** 5-7 days
**Goal:** Build a professional API that integrates all learned concepts.

### Final project structure
```
fastapi-workshop/final-project/
├── .env
├── pyproject.toml
├── alembic.ini
├── alembic/
│   └── versions/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── app.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── users.py
│   │           └── ideas.py       # the main resource
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   └── idea.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── idea.py
│   └── crud/
│       ├── user.py
│       └── idea.py
└── tests/
    ├── conftest.py
    ├── test_auth.py
    └── test_ideas.py
```

### Functionality to implement
- [ ] `POST /v1/auth/register` — create user with hashed password
- [ ] `POST /v1/auth/login` — returns JWT
- [ ] `GET /v1/users/me` — authenticated user's profile
- [ ] `POST /v1/ideas/` — create idea (requires auth)
- [ ] `GET /v1/ideas/` — list authenticated user's ideas
- [ ] `GET /v1/ideas/{id}` — idea detail
- [ ] `PUT /v1/ideas/{id}` — update idea (owner only)
- [ ] `DELETE /v1/ideas/{id}` — delete idea (owner only)

**Success criteria:**
- [ ] Swagger at `/v1/docs` shows all endpoints with documentation
- [ ] Protected endpoints return 401 without a token
- [ ] Tests run with `pytest` and all pass
- [ ] Running `alembic upgrade head` creates the tables correctly

---

## Verification Checklist

### Did I complete Phase 1?
- [ ] I can create an endpoint with path params, query params, and body without looking at docs
- [ ] Swagger is generated automatically and I can test endpoints from there
- [ ] Validation errors return 422 automatically

### Did I complete Phase 2?
- [ ] I understand the difference between `models/`, `schemas/`, `crud/`, and `services/`
- [ ] I can read any file in `app/` and understand its purpose
- [ ] I know how the v1 router is mounted in `main.py`

### Did I complete Phase 3?
- [ ] I can explain `Depends()` in my own words
- [ ] I can trace how authentication is validated from the header to the endpoint
- [ ] I know what `yield` does inside a DB dependency

### Did I complete Phases 4-5?
- [ ] I can implement login with JWT without copying code
- [ ] I understand why CORS is needed and which FE endpoints require it
- [ ] I know when to use BackgroundTasks vs a synchronous endpoint

### Did I complete Phase 6?
- [ ] I can run `pytest tests/ -v` and the tests pass
- [ ] I can write a test for a new endpoint that I added
- [ ] I understand `dependency_overrides` and why it's used in tests

### Did I complete the Final Project?
- [ ] My API has professional modular architecture
- [ ] I can add a new endpoint in less than 30 minutes
- [ ] I can do a code review of a FastAPI API with real technical criteria

---

## Quick Reference: Files by concept

| Concept | File |
|---|---|
| How the app is mounted | `app/main.py` |
| How routers are included | `app/api/v1/router.py` |
| How `.env` is read | `app/core/config.py` |
| How DB session works | `app/core/database.py` |
| How JWT works | `app/core/security.py` |
| How authentication is validated | `app/api/v1/endpoints/auth.py` |
| How an endpoint is structured | `app/api/v1/endpoints/` (any file) |
| How schemas are defined | `app/schemas/` (any file) |
| How dependencies are injected | `app/dependencies.py` |

---

> **Rule of this workshop:** If something doesn't work, open Swagger at `/docs` first. Swagger always shows the exact contract the API expects — it's your number one debugging tool.
