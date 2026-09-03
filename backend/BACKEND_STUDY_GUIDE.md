# Backend Study Guide — Complaint Management System

---

## 📌 Executive Overview

### 1. Objective
Build an automated, intelligent, role-based backend system for managing customer complaints and support tickets with AI classification, automatic agent routing, SLA escalation tracking, and real-time administrator analytics.

### 2. Problem Statement
Traditional customer support systems suffer from manual complaint classification delays, inefficient agent assignment, unmonitored resolution bottlenecks (SLA breaches), and poor visibility into system analytics.

### 3. What Your Backend Does
Your FastAPI backend acts as the central engine of the system:
- **Authenticates Users & Roles**: Secure JWT authentication and role-based access (`user`, `agent`, `admin`).
- **Lodge Complaints & Create Tickets**: Receives complaints, auto-generates human-readable IDs (`CMP-XXXXX`), validates categories against the database, and auto-spawns linked support tickets.
- **AI Classification & Chat Relay**: Integrates with an AI module to classify incoming text and relay chatbot conversations, auto-logging complaints when needed.
- **Intelligent Agent Routing**: Automatically assigns support tickets to the best-matching available support agent using a weighted scoring formula based on agent skills, current workload, and availability.
- **SLA Breach Escalation Engine**: Monitors unresolved tickets against priority-based time thresholds (Urgent, High, Medium, Low) and auto-escalates overdue tickets.
- **State Machine & Audit Logging**: Enforces valid ticket status transitions (`Registered → In Progress → Under Review → Resolved`) and maintains an immutable audit trail in `ticket_history`.
- **Real-Time Admin Analytics**: Aggregates system metrics (totals, category breakdown, status breakdown, average resolution time) for administrators.
- **Notifications**: Automatically notifies users on ticket status changes and SLA escalations.

---

## 📁 File-by-File Breakdown (`backend/`)

### Configuration & Main Entry Points
- `backend/app/main.py`: FastAPI application entrypoint initializing CORS, lifespan startup, routes, and global error handlers.
- `backend/app/exceptions.py`: Custom application exceptions and global JSON error response envelope handlers.
- `backend/app/core/config.py`: Environment configuration loader using `pydantic-settings` to manage DB URLs, JWT secrets, and SLA thresholds.
- `backend/app/core/logging.py`: Configures structured application logging across stdout and log files.
- `backend/app/core/security.py`: Security utilities handling `bcrypt` password hashing, JWT encoding/decoding, and FastAPI authentication dependencies.
- `backend/requirements.txt`: Python package dependency specification file.
- `backend/.env.example`: Template file defining required environment variables.
- `backend/README.md`: Comprehensive guide explaining setup, architecture, database migrations, testing, and API documentation.

### Database Layer & ORM Models
- `backend/app/db/session.py`: Database connection engine factory establishing async sessions (`AsyncSessionLocal`) with PostgreSQL / SQLite.
- `backend/app/db/base.py`: Declares SQLAlchemy `Base` class and auto-registers all 9 ORM models into metadata.
- `backend/app/models/__init__.py`: Package init file importing and exporting all 9 ORM model classes.
- `backend/app/models/user.py`: ORM model for user accounts storing credentials, roles (`user`, `agent`, `admin`), and timestamps.
- `backend/app/models/category.py`: ORM model for dynamic editable complaint classification categories.
- `backend/app/models/team.py`: ORM model representing specialized support teams (e.g., Technical, Billing, Delivery).
- `backend/app/models/agent.py`: ORM model storing agent profiles, team associations, skill sets, current workload, and availability.
- `backend/app/models/complaint.py`: ORM model storing customer complaint descriptions, priority, status, and linked tickets.
- `backend/app/models/ticket.py`: ORM model managing support ticket lifecycle, assigned agent/team, SLA timers, and escalation status.
- `backend/app/models/ticket_history.py`: ORM model recording audit trail entries for ticket status transitions and assignment changes.
- `backend/app/models/notification.py`: ORM model storing user notification alerts triggered by status updates or SLA breaches.
- `backend/app/models/faq.py`: ORM model storing frequently asked questions linked to complaint categories.

### Database Migrations (Alembic)
- `backend/alembic.ini`: Configuration file for Alembic database migration environment and logging.
- `backend/alembic/env.py`: Migration environment runner script connecting Alembic to SQLAlchemy `Base.metadata`.
- `backend/alembic/script.py.mako`: Template file used by Alembic for generating new Python database migration scripts.
- `backend/alembic/versions/001_initial_schema_and_seed_data.py`: Initial migration creating all 9 DB tables and seeding support teams and categories.

### API Routes (`app/api/v1/`)
- `backend/app/api/v1/router.py`: Aggregates and mounts all v1 endpoint routers (`auth`, `complaints`, `tickets`, `chat`, `admin`, `notifications`, `health`).
- `backend/app/api/v1/routes/health.py`: Endpoint providing system health status, project metadata, and uptime checks (`GET /health`).
- `backend/app/api/v1/routes/auth.py`: User authentication endpoints handling registration, login, JWT token refreshes, and user profile views.
- `backend/app/api/v1/routes/complaints.py`: Endpoints for lodging complaints (`POST /complaints`), pagination, and detail lookups.
- `backend/app/api/v1/routes/tickets.py`: Endpoints for managing ticket state transitions, status updates, and history audit tracking.
- `backend/app/api/v1/routes/chat.py`: AI chatbot relay endpoint (`POST /chat`) auto-creating complaints and tickets from conversation.
- `backend/app/api/v1/routes/admin.py`: Role-protected admin endpoints for system analytics, user management, agent workloads, and manual assignments.
- `backend/app/api/v1/routes/notifications.py`: Endpoints for viewing user notifications and marking notifications as read (`GET /notifications`, `PUT /notifications/{id}/read`).

### Pydantic Schemas (`app/schemas/`)
- `backend/app/schemas/user.py`: Pydantic request and response schemas for user registration, authentication, tokens, and profile data.
- `backend/app/schemas/complaint.py`: Pydantic schemas for complaint creation, update, and paginated responses.
- `backend/app/schemas/ticket.py`: Pydantic schemas for ticket creation, status updates, history logs, and paginated responses.
- `backend/app/schemas/chat.py`: Pydantic request and response schemas for the AI chatbot relay endpoint.
- `backend/app/schemas/admin.py`: Pydantic schemas for admin analytics metrics, agent workload responses, and manual ticket assignment requests.
- `backend/app/schemas/notification.py`: Pydantic schemas for user notification payloads and paginated notification lists.

### Business Logic Services (`app/services/`)
- `backend/app/services/auth_service.py`: Business logic service managing user creation, password verification, and JWT token issuance.
- `backend/app/services/ai_client.py`: Async HTTP client connecting backend to external AI service for text classification and chatbot responses with 3s timeout.
- `backend/app/services/complaint_service.py`: Business logic for generating human-readable complaint IDs (`CMP-XXXXX`), DB category validation, and auto-creating linked tickets.
- `backend/app/services/ticket_service.py`: Business logic enforcing ticket status state machine rules (`Registered → In Progress → Under Review → Resolved`) and audit history logging.
- `backend/app/services/assignment_service.py`: Intelligent agent auto-assignment engine calculating agent scores based on skills, workload, and availability.
- `backend/app/services/escalation_service.py`: Background SLA breach detection engine escalating unresolved tickets exceeding priority time thresholds.
- `backend/app/services/admin_service.py`: Business logic computing real-time system metrics, category/priority counts, agent workload views, and manual assignments.
- `backend/app/services/notification_service.py`: Business logic service creating user notifications and updating read statuses.
