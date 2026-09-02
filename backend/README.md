# Backend Module — Complaint Management System

Asynchronous FastAPI backend service powering the AI-powered Complaint Management System, fully aligned with the official PostgreSQL database schema.

## Architecture & Features

- **Framework:** FastAPI with Uvicorn server
- **Database ORM:** Async SQLAlchemy 2.0 + `asyncpg` (PostgreSQL) / `aiosqlite` (Testing)
- **Database Migrations:** Alembic
- **Authentication & Security:** JWT Access & Refresh Tokens (`python-jose`) + `bcrypt` password hashing
- **Data Validation:** Pydantic v2 schemas
- **AI Integration:** HTTP client connecting to AI classification & chatbot endpoints with 3s timeout & keyword rule-based fallback
- **Intelligent Assignment:** Weighted scoring algorithm selecting top available agent per team based on skills and workload
- **SLA Escalation Engine:** Automated checking of unresolved tickets against priority SLA thresholds
- **Audit Logging & State Machine:** Ticket status transitions (`Registered → In Progress → Under Review → Resolved`) with history logs in `ticket_history`
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
│   ├── models/                   # ORM models (User, Team, Agent, Complaint, Ticket, TicketHistory, Notification, FAQ, AIPrediction)
│   ├── schemas/                  # Pydantic request/response schemas
│   └── services/                 # Business logic services (auth, complaint, ticket, assignment, escalation, AI client)
├── alembic.ini                   # Alembic configuration
├── requirements.txt              # Dependencies file
├── .env.example                  # Environment configuration template
├── BACKEND_STUDY_GUIDE.md        # Comprehensive backend architecture study guide
└── README.md                     # Backend documentation
```

---

## Database Integration & Alignment

The backend ORM models match Member 3's official PostgreSQL schema (`schema.sql`):

- **`users`**: `id` BIGINT, `name`, `email`, `password_hash`, `role` (`user` / `admin`).
- **`teams`**: `id` BIGINT, `name`, `description`.
- **`agents`**: `id` BIGINT, `name`, `email`, `team_id` FK, `skills` TEXT, `availability`, `current_workload`.
- **`complaints`**: `complaint_id` VARCHAR(20) PRIMARY KEY, `complaint_text`, `category`, `priority`, `complexity`, `recommended_team`, `user_id` FK.
- **`tickets`**: `id` BIGINT, `ticket_number` VARCHAR(30) UNIQUE, `complaint_id` FK, `category`, `priority`, `status`, `assigned_team_id` FK, `assigned_agent_id` FK, `resolution_information`.
- **`ticket_history`**: `id` BIGINT, `ticket_id` FK, `old_status`, `new_status`, `changed_by` FK, `changed_at`.
- **`notifications`**: `id` BIGINT, `user_id` FK, `ticket_id` FK, `message`, `type`, `is_read`.
- **`faqs`**: `id` BIGINT, `question`, `answer`, `category`, `keywords`.
- **`ai_predictions`**: `id` BIGINT, `ticket_id` FK, `predicted_category`, `predicted_priority`, `confidence_score`, `model_version`.

---

## Getting Started

### 1. Prerequisites
- Python 3.11+
- PostgreSQL database (`complaint_management_db`)

### 2. Environment Setup
Copy `.env.example` to `.env` and adjust configuration variables:
```bash
cp .env.example .env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
To create all database tables and seed initial support teams:
```bash
alembic upgrade head
```

### 5. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`
- ReDoc Docs: `http://localhost:8000/redoc`

---

## Running Tests

Execute the complete pytest test suite:
```bash
python -m pytest tests/
```
