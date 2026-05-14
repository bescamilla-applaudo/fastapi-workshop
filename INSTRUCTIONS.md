# FastAPI Workshop — AI-First Guide

> **Recommended model:** Gemini 3 Flash (0.33x multiplier) for learning chat.
> For complex generation tasks: Claude Sonnet 4.6 or GPT-5.4.
>
> **How to use this file:** Each phase has ready-to-use prompts for Copilot Chat.
> Copy the prompt, send it, read the generated response, run the validation command.
> If you get stuck: `solutions/` has the complete reference implementation.
>
> **Project:** You're building an **Ideas API** — startup idea management with auth, DB, and tests.

---

## Initial setup (one time only)

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Copy environment variables
cp .env.example .env

# 4. Verify the app starts
uvicorn app.main:app --reload
# → open http://localhost:8000/docs — you should see Swagger with only /health
```

**Validation:** `curl http://localhost:8000/health` returns `{"status":"ok"}`.

---

## Phase 1 — Your first endpoint (in-memory CRUD)
**Goal:** Understand endpoints, path params, query params, request body, and status codes.

### Exercise 1.1 — Explore Swagger

> **Prompt (copy verbatim to Copilot Chat):**
> ```
> Explain what Swagger/OpenAPI is and why FastAPI generates it automatically.
> ```

Open `http://localhost:8000/docs` and try the `/health` endpoint from there.

### Exercise 1.2 — In-memory CRUD endpoints

> **Prompt (copy verbatim):**
> ```
> In app/main.py, add CRUD endpoints for "ideas" using in-memory storage
> (a list of dicts). Each idea has: id (auto-incrementing int), title (str),
> description (str, default ""), category (str, default "general").
>
> Endpoints to create:
> 1. POST /ideas — creates an idea, returns 201
> 2. GET /ideas — lists all, accepts query param ?category= to filter
> 3. GET /ideas/{idea_id} — returns one idea, 404 if not found
> 4. DELETE /ideas/{idea_id} — deletes an idea, returns 204, 404 if not found
>
> Use HTTPException for 404s. Import status from fastapi for status codes.
> Then explain: why does FastAPI validate path param types automatically?
> ```

**Validation:**
```bash
# The app should auto-reload. Test in Swagger:
# 1. POST /ideas with {"title": "My first idea"} → 201
# 2. GET /ideas → list with 1 element
# 3. GET /ideas/1 → the created idea
# 4. GET /ideas/999 → 404
# 5. DELETE /ideas/1 → 204
# 6. GET /ideas → empty list
```

### Exercise 1.3 — Understand automatic validation

> **Prompt:**
> ```
> In Swagger, try POST /ideas with an empty body {}. What happens?
> Now try GET /ideas/abc (string instead of int). What error do you get?
> Explain how FastAPI validates this without me writing any validation code.
> ```

---

## Phase 2 — Schemas with Pydantic
**Goal:** Separate validation from endpoints using Pydantic BaseModel.

> **Prompt (copy verbatim):**
> ```
> Refactor the endpoints in app/main.py to use Pydantic schemas.
>
> Create in app/main.py (everything in the same file for now) these classes:
> - IdeaCreate(BaseModel): title (str, min 1 char, max 200), description (str, default ""),
>   category (str, default "general", max 50)
> - IdeaResponse(BaseModel): id, title, description, category
>
> Update the endpoints to:
> - POST /ideas receives IdeaCreate as body and returns IdeaResponse
> - GET /ideas returns list[IdeaResponse]
> - GET /ideas/{id} returns IdeaResponse
> - Use response_model on each endpoint
>
> Explain: what happens if the client sends extra fields not in IdeaCreate?
> And if they send title with 0 characters?
> ```

**Validation:**
```bash
# In Swagger:
# 1. POST /ideas with {"title": ""} → 422 (min_length validation)
# 2. POST /ideas with {"title": "X", "extra_field": true} → 201 (extra ignored)
# 3. The GET /ideas response shows only IdeaResponse fields
```

