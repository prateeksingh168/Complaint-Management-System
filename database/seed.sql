-- Complaint Management System
-- Load the team's sample complaint dataset.
--
-- Run this file from the repository root using psql:
-- psql -d complaint_management_db -f database/seed.sql

CREATE TEMP TABLE complaint_seed (
    complaint_id VARCHAR(20),
    complaint_text TEXT,
    category VARCHAR(100),
    priority VARCHAR(20),
    complexity VARCHAR(20),
    recommended_team VARCHAR(100)
);

\copy complaint_seed (
    complaint_id,
    complaint_text,
    category,
    priority,
    complexity,
    recommended_team
) FROM 'database/complaint_management_dataset.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

INSERT INTO complaints (
    complaint_id,
    complaint_text,
    category,
    priority,
    complexity,
    recommended_team
)
SELECT
    complaint_id,
    complaint_text,
    category,
    priority,
    complexity,
    recommended_team
FROM complaint_seed
ON CONFLICT (complaint_id) DO NOTHING;

SELECT COUNT(*) AS total_complaints
FROM complaints;