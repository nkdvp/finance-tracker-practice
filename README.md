# Finance Tracker Practice

This is a small RESTful API that I'm building to practice modern Python and FastAPI.
The application lets users manage their own income/expense categories and financial
transactions.

I'm using the project to learn asynchronous SQLAlchemy, Alembic, Pydantic, and a
layered architecture:

```text
Router → Service → Repository → Database
```

## What Works Now

- FastAPI application factory and `/health` endpoint
- Async SQLAlchemy 2.0 with SQLite
- Alembic migration for `User`, `Category`, and `Transaction`
- User create, list, and detail endpoints
- Full CRUD endpoints for categories and transactions
- Pydantic request/response models and email validation
- Dependency Injection for database sessions, repositories, and services
- Centralized custom application errors and exception handlers
- Clean `Router → Service → Repository` architecture
- Request logging middleware with request ID, method, path, parameters, status, and duration
- Swagger/OpenAPI documentation at `/docs`
- Ruff linting and mypy strict type checking

## What I Want to Add Next

- Unit and integration testing with Pytest
- Authentication and authorization
- Centralized settings and reusable utilities
- Summary endpoint and advanced transaction filters
- N+1 query review and eager-loading strategy
- Structured JSON logging

## Getting Started

### Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Install and run

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

Open:

- API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

SQLite is used by default:

```text
sqlite+aiosqlite:///./finance.db
```

You can override it with the `DATABASE_URL` environment variable.

## API Overview

| Resource | Available operations |
| --- | --- |
| Health | Check application health |
| Users | Create, list, get details |
| Categories | Create, list, get, update, delete |
| Transactions | Create, list, get, update, delete |

## Project Structure

```text
app/
├── errors/          # Custom exceptions and HTTP exception handlers
├── middlewares/     # Request logging and future HTTP middleware
├── models/          # SQLAlchemy database models
├── repositories/    # Database access
├── routers/         # HTTP endpoints
├── schemas/         # Pydantic request and response models
└── services/        # Business rules and transaction boundaries
migrations/          # Alembic migrations
main.py              # FastAPI application factory
```

## Authentication Roadmap

For authentication and authorization, I plan to:

- Add secure user registration and login
- Hash passwords before persistence
- Issue and validate JWT access tokens
- Add a user role, including an `admin` role
- Allow admins to view all permitted resources
- Add authentication (`AuthN`) and authorization (`AuthZ`) middleware/dependencies
- Add customized authentication errors, for example:
  - `401 Unauthorized`: authentication is missing or invalid
  - `403 Forbidden`: the authenticated user is not allowed to perform the action
- Optionally support refresh tokens backed by a cache

I will keep secrets in environment-based settings instead of committing them to Git.

## Utilities and Configuration Roadmap

I also want to clean up repeated configuration and helper code:

- Create `app/utils/` for small reusable helpers
- Move duplicated helper logic into focused utility modules
- Add `app/utils/config.py` for settings such as:
  - Database URL
  - JWT secret and algorithm
  - Access-token expiration
  - Other repeated configuration values
- Replace hardcoded runtime configuration with environment-backed settings
- Use Pydantic `BaseSettings` when the settings layer is implemented

`utils` should contain reusable code only; business rules should remain in services.

## What I'm Learning

| Area | Learning target | Status |
| --- | --- | --- |
| Modern Python & Tooling | Syntax, type hints, f-strings, comprehensions, uv, Ruff, and mypy | In progress |
| Asynchronous Programming | `async`/`await`, event loop, and sync `requests` vs async `httpx` | In progress |
| Data Validation | Pydantic schemas, `BaseSettings`, and field validators | In progress |
| FastAPI Core | RESTful routes, request/response models, and `Depends` | Applied |
| Database & Persistence | Async SQLAlchemy 2.0, Alembic, and preventing N+1 queries | In progress |
| Enterprise Architecture | `Router → Service → Repository` | Applied |
| Security & JWT | Registration, password hashing, JWT, AuthN, and AuthZ | Planned |
| Testing & Quality | Pytest, integration tests, and high test coverage | Planned |

## Practical Project

My goal is to build a RESTful financial management system where users can track income
and expenses across their own categories. I want to apply each learning area above to
one practical FastAPI project.

## Milestones

### End of Week 1: Theory & Environment

- Done: environment initialized with uv
- Done: Ruff and mypy strict checks configured and passing
- In progress: compare async `httpx` with sync `requests` in a learning script
- Done: FastAPI routing, Pydantic schemas, and Dependency Injection applied
- Done: initial ERD represented by SQLAlchemy models and Alembic migration

### End of Week 2: Core Features

- Done: FastAPI app factory and database scaffold
- Done: Alembic migration for users, categories, and transactions
- Done: category and transaction CRUD with response models
- Done: all current endpoints visible and typed in Swagger
- Planned: registration, login, password hashing, and JWT issuance
- Planned: initial unit tests with Pytest
- Planned: minimum 60% test coverage

### End of Week 3: Hardening & Professional Polish

- Planned: `GET /summary` with aggregations and advanced transaction filters
- Done: clean `Router → Service → Repository` architecture
- Planned: verify and remove N+1 queries with eager loading where required
- Planned: add background tasks and structured JSON logging
- Planned: increase coverage and add integration tests with an isolated test database

## Reporting & Evaluation

- **Daily report:** What I did | What I learned | Blockers
- **Final report:** Technical challenges, solutions, and self-assessment
- **Evidence of work:** GitHub repository with clear commits and an up-to-date README

Once these milestones are complete, I will write a final self-evaluation and prepare
the project for a demo.

## Quality Checks

```bash
uv run ruff check .
uv run mypy .
```

Testing commands and coverage configuration will be added with the testing milestone.