### Exercise 2.2 — Custom validators

> **Prompt:**
> ```
> Add a validator to IdeaCreate that rejects titles containing only whitespace
> (e.g., "   "). Use @field_validator from Pydantic v2.
> Also add an optional field is_public: bool = False.
> ```

---

## Phase 3 — Modular structure with APIRouter
**Goal:** Reorganize the code into modules like a professional API.

> **Prompt (copy verbatim):**
> ```
> Refactor the Ideas API to use a modular structure. Move the code from app/main.py
> to this structure:
>
> app/
> ├── main.py              ← only FastAPI(), health check, include_router
> ├── schemas/
> │   ├── __init__.py
> │   └── idea.py          ← IdeaCreate, IdeaResponse (move from main.py)
> └── api/
>     ├── __init__.py
>     └── v1/
>         ├── __init__.py
>         ├── router.py    ← v1_router that includes the endpoints
>         └── endpoints/
>             ├── __init__.py
>             └── ideas.py ← endpoints with APIRouter(prefix="/ideas")
>
> Requirements:
> - main.py imports v1_router and includes it with prefix="/api/v1"
> - ideas.py uses router = APIRouter(prefix="/ideas", tags=["ideas"])
> - Schemas are imported from app.schemas.idea
> - In-memory storage stays in ideas.py (we'll change it in Phase 4)
>
> Then explain: why use /api/v1/ versioning from the start?
> ```

**Validation:**
```bash
# Restart uvicorn if it didn't detect the new files:
uvicorn app.main:app --reload

# In Swagger (http://localhost:8000/docs):
# - Endpoints are now at /api/v1/ideas/
# - POST /api/v1/ideas/ → 201
# - GET /api/v1/ideas/ → list
# - The "ideas" tag groups the endpoints in Swagger
```

### Exercise 3.2 — Compare with the solution

> **Prompt:**
> ```
> Open solutions/app/api/v1/router.py and solutions/app/api/v1/endpoints/ideas.py.
> Compare the structure with what you generated. What differences are there?
> ```

---

## Phase 4 — Database with async SQLAlchemy
**Goal:** Replace in-memory storage with SQLite + SQLAlchemy.

### Exercise 4.1 — Configuration and models

> **Prompt (copy verbatim):**
> ```
> Add async SQLAlchemy with SQLite to the Ideas API.
>
> Create these files:
>
> 1. app/core/__init__.py (empty)
> 2. app/core/config.py — Settings with pydantic-settings:
>    - database_url: str (default "sqlite+aiosqlite:///./ideas.db")
>    - secret_key: str (default "change-me...")
>    - debug: bool (default False)
>    - Use model_config with env_file=".env"
>    - get_settings() function with @lru_cache
>
> 3. app/core/database.py — engine and session setup:
>    - create_async_engine with settings.database_url
>    - async_sessionmaker with AsyncSession
>    - Async get_db() function that yields a session (with commit/rollback)
>
> 4. app/models/__init__.py (empty)
> 5. app/models/base.py — DeclarativeBase
> 6. app/models/idea.py — Idea model with:
>    - id (int, primary key)
>    - title (String 200)
>    - description (Text, default "")
>    - category (String 50, default "general")
>    - is_public (bool, default False)
>    - created_at, updated_at (DateTime with timezone)
>
> 7. Update app/main.py:
>    - Add lifespan that does create_all on startup and dispose on shutdown
>
> Explain: why use async_sessionmaker instead of regular sessionmaker?
> What advantage does it have over the synchronous ORM?
> ```

### Exercise 4.2 — Endpoints with DB

