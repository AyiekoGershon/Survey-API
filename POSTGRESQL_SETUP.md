# PostgreSQL Database Schema Guide

## Overview

The `database_schema_postgres.sql` file contains a fully PostgreSQL-compatible version of the Sky Survey API database schema.

## Key Differences from MySQL

| Feature | MySQL | PostgreSQL |
|---------|-------|-----------|
| **Auto-increment** | `INT PRIMARY KEY AUTO_INCREMENT` | `SERIAL PRIMARY KEY` |
| **Timestamp updates** | `ON UPDATE CURRENT_TIMESTAMP` | Trigger function |
| **ENUM** | `ENUM(...)` | `CREATE TYPE ... AS ENUM(...)` |
| **JSON** | `JSON` | `JSONB` (binary JSON, better for queries) |
| **Index creation** | `INDEX idx_name (col)` in CREATE TABLE | `CREATE INDEX idx_name ON table(col);` |
| **Named constraints** | `UNIQUE KEY name (col)` | `CONSTRAINT name UNIQUE (col)` |
| **Database switch** | `USE database_name;` | `\c database_name` (in psql) |

## Installation Steps

### 1. Create the Database
```bash
# Using psql directly
createdb sky_survey_db

# Or using psql interactive mode
psql -U postgres
CREATE DATABASE sky_survey_db;
```

### 2. Run the Schema
```bash
# Execute the schema file
psql -U postgres -d sky_survey_db -f database_schema_postgres.sql

# Or from within psql
\c sky_survey_db
\i database_schema_postgres.sql
```

### 3. Verify Tables
```bash
# List all tables
\dt

# Describe a specific table
\d surveys
```

## PostgreSQL Features Used

### 1. SERIAL Type
```sql
id SERIAL PRIMARY KEY
```
- Automatically creates a SEQUENCE
- Equivalent to MySQL's AUTO_INCREMENT

### 2. ENUM Type
```sql
CREATE TYPE question_type AS ENUM (
    'short_text',
    'long_text',
    ...
);
```
- Strongly-typed enumeration
- Better than VARCHAR for question types

### 3. JSONB
```sql
file_properties JSONB
selected_values JSONB
```
- Binary JSON format (more efficient than JSON)
- Supports indexing and queries
- Better performance than MySQL JSON

### 4. Triggers for Timestamp Updates
```sql
CREATE TRIGGER surveys_update_timestamp
BEFORE UPDATE ON surveys
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();
```
- Automatically updates `updated_at` on record modification
- MySQL uses `ON UPDATE CURRENT_TIMESTAMP`, PostgreSQL uses triggers

### 5. Constraints
```sql
CONSTRAINT unique_survey_question UNIQUE (survey_id, name)
```
- Named constraints for easier management

## Connecting to PostgreSQL

### Using psql (command line)
```bash
psql -U postgres -d sky_survey_db
```

### Using Python
You'll need to update your `database.py` to use PostgreSQL:

```python
import psycopg2
from psycopg2 import pool

db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),  # PostgreSQL default port
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "sky_survey_db"),
}

# Create connection pool
connection_pool = pool.SimpleConnectionPool(1, 20, **db_config)
```

### Install PostgreSQL Python Driver
```bash
pip install psycopg2-binary
```

## Differences in Python Code

### MySQL
```python
cursor.execute("SELECT * FROM surveys WHERE id = %s", (survey_id,))
```

### PostgreSQL
```python
cursor.execute("SELECT * FROM surveys WHERE id = %s", (survey_id,))
```
- Same parameter style `%s`
- Works with both MySQL and PostgreSQL

## Performance Considerations

PostgreSQL advantages:
- **JSONB**: Better performance for JSON queries than MySQL JSON
- **Triggers**: More efficient for automatic timestamp updates
- **Indexes**: More flexible index types available
- **ENUM**: Strongly typed, prevents invalid values

## Backup and Restore

### Backup Database
```bash
pg_dump -U postgres -d sky_survey_db > backup.sql
```

### Restore Database
```bash
psql -U postgres -d sky_survey_db < backup.sql
```

## Troubleshooting

### Issue: "Permission denied for schema public"
```bash
# Grant permissions
psql -U postgres -d sky_survey_db
GRANT ALL ON SCHEMA public TO postgres;
```

### Issue: "Type does not exist: question_type"
- Ensure the `CREATE TYPE` statement runs before creating the `questions` table
- The schema file handles this automatically

### Issue: Connection refused
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Check default port is 5432 (not 3306)

## Migration from MySQL to PostgreSQL

If migrating existing data:

1. Export MySQL data:
   ```bash
   mysqldump -u root -p sky_survey_db > mysql_data.sql
   ```

2. Create PostgreSQL schema:
   ```bash
   psql -U postgres -d sky_survey_db -f database_schema_postgres.sql
   ```

3. Migrate data (may need conversion scripts for ENUM and JSON types)

4. Verify data integrity

## Environment Variables (.env)

Update your `.env` file for PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=sky_survey_db
DB_POOL_SIZE=10
```

## Testing the Schema

Verify all tables and functions:

```bash
# Connect to database
psql -U postgres -d sky_survey_db

# List all tables
\dt

# List all types
\dT

# List all functions
\df

# Show table structure
\d surveys
\d questions

# Count records
SELECT COUNT(*) FROM surveys;
```

## Notes

- All tables have cascading foreign keys (ON DELETE CASCADE)
- All timestamps use UTC (CURRENT_TIMESTAMP)
- JSONB is used instead of JSON for better performance
- Triggers automatically update `updated_at` timestamps
- All indexes follow naming convention: `idx_tablename_columnname`

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL JSONB vs JSON](https://www.postgresql.org/docs/current/datatype-json.html)
- [PostgreSQL Triggers](https://www.postgresql.org/docs/current/sql-createtrigger.html)
- [PostgreSQL Enum Types](https://www.postgresql.org/docs/current/datatype-enum.html)
