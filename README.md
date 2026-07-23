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
- Async SQLAlchemy sessions via `AsyncSessionLocal` in `app/database/session.py`.
- `app/core/dependencies.py` is the single place that wires everything together:
  - `get_uow()` — an `asynccontextmanager` that opens an `AsyncSessionLocal`, wraps it in `SQLAlchemyUnitOfWork`, and yields the UoW. Services take a `uow_factory` (i.e. `get_uow`) in their constructor rather than a raw session.
  - `get_vector_store()`, `get_embedding_provider()`, `get_llm_provider()` — build the configured AI provider (see Phase 10) based on `settings.ai`/`settings.database.VECTOR_DB`.
  - `get_storage_provider()`, `get_health_service()` — other shared singletons.
- Routers construct a module `service = XyzService(...)` at import time using these factories (see `modules/chat/router.py`, `modules/conversation/router.py`) rather than using FastAPI `Depends` everywhere.
Files: `app/database/session.py`, `app/core/dependencies.py`.

Phase 8 — Database Foundation ✅
Goal: Models, mixins, and session management ready for production.
- Declarative base: `app/database/base.py` defines `Base` (SQLAlchemy 2.0 `DeclarativeBase`).
- Mixins: `app/database/mixins.py` provides `UUIDMixin` (Postgres UUID primary key) and `TimestampMixin` (`created_at`, `updated_at`) using `func.now()`.
- Engine/session: `app/database/session.py` builds the engine and `SessionLocal` (with `echo` toggled by `settings.app.DEBUG`).
- Models should live under `app/database/models/` and inherit from `Base` and mixins for consistent behavior.
Files: `app/database/base.py`, `app/database/mixins.py`, `app/database/session.py`, `app/database/models/*`.

Phase 9 — Persistence & Migrations (brief)
- PostgreSQL used via async SQLAlchemy (URL in `app/core/config.py`, engine/session in `app/database/session.py`).
- Models inherit from `app/database/models/base_model.py::BaseModel`, which combines `Base` (`app/database/base.py`) with `UUIDMixin` and `TimestampMixin` (`app/database/mixins.py`) — every table automatically gets `id` (UUID PK), `is_deleted`, `deleted_by`, `created_at`, `updated_at`, `deleted_at` for free (soft-delete friendly).
- Repository pattern implemented in `app/common/repository/base.py` (`BaseRepository[ModelType]`) providing `list`, `get`, `create`, `create_many`, `update`, `delete`. Feature repositories (e.g. `modules/conversation/repository.py`, `modules/message/repository.py`) extend it and add query methods (e.g. `get_by_conversation`).
- Alembic configured in `alembic/` for migrations. `alembic/env.py` imports every module's `models.py` (e.g. `app.modules.conversation.models`, `app.modules.message.models`) so autogenerate can see new tables — **new model modules must be imported there**.
- Unit of Work implemented under `uow/` (`uow/base.py::UnitOfWork` ABC, `uow/sqlalchemy.py::SQLAlchemyUnitOfWork`) to manage transactional workflows: it owns the `AsyncSession`, instantiates every repository bound to that same session (`uow.conversations`, `uow.messages`, `uow.documents`, `uow.document_chunks`, `uow.retrieval_chunks`), and commits on clean `__aexit__` / rolls back on exception.
- Database testing implemented under `test/` using fixtures in `test/conftest.py` and test(s) in `test/database/test_database.py`.

