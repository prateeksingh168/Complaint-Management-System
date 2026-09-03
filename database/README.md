# Complaint Management System — Database

This folder contains the PostgreSQL database resources for the
Complaint Management System.

## Files

### `schema.sql`

Creates the PostgreSQL database structure, including:

- Users
- Teams
- Agents
- Complaints
- Tickets
- Ticket History
- Notifications
- FAQs / Knowledge Base
- AI Predictions

### `complaint_management_dataset.csv`

Contains the team's initial sample complaint dataset.

The dataset uses these six fields:

- `complaint_id`
- `complaint_text`
- `category`
- `priority`
- `complexity`
- `recommended_team`

The initial dataset contains 500 complaint records.

The database is not limited to these 500 records. Additional
complaints can be stored using the same six-field complaint format.

### `seed.sql`

Contains seed-data instructions and a verification query for the
initial dataset.

## Database Setup

### 1. Create the database

Create a PostgreSQL database named:

`complaint_management_db`

### 2. Run the schema

Open `schema.sql` in pgAdmin Query Tool and execute it.

This creates all required tables, relationships, constraints,
and indexes.

### 3. Import the sample dataset

In pgAdmin:

1. Open `complaint_management_db`.
2. Go to `Schemas → public → Tables`.
3. Right-click the `complaints` table.
4. Select `Import/Export Data`.
5. Select `Import`.
6. Choose `complaint_management_dataset.csv`.
7. Select CSV format.
8. Enable the header option.
9. Import the six dataset columns:

   - `complaint_id`
   - `complaint_text`
   - `category`
   - `priority`
   - `complexity`
   - `recommended_team`

## Verify the Data

Run:

```sql
SELECT COUNT(*) AS total_complaints
FROM complaints;