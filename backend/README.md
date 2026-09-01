# Backend Module — Complaint Management System

Asynchronous FastAPI backend service powering the AI-powered Complaint Management System.

## Architecture & Features

- **Framework:** FastAPI with Uvicorn server
- **Database ORM:** Async SQLAlchemy 2.0 + `asyncpg` (PostgreSQL) / `aiosqlite` (Testing)
- **Database Migrations:** Alembic
- **Authentication & Security:** JWT Access & Refresh Tokens (`python-jose`) + `bcrypt` password hashing
- **Data Validation:** Pydantic v2 schemas
- **AI Integration:** HTTP client connecting to AI classification & chatbot endpoints with 3s timeout & keyword rule-based fallback
- **Intelligent Assignment:** Weighted scoring algorithm selecting top available agent per team
- **SLA Escalation Engine:** Automated checking of unresolved tickets against priority SLA thresholds
- **Audit Logging & State Machine:** Ticket status transitions (`Registered → In Progress → Under Review → Resolved`) with complete history logs in `ticket_history`
- **Analytics & Admin APIs:** System metrics, category/priority counts, agent workload status, and manual ticket assignment

---

## Directory Structure

```
backend/
├── alembic/                      # Database migration scripts & env config
│   ├── versions/                 # Alembic migration revisions
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── main.py                   # FastAPI app initialization, middleware, routes
│   ├── exceptions.py             # Global exception handlers & error envelope
│   ├── api/
│   │   └── v1/
│   │       ├── router.py         # Main API v1 router aggregator
│   │       └── routes/           # Route handlers (auth, complaints, tickets, chat, admin, notifications, health)
│   ├── core/
│   │   ├── config.py             # Settings loader via pydantic-settings
│   │   ├── security.py           # Bcrypt & JWT security utilities
│   │   └── logging.py            # Structured logging setup
│   ├── db/
│   │   ├── session.py            # Async engine & sessionmaker factory
│   │   └── base.py               # SQLAlchemy DeclarativeBase
│   ├── models/                   # ORM database models (User, Complaint, Ticket, Category, Team, Agent, etc.)
│   ├── schemas/                  # Pydantic request/response schemas
│   └── services/                 # Business logic services (auth, complaint, ticket, assignment, escalation, AI client)
├── alembic.ini                   # Alembic configuration
├── requirements.txt              # Dependencies file
├── .env.example                  # Environment configuration template
└── .env                          # Local environment settings
```

---

## Getting Started

### 1. Prerequisites
- Python 3.11+
- PostgreSQL database (or local connection string)

### 2. Environment Setup
Copy `.env.example` to `.env` and adjust configuration variables as needed:
```bash
cp .env.example .env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
To create all database tables and seed initial lookup categories & support teams:
```bash
alembic upgrade head
```

### 5. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
- API Docs (Swagger UI): `http://localhost:8000/docs`
- ReDoc Docs: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/api/v1/health`

---

## Running Tests

Execute the complete pytest test suite:
```bash
python -m pytest tests/
```

All 28+ unit and integration tests verify health routes, database ORM models, auth, complaint lifecycle, ticket state machine, AI fallback integration, assignment scoring, SLA escalation, and global error handling.