Unit of Work & Database Testing (what to expect in this repo)
- `SQLAlchemyUnitOfWork.__aenter__` returns itself; `__aexit__` commits if no exception occurred (otherwise rolls back), then closes the session — so a plain `async with self.uow_factory() as uow: ...` auto-commits at the end of the block.
- Services never construct a `SQLAlchemyUnitOfWork` directly — they receive a `uow_factory: Callable[[], UnitOfWork]` (in practice `get_uow` from `app/core/dependencies.py`) in their `__init__` and call `async with self.uow_factory() as uow:` per operation.
- **Sharing one transaction across multiple service calls**: some services (see `modules/conversation/service.py`, `modules/message/service.py`) accept an *optional* `uow` argument on each method plus a private `_with_uow(uow, func)` helper — if a caller already has an open `uow` (e.g. `modules/chat/service.py` opening one `async with get_uow() as uow:` block to resolve a conversation, fetch history, and save the user's message atomically), it's reused instead of opening a new session; otherwise the method opens/manages its own. This keeps unrelated single calls simple while allowing related writes to be atomic when needed.
- Tests: `test/conftest.py` provides a test DB session fixture and overrides app dependencies so tests use the test session; `test/database/test_database.py` contains asserts verifying models, repository methods, or UoW behavior.

Phase 10 — AI / RAG Layer ✅
Goal: Pluggable providers for embeddings, LLMs, and vector stores, composed into a retrieval-augmented chat flow.
- Providers live under `modules/ai/providers/` and each follow the same shape: an abstract `base.py` (e.g. `LLMProvider`, `EmbeddingProvider`, `VectorStoreProvider`), one implementation per backend (`llm/anthropic.py`; `embeddings/ollama.py`; `vectorstore/pgvector.py`, `qdrant.py`, `pinecone.py`), a `dto.py` for request/response DTOs, and a `factory.py` (`LLMFactory`, `EmbeddingFactory`, `VectorStoreFactory`) that picks the implementation based on settings (`settings.ai.LLM_PROVIDER`, `settings.ai.EMBEDDING_PROVIDER`, `settings.database.VECTOR_DB`). `app/core/dependencies.py` exposes `get_llm_provider()`, `get_embedding_provider()`, `get_vector_store()` built from these factories.
- `modules/ai/ingestion/` (`loader.py`, `splitter.py`, `service.py`, `dto.py`) turns uploaded documents into chunks for embedding.
- `modules/ai/retrieval/` (`repository.py`, `service.py`, `dto.py`) runs similarity search over the vector store to fetch top-k relevant chunks for a query.
- `modules/ai/prompt/` (`template.py`, `service.py`, `dto.py`) builds the final list of `ChatMessage`s (system/context/history/question) sent to the LLM.
- `modules/ai/rag/service.py::RAGService` ties it together: `ask()` returns a single `RAGResponse` (retrieved chunks + full `ChatResponse`); `ask_stream()` returns a `RAGStreamResponse` (retrieved chunks + an async generator of `ChatStreamChunk`s) for streaming replies.
- `modules/chat/service.py::ChatService` is the top-level orchestrator used by the `/chat` and `/chat/stream` routes: it resolves/creates a `Conversation`, loads recent `Message` history via `modules/message/service.py::MessageService`, calls `RAGService`, then persists the user + assistant messages.
Files: `modules/ai/providers/*`, `modules/ai/ingestion/*`, `modules/ai/retrieval/*`, `modules/ai/prompt/*`, `modules/ai/rag/*`, `modules/chat/*`, `modules/conversation/*`, `modules/message/*`.

Adding new modules / features — step-by-step
This mirrors how `modules/message/` and `modules/chat/` were added.

1. Create the module skeleton under `modules/<feature>/`:
	- `models.py` — SQLAlchemy model, only if the feature is DB-backed (see step 2).
	- `repository.py` — extends `BaseRepository[Model]` from `app/common/repository/base.py`; add query methods here (e.g. `get_by_conversation`).
	- `schemas.py` — Pydantic request/response models (e.g. `XyzResponseSchema` with `model_config = {"from_attributes": True}`).
	- `service.py` — business logic; takes `uow_factory: Callable[[], UnitOfWork]` in `__init__` and does `async with self.uow_factory() as uow: ...` per operation. If the operation may need to share a transaction with a caller, accept an optional `uow: UnitOfWork | None = None` param (see the `_with_uow` helper pattern in `modules/conversation/service.py` / `modules/message/service.py`).
	- `router.py` — define an `APIRouter`, instantiate `service = XyzService(uow_factory=get_uow)` at module level, and define endpoints that call the service and wrap results in `ApiResponse` (`app/schemas/response.py`).

2. Create persistence pieces (if DB-backed):
	- Model: extend `app/database/models/base_model.py::BaseModel` (gives you `id`, soft-delete fields, and timestamps for free). Use `Mapped`/`mapped_column` (SQLAlchemy 2.0 style) and add `relationship(...)` + `TYPE_CHECKING` imports for cross-module FKs (see `modules/message/models.py` ↔ `modules/conversation/models.py`).
	- Register the model with Alembic: add `import app.modules.<feature>.models` to `alembic/env.py` so autogenerate can see the new table.
	- Unit of Work: add `self.<feature>s = <Feature>Repository(self.session)` in `uow/sqlalchemy.py::SQLAlchemyUnitOfWork.__init__` so it's available as `uow.<feature>s` everywhere.

3. Wire DI and route registration:
	- Reuse the existing factories in `app/core/dependencies.py` (`get_uow`, `get_llm_provider`, `get_embedding_provider`, `get_vector_store`, etc.) — add a new `get_xyz_*()` factory here only if you're introducing a new pluggable provider.
	- Register the router: import it and add `api_router.include_router(xyz_router, prefix=settings.app.API_V1_PREFIX, tags=["Xyz"])` in `app/router.py`.

4. Add migrations:
```bash
alembic revision --autogenerate -m "create_<feature>_table"
alembic upgrade head
```
	- Always review the generated migration file before running it — autogenerate can miss things like FK types (see `alembic/versions/02494cf5a198_add_foreignkey_messages_table.py`, a follow-up migration needed to convert `messages.conversation_id` to a proper UUID FK).

5. Add tests:
	- Unit tests for service/repository logic under `test/` (see `test/repositories/`).
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
- `app/router.py` — top-level router composition (add new feature routers here)
- `app/core/config.py` — settings and env handling
- `app/core/dependencies.py` — UoW factory (`get_uow`) and AI provider factories
- `app/database/session.py` — async engine/session setup
- `app/database/mixins.py`, `app/database/models/base_model.py` — UUID, soft-delete & timestamp mixins shared by every model
- `app/common/repository/base.py` — repository conventions (`BaseRepository`)
- `uow/base.py`, `uow/sqlalchemy.py` — unit of work implementation (transaction coordination, repository registry)
- `modules/chat/service.py` — example of orchestrating multiple services (`ConversationService`, `MessageService`, `RAGService`) with a shared `uow`
- `alembic/env.py` — where new model modules must be imported for autogenerate to detect them
- `test/conftest.py` & `test/database/test_database.py` — test fixtures and DB tests

