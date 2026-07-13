README - Chatbot Backend

Overview
- Purpose: HTTP backend for a chatbot, built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, and a clean service/repository architecture.
- Status: Foundation, DB, repository pattern, Unit of Work, and DB tests implemented.

How I built this (phases with concrete details & file refs)

Phase 1 — Project Foundation ✅
Goal: Get FastAPI running and scaffold a maintainable app.
- Project layout: top-level files and `app/`, `alembic/`, `test/`.
- Entrypoint: `app/main.py` creates the FastAPI app, calls `app/core/logging.setup_logging()`, uses `lifespan` from `app/core/lifespan.py`, registers exception handlers from `app/core/exceptions.py`, mounts middleware `app/middleware/logging.py`, and includes `api_router` from `app/router.py`. Root endpoint returns `ApiResponse` using `app/schemas/response.py`.
- Routers: feature routers live under `modules/` (e.g., `modules/health/router.py`, `modules/system/router.py`) and are aggregated by `app/router.py`.
- Dev server: run via Uvicorn: `uvicorn app.main:app --reload`.
Files: `app/main.py`, `app/router.py`, `modules/*/router.py`, `requirements.txt`.

Phase 2 — Configuration Management ✅
Goal: Centralized, environment-based settings.
- Pydantic Settings in `app/core/config.py`. `Settings` composes `AppSettings`, `AISettings`, `DatabaseSettings`.
- `.env` support and nested variables use `env_file=".env"` and `env_nested_delimiter="__"`.
- `DatabaseSettings.database_url` builds the SQLAlchemy URL used by `app/database/session.py`.
- Usage: import `settings` from `app.core.config` wherever needed.
Files: `app/core/config.py`, `.env` (local).

Phase 3 — Logging ✅
Goal: Production-oriented logging and request tracing.
- `app/core/logging.py` calls `logging.basicConfig()` and is invoked at startup.
- Request logging middleware in `app/middleware/logging.py` logs method, path, status, and processing time.
- Lifecycle logs via `app/core/lifespan.py`.
Files: `app/core/logging.py`, `app/middleware/logging.py`, `app/core/lifespan.py`.

Phase 4 — Application Lifecycle ✅
Goal: Manage startup/shutdown and readiness checks.
- `app/core/lifespan.py` provides an `asynccontextmanager` lifecycle hook for startup/teardown tasks and is passed to `FastAPI(..., lifespan=lifespan)`. Add DB/Redis/Vector DB checks here for readiness.
Files: `app/core/lifespan.py`.

Phase 5 — Exception Handling ✅
Goal: Consistent API error shapes and handling.
- Centralized exception registration in `app/core/exceptions.py`. Handlers return `ApiResponse`-shaped responses (`app/schemas/response.py`) for consistent clients.
Files: `app/core/exceptions.py`, `app/schemas/response.py`.

Phase 6 — API Structure ✅
Goal: Clean, versioned routing and modular endpoints.
- Version prefix is driven by `settings.app.API_V1_PREFIX` (in `app/core/config.py`).
- Each feature in `modules/` exposes an APIRouter; `app/router.py` composes them into `api_router`, included by `app/main.py`.
Files: `app/router.py`, `modules/*/router.py`.

Phase 7 — Dependency Injection ✅
Goal: Scalable wiring for services and DB sessions.
- SQLAlchemy sessions instantiated in `app/database/session.py` via `engine = create_engine(settings.database.database_url, ...)` and `SessionLocal = sessionmaker(...)`.
- Provide DB session dependency and other shared providers via `app/core/dependecies.py` (use `Depends` in routers/services).
Files: `app/database/session.py`, `app/core/dependecies.py`.

Phase 8 — Database Foundation ✅
Goal: Models, mixins, and session management ready for production.
- Declarative base: `app/database/base.py` defines `Base` (SQLAlchemy 2.0 `DeclarativeBase`).
- Mixins: `app/database/mixins.py` provides `UUIDMixin` (Postgres UUID primary key) and `TimestampMixin` (`created_at`, `updated_at`) using `func.now()`.
- Engine/session: `app/database/session.py` builds the engine and `SessionLocal` (with `echo` toggled by `settings.app.DEBUG`).
- Models should live under `app/database/models/` and inherit from `Base` and mixins for consistent behavior.
Files: `app/database/base.py`, `app/database/mixins.py`, `app/database/session.py`, `app/database/models/*`.

Phase 9 — Persistence & Migrations (brief)
- PostgreSQL used via SQLAlchemy (URL in `app/core/config.py`).
- Repository pattern implemented in `app/common/repository/base.py` to encapsulate CRUD.
- Alembic configured in `alembic/` for migrations.
- Unit of Work implemented under `uow/` to manage transactional workflows and expose repositories.
- Database testing implemented under `test/` using fixtures in `test/conftest.py` and test(s) in `test/database/test_database.py`.

Unit of Work & Database Testing (what to expect in this repo)
- `uow/sqlalchemy.py` (or `uow/base.py`) should accept `SessionLocal`/engine, open a session per unit-of-work, instantiate repositories with that session, provide `commit()` and `rollback()` semantics, and ensure session cleanup.
- Tests: `test/conftest.py` provides a test DB session fixture and overrides app dependencies so tests use the test session; `test/database/test_database.py` contains asserts verifying models, repository methods, or UoW behavior.

Adding new modules / features — step-by-step
1. Create module skeleton under `modules/` (choose a name):
	- `modules/<feature>/router.py` — define an `APIRouter` with endpoints.
	- `modules/<feature>/schemas.py` — Pydantic request/response models.
	- `modules/<feature>/service.py` — business logic; call repositories or UoW here.
	- If persistence required: add a model in `app/database/models/<feature>.py`.

2. Create persistence pieces (if DB-backed):
	- Model: extend `Base` and mixins from `app/database/base.py` and `app/database/mixins.py`.
	- Repository: add `common/repository/<feature>.py` with a class extending `BaseRepository` or using the conventions in `app/common/repository/base.py`.
	- Unit of Work: if a multi-repo transaction is needed, add hooks into `uow/` to expose the new repository.

3. Wire DI and route registration:
	- Provide dependencies in `app/core/dependecies.py` (e.g., `get_db()` yields a session or a UoW factory).
	- In `modules/<feature>/router.py`, use `Depends` to inject `service` constructors or DB dependencies.
	- Register router: import and include it in `app/router.py` or `app/main.py`.

4. Add migrations:
```bash
alembic revision --autogenerate -m "Add <feature> model"
alembic upgrade head
```

5. Add tests:
	- Unit tests for service logic under `test/`.
	- Integration tests exercising HTTP routes or repository/UoW using the DB fixtures in `test/conftest.py`.

6. Docs & API surface:
	- Update README/docs to mention new endpoints and schema examples.
	- OpenAPI docs are auto-generated by FastAPI at `/docs` and `/openapi.json`.

Quick developer commands
- Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- Run dev server:
```bash
uvicorn app.main:app --reload
```
- Create & apply migrations:
```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```
- Run tests:
```bash
pytest -q
```

Files to review when extending or debugging
- `app/main.py` — app wiring and root endpoint
- `app/core/config.py` — settings and env handling
- `app/database/session.py` — engine/session setup
- `app/database/mixins.py` — UUID & timestamp mixins
- `app/common/repository/base.py` — repository conventions
- `uow/` — unit of work implementation (transaction coordination)
- `test/conftest.py` & `test/database/test_database.py` — test fixtures and DB tests