> **Prompt:**
> ```
> Update app/api/v1/endpoints/ideas.py to use SQLAlchemy instead of the in-memory
> list.
>
> Each endpoint should:
> - Receive db: AsyncSession = Depends(get_db)
> - Use select(), db.add(), db.delete(), db.flush(), db.refresh()
> - POST returns 201 with the created idea (refresh to get the generated id)
> - GET lists with order_by(created_at.desc()) and optional category filter
> - GET /{id} with scalar_one_or_none() and 404 if None
> - DELETE with 204
>
> Also add PUT /ideas/{id} for updates (using model_dump(exclude_unset=True)).
>
> Create an IdeaUpdate schema with all optional fields for PUT.
> ```

**Validation:**
```bash
# Restart uvicorn. The first time it creates ideas.db automatically.
uvicorn app.main:app --reload

# In Swagger:
# 1. POST /api/v1/ideas/ with {"title": "Persistent"} → 201 (now has created_at)
# 2. Restart uvicorn → GET /api/v1/ideas/ → the idea is still there (persisted in SQLite)
# 3. PUT /api/v1/ideas/1 with {"title": "Updated"} → 200
# 4. DELETE /api/v1/ideas/1 → 204
```

### Exercise 4.3 — Inspect the DB

> **Prompt:**
> ```
> How can I see the contents of ideas.db from the terminal?
> Give me the command to inspect the tables and view the data.
> ```

---

## Phase 5 — JWT Authentication
**Goal:** Add users, registration, login, and protected endpoints.

> **Switch model → Claude Sonnet 4.6 or GPT-5.4**
> This phase generates 8 interrelated files with JWT, bcrypt, OAuth2, and SQLAlchemy relationships.
> Gemini 3 Flash often omits security details or breaks the relationships between models.

### Exercise 5.1 — User model and schemas

> **Prompt (copy verbatim):**
> ```
> Add JWT authentication to the Ideas API.
>
> Create these files:
>
> 1. app/core/security.py:
>    - hash_password(password) → str (uses passlib with bcrypt)
>    - verify_password(plain, hashed) → bool
>    - create_access_token(data, expires_delta) → str (uses python-jose)
>    - decode_access_token(token) → dict | None
>    - Uses settings.secret_key and HS256 algorithm
>
> 2. app/models/user.py — User model:
>    - id, email (unique, indexed), hashed_password, is_active, created_at
>    - Relationship: ideas = relationship(back_populates="owner")
>
> 3. Update app/models/idea.py:
>    - Add owner_id (ForeignKey to users.id)
>    - Add owner = relationship(back_populates="ideas")
>
> 4. app/schemas/user.py:
>    - UserCreate: email (EmailStr), password (min 6 chars)
>    - UserResponse: id, email, is_active (with from_attributes=True)
>    - Token: access_token, token_type="bearer"
>
> 5. app/api/v1/endpoints/auth.py with router prefix="/auth":
>    - POST /register → creates user, returns UserResponse (201). 409 if email exists.
>    - POST /login → accepts OAuth2PasswordRequestForm, returns Token. 401 if invalid credentials.
>
> 6. app/dependencies.py — get_current_user():
>    - Uses OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
>    - Decodes token, finds user, returns User or 401
>
> 7. Update ideas.py: all endpoints require current_user = Depends(get_current_user)
>    - POST assigns owner_id = current_user.id
>    - GET/PUT/DELETE filter by owner_id (only your ideas)
>
> 8. Include auth.router in v1_router
>
> Explain: why does OAuth2PasswordRequestForm use "username" and not "email"?
> ```

**Validation:**
```bash
# Restart uvicorn (delete ideas.db to recreate tables with users):
rm -f ideas.db && uvicorn app.main:app --reload

# In Swagger:
# 1. POST /api/v1/auth/register with {"email": "test@demo.com", "password": "secret123"} → 201
# 2. POST /api/v1/auth/login with form data (username=test@demo.com, password=secret123) → Token
# 3. Click "Authorize" in Swagger → paste the token
# 4. POST /api/v1/ideas/ → 201 (now has owner_id)
# 5. Without token: POST /api/v1/ideas/ → 401
```

