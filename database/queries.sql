-- ============================================================
-- Complaint Management System
-- Common Database Queries
-- ============================================================


-- ============================================================
-- 1. View all complaints
-- ============================================================

SELECT *
FROM complaints
ORDER BY complaint_id;


-- ============================================================
-- 2. View the most recent complaints
-- ============================================================

SELECT *
FROM complaints
ORDER BY created_at DESC
LIMIT 20;


-- ============================================================
-- 3. Find complaints by category
-- Example: Technical
-- ============================================================

SELECT *
FROM complaints
WHERE category = 'Technical'
ORDER BY complaint_id;


-- ============================================================
-- 4. Find high-priority complaints
-- ============================================================

SELECT *
FROM complaints
WHERE priority IN ('Urgent', 'High')
ORDER BY
    CASE priority
        WHEN 'Urgent' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;


-- ============================================================
-- 5. Find complaints recommended for a particular team
-- ============================================================

SELECT *
FROM complaints
WHERE recommended_team = 'Technical Support'
ORDER BY complaint_id;


-- ============================================================
-- 6. Count complaints by category
-- ============================================================

SELECT
    category,
    COUNT(*) AS total_complaints
FROM complaints
GROUP BY category
ORDER BY total_complaints DESC;


-- ============================================================
-- 7. Count complaints by priority
-- ============================================================

SELECT
    priority,
    COUNT(*) AS total_complaints
FROM complaints
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'Urgent' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
    END;


-- ============================================================
-- 8. Count complaints by complexity
-- ============================================================

SELECT
    complexity,
    COUNT(*) AS total_complaints
FROM complaints
GROUP BY complexity
ORDER BY total_complaints DESC;


-- ============================================================
-- 9. Count complaints by recommended team
-- ============================================================

SELECT
    recommended_team,
    COUNT(*) AS total_complaints
FROM complaints
GROUP BY recommended_team
ORDER BY total_complaints DESC;


-- ============================================================
-- 10. Search complaints by text
-- ============================================================

SELECT *
FROM complaints
WHERE complaint_text ILIKE '%payment%'
ORDER BY complaint_id;


-- ============================================================
-- 11. View complaints by category and priority
-- ============================================================

SELECT
    complaint_id,
    complaint_text,
    category,
    priority,
    complexity,
    recommended_team
FROM complaints
WHERE category = 'Billing'
  AND priority IN ('Urgent', 'High')
ORDER BY complaint_id;


-- ============================================================
-- 12. Total number of complaints
-- ============================================================

SELECT COUNT(*) AS total_complaints
FROM complaints;


-- ============================================================
-- 13. View tickets with their complaint information
-- ============================================================

SELECT
    t.ticket_number,
    t.status,
    t.category,
    t.priority,
    c.complaint_id,
    c.complaint_text,
    c.complexity,
    c.recommended_team
FROM tickets t
JOIN complaints c
    ON t.complaint_id = c.complaint_id
ORDER BY t.created_at DESC;


-- ============================================================
-- 14. View tickets assigned to a particular team
-- ============================================================

SELECT
    t.ticket_number,
    t.category,
    t.priority,
    t.status,
    tm.name AS assigned_team
FROM tickets t
JOIN teams tm
    ON t.assigned_team_id = tm.id
WHERE tm.name = 'Technical Support'
ORDER BY t.created_at DESC;


-- ============================================================
-- 15. View ticket history
-- ============================================================

SELECT
    t.ticket_number,
    th.old_status,
    th.new_status,
    th.changed_at
FROM ticket_history th
JOIN tickets t
    ON th.ticket_id = t.id
ORDER BY th.changed_at DESC;


-- ============================================================
-- 16. View unread notifications for a user
-- ============================================================

SELECT *
FROM notifications
WHERE user_id = 1
  AND is_read = FALSE
ORDER BY created_at DESC;