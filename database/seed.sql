-- ============================================================
-- Complaint Management System
-- Seed Data
-- ============================================================

-- The initial sample data is stored in:
-- complaint_management_dataset.csv
--
-- CSV columns:
-- complaint_id
-- complaint_text
-- category
-- priority
-- complexity
-- recommended_team
--
-- Import the CSV into the complaints table using pgAdmin's
-- Import/Export Data -> Import feature.
--
-- The database is not limited to the initial 500 records.
-- New records can be added using the same six-column format.

SELECT COUNT(*) AS total_complaints
FROM complaints;