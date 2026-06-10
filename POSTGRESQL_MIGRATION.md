# MySQL to PostgreSQL Migration Guide

## Quick Start: Switch to PostgreSQL

### Files Provided

1. **database_schema_postgres.sql** - PostgreSQL-compatible schema
2. **database_postgres.py** - PostgreSQL database connection module
3. **POSTGRESQL_SETUP.md** - Detailed PostgreSQL setup guide

## Step-by-Step Migration

### Step 1: Install PostgreSQL Driver
```bash
pip install psycopg2-binary
```

### Step 2: Create PostgreSQL Database
```bash
# Using createdb command
createdb sky_survey_db

# Or using psql
psql -U postgres
CREATE DATABASE sky_survey_db;
```

### Step 3: Run the Schema
```bash
psql -U postgres -d sky_survey_db -f database_schema_postgres.sql
```

### Step 4: Update Environment Variables
Edit `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=sky_survey_db
DB_POOL_SIZE=10
```

### Step 5: Switch Database Module

**Option A: Replace database.py**
```bash
# Backup original
copy app\database.py app\database_mysql.py

# Use PostgreSQL version
copy database_postgres.py app\database.py
```

**Option B: Use PostgreSQL version directly**
Update `app/main.py` and all routers:
```python
# Change from:
from app.database import get_db_connection

# To:
from app.database_postgres import get_db_connection, return_db_connection
```

### Step 6: Test Connection
```bash
python -c "
from app.database_postgres import init_database
if init_database():
    print('✓ PostgreSQL connection successful')
else:
    print('✗ Connection failed')
"
```

### Step 7: Start API
```bash
uvicorn app.main:app --reload
```

## Code Changes Needed

### If using `database_postgres.py` as-is

The `database_postgres.py` module provides compatibility wrappers, but you may need to update cursor usage in routers:

**MySQL Style:**
```python
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM surveys")
row = cursor.fetchone()
print(row["id"], row["name"])
```

**PostgreSQL Style:**
```python
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cursor.execute("SELECT * FROM surveys")
row = cursor.fetchone()
print(row["id"], row["name"])  # Same API!
```

### For lastrowid (Insert IDs)

**MySQL:**
```python
cursor.execute("INSERT INTO surveys (name) VALUES (%s)", (name,))
survey_id = cursor.lastrowid
```

**PostgreSQL (with RETURNING):**
```python
cursor.execute(
    "INSERT INTO surveys (name) VALUES (%s) RETURNING id",
    (name,)
)
survey_id = cursor.fetchone()[0]
```

Or without RETURNING:
```python
cursor.execute("INSERT INTO surveys (name) VALUES (%s)", (name,))
conn.commit()
# Get the ID from SEQUENCE
cursor.execute("SELECT lastval()")
survey_id = cursor.fetchone()[0]
```

### Updating All Routers for PostgreSQL

If you want full PostgreSQL support without compatibility layers:

1. Replace `cursor(dictionary=True)` with `cursor_factory=psycopg2.extras.DictCursor`
2. Replace `cursor.lastrowid` with `RETURNING id` clause
3. Replace `conn.commit()` after each operation
4. Import `psycopg2.extras` for DictCursor

## Key API Differences

| Operation | MySQL | PostgreSQL |
|-----------|-------|-----------|
| Get last insert ID | `cursor.lastrowid` | Use `RETURNING id` |
| Dictionary cursor | `cursor(dictionary=True)` | `cursor(cursor_factory=DictCursor)` |
| Connection commit | `conn.commit()` | `conn.commit()` |
| Boolean values | `TRUE/FALSE` | `true/false` (UPPERCASE or lowercase) |
| JSON queries | `JSON_EXTRACT()` | `->`/`->>` operators |
| ENUM validation | Runtime | Compile-time (stronger) |

## Testing the Migration

### 1. Test Database Connection
```bash
python -c "from app.database_postgres import init_database; print('✓ OK' if init_database() else '✗ FAIL')"
```

### 2. Test Schema
```bash
psql -U postgres -d sky_survey_db -c "\dt"
```

### 3. Test API Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/surveys
```

### 4. Test Insert Operations
```bash
curl -X POST "http://localhost:8000/api/surveys" \
     -d "name=Test&description=Test+Survey"
```

## Rollback to MySQL

If you need to switch back:

1. Restore original `database.py`:
   ```bash
   copy app\database_mysql.py app\database.py
   ```

2. Restore MySQL database:
   ```bash
   mysql -u root -p < database_schema.sql
   ```

3. Restart API server

## Advantages of PostgreSQL

- **JSONB**: Superior JSON support and performance
- **ENUM**: Type-safe enumerations
- **Triggers**: Automatic timestamp updates without application code
- **Stronger typing**: Compile-time validation of ENUM values
- **Better performance**: Generally faster for complex queries
- **Open source**: Fully open source, no licensing concerns
- **Advanced features**: Window functions, CTEs, full-text search

## Advantages of MySQL

- **Simpler setup**: Easier for beginners
- **Wide hosting**: More shared hosting providers support it
- **Smaller footprint**: Lighter resource usage
- **Compatibility**: Better compatibility with older applications

## Performance Comparison

| Metric | MySQL | PostgreSQL |
|--------|-------|-----------|
| Startup time | Fast | Slower |
| Simple queries | Slightly faster | Slightly slower |
| Complex queries | Slower | Faster |
| JSON performance | Good | Excellent (JSONB) |
| Concurrent users | Good | Better |
| Transaction safety | ACID (InnoDB) | ACID (always) |

## Support

Both schemas are fully supported. Choose based on your infrastructure and preferences:

- **Use MySQL** if: You're on shared hosting or have MySQL expertise
- **Use PostgreSQL** if: You want advanced features and better performance

Both will work perfectly with the Sky Survey API.

## Troubleshooting PostgreSQL

### Connection Issues
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Connect directly
psql -U postgres -d sky_survey_db
```

### Schema Issues
```bash
# View tables
psql -U postgres -d sky_survey_db -c "\dt"

# View table structure
psql -U postgres -d sky_survey_db -c "\d surveys"

# View indexes
psql -U postgres -d sky_survey_db -c "\di"
```

### Data Issues
```bash
# Check for conflicts with ENUM types
psql -U postgres -d sky_survey_db -c "\dT"

# Verify triggers
psql -U postgres -d sky_survey_db -c "\dy"
```

## Next Steps

1. Review [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) for detailed information
2. Choose your database (MySQL or PostgreSQL)
3. Follow the appropriate setup guide
4. Start the API and test endpoints
5. Monitor logs for any issues

---

**Recommendation**: Use PostgreSQL for new projects, MySQL for existing infrastructure.