### Exercise 5.2 — Test user isolation

> **Prompt:**
> ```
> Register a second user (user2@demo.com) and create an idea with each one.
> Verify that GET /api/v1/ideas/ only returns the logged-in user's ideas.
> What happens if I try PUT /api/v1/ideas/1 with user2's token (who isn't the owner)?
> ```

---

## Phase 6 — Middleware, CORS, and error handling
**Goal:** Add cross-cutting infrastructure layers.

> **Prompt (copy verbatim):**
> ```
> Add middleware, CORS, and error handling to the Ideas API.
>
> In app/main.py:
>
> 1. Logging middleware:
>    - Logs each request: "METHOD /path → STATUS (duration)"
>    - Uses time.perf_counter() to measure duration
>
> 2. CORS:
>    - Allows origin http://localhost:3000 (a future web client)
>    - Allows credentials, all methods and headers
>
> 3. Custom exception handler:
>    - Create a ResourceNotFoundError(resource, resource_id) class
>    - Register an exception_handler that returns 404 with a descriptive message
>
> Explain: why is CORS needed when the web client and API are on different
> ports? What would happen without the CORS middleware?
> ```

**Validation:**
```bash
# Make any request and observe the log in the uvicorn terminal:
# POST /api/v1/ideas/ → 201 (0.005s)

# Test CORS with curl:
curl -i -X OPTIONS http://localhost:8000/api/v1/ideas/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"
# Should return Access-Control-Allow-* headers
```

---

## Phase 7 — Testing with pytest
**Goal:** Write automated tests for the entire API.

### Exercise 7.1 — Test setup

> **Switch model → Claude Sonnet 4.6 or GPT-5.4**
> Async fixtures with `dependency_overrides`, `anyio`, and in-memory SQLite require precise
> reasoning about the session lifecycle. Gemini 3 Flash tends to generate fixtures with state leaks.

> **Prompt (copy verbatim):**
> ```
> Create the testing setup for the Ideas API.
>
> tests/conftest.py should have:
>
> 1. Fixture test_engine — create_async_engine with in-memory SQLite
>    (sqlite+aiosqlite:///:memory:), create_all in setup, drop_all in teardown
>
> 2. Fixture db_session — async_sessionmaker from test_engine, yield session, rollback
>
> 3. Fixture client — AsyncClient with ASGITransport(app=app),
>    override get_db with the test db_session, clear overrides in teardown
>
> 4. Fixture test_user — creates a User with email "test@example.com" and hashed password
>
> 5. Fixture auth_headers — logs in with test_user and returns
>    {"Authorization": "Bearer <token>"}
>
> Use @pytest.mark.anyio on tests. Import AsyncClient from httpx.
>
> Then explain: why use dependency_overrides instead of connecting
> to the real DB in tests?
> ```

### Exercise 7.2 — Auth tests

> **Prompt:**
> ```
> Create tests/test_auth.py with these tests (all use the client fixture):
>
> 1. test_register_user — registers user, verifies 201 and that it returns email without password
> 2. test_register_duplicate_email — tries to register existing email, verifies 409
> 3. test_register_invalid_email — invalid email, verifies 422
> 4. test_register_short_password — password < 6 chars, verifies 422
> 5. test_login_success — correct login, verifies token in response
> 6. test_login_wrong_password — wrong password, verifies 401
> 7. test_login_nonexistent_user — nonexistent user, verifies 401
>
> Each test is independent. Use the conftest.py fixtures.
> ```

### Exercise 7.3 — Ideas tests

