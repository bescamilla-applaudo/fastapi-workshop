# FastAPI Workshop — My Progress

> **How to use this file:**
> Update the checkboxes `[ ]` → `[x]` as you complete each item.
> When you resume the workshop, tell Copilot:
> _"Check PROGRESS.md and let's continue from where I left off"_
>
> **Model:** Gemini 3 Flash for chat. Claude Sonnet 4.6 for complex generation.

---

## Current status

**Active phase:** Setup — Configure the environment
**Last action:** Workshop configured, ready to start

---

## Setup

- [ ] Created the venv: `python3 -m venv .venv && source .venv/bin/activate`
- [ ] Installed dependencies: `pip install -e ".[dev]"`
- [ ] Copied .env: `cp .env.example .env`
- [ ] Started the app: `uvicorn app.main:app --reload`
- [ ] Verified Swagger at `http://localhost:8000/docs` — only shows /health

**Validation:** `curl http://localhost:8000/health` → `{"status":"ok"}`

---

## Phase 1 — Your first endpoint (in-memory CRUD)

- [ ] Understood Swagger/OpenAPI and why FastAPI generates it automatically
- [ ] Sent prompt §1.2 and Copilot generated CRUD endpoints in app/main.py
- [ ] Tested in Swagger: POST, GET, GET/{id}, DELETE work correctly
- [ ] Understood: FastAPI validates path param types automatically (int vs str)
- [ ] Tested sending empty body {} and saw the 422 validation error

**Validation:** CRUD works in Swagger — POST 201, GET 200, DELETE 204, 404 on nonexistent id.

---

## Phase 2 — Schemas with Pydantic

- [ ] Sent prompt §2 and Copilot created IdeaCreate + IdeaResponse with BaseModel
- [ ] Endpoints use response_model to control what gets returned
- [ ] Tested validation: empty title → 422, extra fields → ignored
- [ ] Added custom validator to reject titles with only whitespace
- [ ] Understood: Pydantic validates data at the boundary — rejects invalid input before it reaches the logic

**Validation:** POST with `{"title": "   "}` → 422. POST with extra fields → 201 (ignored).

---

## Phase 3 — Modular structure with APIRouter

- [ ] Sent prompt §3 and Copilot refactored to app/api/v1/endpoints/ideas.py
- [ ] main.py now only has FastAPI() + include_router
- [ ] Schemas are in app/schemas/idea.py
- [ ] Swagger shows endpoints at /api/v1/ideas/ with tag "ideas"
- [ ] Compared with solutions/app/api/v1/ — differences noted

**Validation:** Swagger works at `/docs` with endpoints at `/api/v1/ideas/`.

---

## Phase 4 — Database with SQLAlchemy

- [ ] Created app/core/config.py with Settings and pydantic-settings
- [ ] Created app/core/database.py with async engine + get_db
- [ ] Created app/models/idea.py with SQLAlchemy model
- [ ] Updated main.py with lifespan (create_all)
- [ ] Updated endpoints to use Depends(get_db) + async queries
- [ ] Added PUT /ideas/{id} with IdeaUpdate (optional fields)
- [ ] Verified: data persists between uvicorn restarts

**Validation:** POST idea → restart uvicorn → GET ideas → the idea is still there.

---

## Phase 5 — JWT Authentication

- [ ] Created app/core/security.py with hash, verify, JWT encode/decode
- [ ] Created app/models/user.py with relationship to ideas
- [ ] Created app/schemas/user.py with UserCreate, Token
- [ ] Created app/api/v1/endpoints/auth.py with register + login
- [ ] Created app/dependencies.py with get_current_user (OAuth2PasswordBearer)
- [ ] Updated ideas.py: all endpoints require auth
- [ ] Swagger: can Authorize with token and operate
- [ ] Tested isolation: user1 cannot see user2's ideas

**Validation:** Without token → 401. With token → CRUD works. Two users isolated.

---

## Phase 6 — Middleware, CORS, and errors

- [ ] Added logging middleware (method, path, status, duration)
- [ ] Configured CORS for localhost:3000
- [ ] Created ResourceNotFoundError with custom exception_handler
- [ ] Understood: CORS is needed when FE and API are on different ports
- [ ] Verified logs in uvicorn terminal

**Validation:** Each request appears in logs. CORS headers present in OPTIONS.

---

## Phase 7 — Testing with pytest

- [ ] Created tests/conftest.py with fixtures: engine, session, client, test_user, auth_headers
- [ ] Created tests/test_auth.py — 7 registration and login tests
- [ ] Created tests/test_ideas.py — 11 CRUD + auth tests
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Compared with solutions/tests/ — differences noted
- [ ] Understood: dependency_overrides replaces get_db in tests without touching the real DB

**Validation:** `pytest tests/ -v` → 18+ tests, 0 failures.
