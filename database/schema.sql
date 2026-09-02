-- ============================================================
-- Complaint Management System
-- PostgreSQL Database Schema
-- ============================================================

-- ============================================================
-- 1. USERS
-- ============================================================

CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT users_role_check
        CHECK (role IN ('user', 'admin'))
);


-- ============================================================
-- 2. TEAMS
-- ============================================================

CREATE TABLE teams (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 3. AGENTS
-- ============================================================

CREATE TABLE agents (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    team_id BIGINT,
    skills TEXT,
    availability VARCHAR(20) NOT NULL DEFAULT 'Available',
    current_workload INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT agents_availability_check
        CHECK (availability IN ('Available', 'Busy', 'Unavailable')),

    CONSTRAINT agents_workload_check
        CHECK (current_workload >= 0),

    CONSTRAINT agents_team_fk
        FOREIGN KEY (team_id)
        REFERENCES teams(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


-- ============================================================
-- 4. COMPLAINTS
-- ============================================================
-- The following six fields follow the team's sample dataset:
--
-- complaint_id
-- complaint_text
-- category
-- priority
-- complexity
-- recommended_team
--
-- Additional fields are included to support the complete
-- application without changing the sample data format.
-- ============================================================

CREATE TABLE complaints (
    complaint_id VARCHAR(20) PRIMARY KEY,
    complaint_text TEXT NOT NULL,

    category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    complexity VARCHAR(20) NOT NULL,
    recommended_team VARCHAR(100) NOT NULL,

    user_id BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT complaints_category_check
        CHECK (
            category IN (
                'Billing',
                'Technical',
                'Service',
                'Account',
                'Delivery',
                'Other'
            )
        ),

    CONSTRAINT complaints_priority_check
        CHECK (
            priority IN (
                'Urgent',
                'High',
                'Medium',
                'Low'
            )
        ),

    CONSTRAINT complaints_complexity_check
        CHECK (
            complexity IN (
                'Low',
                'Medium',
                'High'
            )
        ),

    CONSTRAINT complaints_team_check
        CHECK (
            recommended_team IN (
                'General Support',
                'Technical Support',
                'Delivery Support',
                'Billing Support',
                'Service Support',
                'Account Support'
            )
        ),

    CONSTRAINT complaints_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


-- ============================================================
-- 5. TICKETS
-- ============================================================

CREATE TABLE tickets (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    ticket_number VARCHAR(30) NOT NULL UNIQUE,
    complaint_id VARCHAR(20) NOT NULL UNIQUE,

    category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Registered',

    assigned_team_id BIGINT,
    assigned_agent_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,

    resolution_information TEXT,

    CONSTRAINT tickets_complaint_fk
        FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT tickets_category_check
        CHECK (
            category IN (
                'Billing',
                'Technical',
                'Service',
                'Account',
                'Delivery',
                'Other'
            )
        ),

    CONSTRAINT tickets_priority_check
        CHECK (
            priority IN (
                'Urgent',
                'High',
                'Medium',
                'Low'
            )
        ),

    CONSTRAINT tickets_status_check
        CHECK (
            status IN (
                'Registered',
                'In Progress',
                'Under Review',
                'Resolved'
            )
        ),

    CONSTRAINT tickets_team_fk
        FOREIGN KEY (assigned_team_id)
        REFERENCES teams(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT tickets_agent_fk
        FOREIGN KEY (assigned_agent_id)
        REFERENCES agents(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


-- ============================================================
-- 6. TICKET HISTORY
-- ============================================================

CREATE TABLE ticket_history (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    ticket_id BIGINT NOT NULL,
    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    changed_by BIGINT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ticket_history_ticket_fk
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT ticket_history_user_fk
        FOREIGN KEY (changed_by)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT ticket_history_new_status_check
        CHECK (
            new_status IN (
                'Registered',
                'In Progress',
                'Under Review',
                'Resolved'
            )
        )
);


-- ============================================================
-- 7. NOTIFICATIONS
-- ============================================================

CREATE TABLE notifications (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    user_id BIGINT NOT NULL,
    ticket_id BIGINT,
    message TEXT NOT NULL,
    type VARCHAR(30) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT notifications_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT notifications_ticket_fk
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 8. FAQs / KNOWLEDGE BASE
-- ============================================================

CREATE TABLE faqs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    keywords TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT faqs_category_check
        CHECK (
            category IN (
                'Billing',
                'Technical',
                'Service',
                'Account',
                'Delivery',
                'Other'
            )
        )
);


-- ============================================================
-- 9. AI PREDICTIONS
-- ============================================================

CREATE TABLE ai_predictions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    ticket_id BIGINT NOT NULL,

    predicted_category VARCHAR(50),
    predicted_priority VARCHAR(20),
    confidence_score NUMERIC(5,4),
    model_version VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ai_predictions_ticket_fk
        FOREIGN KEY (ticket_id)
        REFERENCES tickets(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT ai_predictions_category_check
        CHECK (
            predicted_category IS NULL OR
            predicted_category IN (
                'Billing',
                'Technical',
                'Service',
                'Account',
                'Delivery',
                'Other'
            )
        ),

    CONSTRAINT ai_predictions_priority_check
        CHECK (
            predicted_priority IS NULL OR
            predicted_priority IN (
                'Urgent',
                'High',
                'Medium',
                'Low'
            )
        ),

    CONSTRAINT ai_predictions_confidence_check
        CHECK (
            confidence_score IS NULL OR
            confidence_score BETWEEN 0 AND 1
        )
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_complaints_category
    ON complaints(category);

CREATE INDEX idx_complaints_priority
    ON complaints(priority);

CREATE INDEX idx_complaints_complexity
    ON complaints(complexity);

CREATE INDEX idx_complaints_recommended_team
    ON complaints(recommended_team);

CREATE INDEX idx_complaints_user_id
    ON complaints(user_id);

CREATE INDEX idx_tickets_status
    ON tickets(status);

CREATE INDEX idx_tickets_priority
    ON tickets(priority);

CREATE INDEX idx_tickets_category
    ON tickets(category);

CREATE INDEX idx_tickets_assigned_team
    ON tickets(assigned_team_id);

CREATE INDEX idx_tickets_assigned_agent
    ON tickets(assigned_agent_id);

CREATE INDEX idx_ticket_history_ticket_id
    ON ticket_history(ticket_id);

CREATE INDEX idx_notifications_user_id
    ON notifications(user_id);

CREATE INDEX idx_notifications_ticket_id
    ON notifications(ticket_id);

CREATE INDEX idx_ai_predictions_ticket_id
    ON ai_predictions(ticket_id);