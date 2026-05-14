# FastAPI Workshop — AI-First API Development

Hands-on workshop to learn **FastAPI** from scratch using AI as your copilot. You'll build a complete **Ideas API** with authentication, database, and tests.

## What you'll learn

- REST endpoints with automatic validation (Pydantic)
- Modular structure with APIRouter
- SQLAlchemy 2.0 async with SQLite
- JWT authentication (register, login, protected endpoints)
- Middleware, CORS, and error handling
- Testing with pytest + httpx (AsyncClient)

## Prerequisites

- Python 3.12+
- VS Code with GitHub Copilot
- Basic knowledge of Python and terminal

## Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Copy environment variables
cp .env.example .env

# 4. Verify
uvicorn app.main:app --reload
# → http://localhost:8000/docs (Swagger)
```

## Structure

| Folder | Purpose |
|---|---|
| `app/` | Your work — you build the API phase by phase |
| `tests/` | Your work — tests with pytest |
| `solutions/` | Complete reference (do not modify) |

## How to use

1. Open [INSTRUCTIONS.md](INSTRUCTIONS.md) — it has ready-to-use prompts for Copilot Chat
2. Follow the phases in order (1→7)
3. Each phase has validation with Swagger and/or pytest
4. If you get stuck, check `solutions/`

## Quick commands

```bash
source .venv/bin/activate              # Activate environment
uvicorn app.main:app --reload          # Start API
pytest tests/ -v                       # Run tests
sqlite3 ideas.db ".tables"             # Inspect DB
```

## Theory reference

See [FASTAPI.md](FASTAPI.md) for in-depth concepts.