> **Prompt:**
> ```
> Create tests/test_ideas.py with these tests (use client + auth_headers):
>
> 1. test_create_idea — creates idea, verifies 201 with correct data
> 2. test_create_idea_without_auth — without token, verifies 401
> 3. test_create_idea_empty_title — empty title, verifies 422
> 4. test_list_ideas — creates 2, lists them, verifies at least 2
> 5. test_list_ideas_filter_by_category — filters by category, verifies result
> 6. test_get_idea — creates and gets by id, verifies data
> 7. test_get_nonexistent_idea — nonexistent id, verifies 404
> 8. test_update_idea — creates, updates, verifies change
> 9. test_update_partial — updates only description, title doesn't change
> 10. test_delete_idea — creates, deletes (204), tries to get (404)
> 11. test_health_check — GET /health returns ok
>
> Each test is independent thanks to db_session with rollback.
> ```

**Validation:**
```bash
pytest tests/ -v
# All tests should pass. Expected: ~18 tests, 0 failures.
```

### Exercise 7.4 — Compare with the solution

> **Prompt:**
> ```
> Open solutions/tests/conftest.py and solutions/tests/test_ideas.py.
> Compare with my tests. What differences are there in the fixtures or assertions?
> ```

---

## Final project structure

```
fastapi-workshop/
├── app/                             ← YOUR WORK: you build this phase by phase
│   ├── __init__.py
│   ├── main.py                      ← Starter: just health check → grows each phase
│   ├── api/
│   │   └── v1/
│   │       ├── router.py            ← (Phase 3) v1 router
│   │       └── endpoints/
│   │           ├── auth.py           ← (Phase 5) register, login
│   │           └── ideas.py          ← (Phase 1→4) CRUD endpoints
│   ├── core/
│   │   ├── config.py                ← (Phase 4) Settings with pydantic-settings
│   │   ├── database.py              ← (Phase 4) AsyncEngine, get_db
│   │   └── security.py              ← (Phase 5) JWT, password hashing
│   ├── models/
│   │   ├── base.py                  ← (Phase 4) DeclarativeBase
│   │   ├── user.py                  ← (Phase 5) User model
│   │   └── idea.py                  ← (Phase 4) Idea model
│   ├── schemas/
│   │   ├── user.py                  ← (Phase 5) UserCreate, Token
│   │   └── idea.py                  ← (Phase 2) IdeaCreate, IdeaResponse
│   └── dependencies.py              ← (Phase 5) get_current_user
├── tests/                           ← YOUR WORK: tests (Phase 7)
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_ideas.py
├── solutions/                       ← REFERENCE: do not modify
│   ├── app/                         ← Complete implementation
│   └── tests/                       ← Complete tests
├── .github/
│   └── copilot-instructions.md      ← Backend Engineer persona
├── .vscode/mcp.json                 ← Context7
├── pyproject.toml                   ← Project dependencies
├── .env.example                     ← Example environment variables
├── PROGRESS.md                      ← Your progress tracking
└── FASTAPI.md                       ← Complete theory reference
```

---

## Quick commands

| Action | Command |
|---|---|
| Activate venv | `source .venv/bin/activate` |
| Install deps | `pip install -e ".[dev]"` |
| Start app | `uvicorn app.main:app --reload` |
| Swagger | `http://localhost:8000/docs` |
| Run tests | `pytest tests/ -v` |
| Single test | `pytest tests/test_auth.py::test_login_success -v` |
| Tests with output | `pytest tests/ -v -s` |
| Reset DB | `rm -f ideas.db && uvicorn app.main:app --reload` |
| Inspect DB | `sqlite3 ideas.db ".tables"` |

---

## Tips for Gemini 3 Flash

- Excellent for generating endpoints and schemas — follows the FastAPI pattern faithfully.
- If it generates incomplete code, add "Complete the entire file, no TODOs or placeholders".
- For conceptual explanations (DI, middleware, JWT), it works as well as more expensive models.
- If a prompt fails: re-send it with the uvicorn error pasted — Flash self-corrects well.
- For complex test generation (conftest with async fixtures), consider Claude Sonnet 4.6.
