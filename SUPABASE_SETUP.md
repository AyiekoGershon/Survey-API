# Supabase Setup Guide

## Quick Answer: YES! ✅

The PostgreSQL schema works perfectly with **Supabase**. Supabase is PostgreSQL-based, so all our schema is compatible.

---

## Why Supabase?

Supabase is an excellent choice for the Sky Survey API because:

| Feature | Benefit |
|---------|---------|
| **PostgreSQL-based** | Perfect for our schema |
| **Free tier** | Generous free database (500MB) |
| **Managed** | No database maintenance |
| **Serverless** | Auto-scaling, no infrastructure |
| **Built-in Auth** | User authentication included |
| **Realtime** | WebSocket support for live updates |
| **Storage** | Built-in file storage (certificates) |
| **REST API** | Auto-generated REST API |

---

## Setup Steps

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up (free account)
3. Create new project
   - Project name: `sky-survey-api`
   - Password: Choose secure password
   - Region: Choose closest to you
   - Click "Create new project"

### 2. Wait for Database

The database will be created in ~2 minutes. You'll see:
- Project URL: `https://xxxxx.supabase.co`
- Database credentials (save these!)

### 3. Copy Connection Details

In Supabase dashboard:
1. Click "Settings" → "Database"
2. Copy the connection string or individual details

**Connection String Format:**
```
postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

**Connection Details:**
- **Host**: `db.xxxxx.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: (your chosen password)

### 4. Open SQL Editor

In Supabase dashboard:
1. Click "SQL Editor" (left sidebar)
2. Click "+ New Query"
3. Paste the contents of `database_schema_supabase.sql`
4. Click "Run"

**✓ Schema created in seconds!**

### 5. Update .env

Replace your `.env` file:

```env
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_supabase_password
DB_NAME=postgres
DB_POOL_SIZE=10
```

### 6. Update requirements.txt

Keep the same dependencies:
```
psycopg2-binary==2.9.9
```

(Or use `database_postgres.py` if not already using it)

### 7. Test Connection

```bash
# Test with psql
psql postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres

# Or run validation
python validate.py
```

### 8. Start API

```bash
uvicorn app.main:app --reload
```

---

## Supabase-Specific Features

### Option 1: File Storage for Certificates

Instead of saving to `app/uploads/`, use Supabase Storage:

```python
# Install Supabase SDK
pip install supabase python-dotenv

# In file_service.py
from supabase import create_client, Client

supabase: Client = create_client(
    "https://xxxxx.supabase.co",
    "your-anon-key"
)

def save_uploaded_file(file: UploadFile, response_id: int) -> str:
    """Save file to Supabase Storage"""
    file_path = f"certificates/{response_id}/{file.filename}"
    
    supabase.storage.from_("certificates").upload(
        file_path,
        file.file.read()
    )
    
    return file_path
```

### Option 2: Row Level Security (RLS)

Enable RLS for multi-tenant security:

```sql
-- In SQL Editor

-- Enable RLS on all tables
ALTER TABLE surveys ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;

-- Create policies (example: users see only their responses)
CREATE POLICY "Users can read own responses" ON responses
FOR SELECT USING (auth.uid()::text = user_email);
```

### Option 3: Realtime Subscriptions

Enable realtime updates:

```python
# Subscribe to new responses
supabase.on('*', 'responses', callback=on_response_change).subscribe()
```

---

## File Differences: MySQL vs PostgreSQL vs Supabase

| File | MySQL | PostgreSQL | Supabase |
|------|-------|-----------|----------|
| Schema | `database_schema.sql` | `database_schema_postgres.sql` | `database_schema_supabase.sql` |
| Driver | `mysql-connector-python` | `psycopg2-binary` | `psycopg2-binary` |
| Database Module | `app/database.py` | `app/database_postgres.py` | `app/database_postgres.py` |
| Setup | Local MySQL | Local PostgreSQL | Supabase cloud |

---

## Connection Methods

### Method 1: Direct PostgreSQL Connection (Recommended)

Use `database_postgres.py` as-is:

```python
from app.database_postgres import get_db_connection

# Works with Supabase directly
```

### Method 2: Supabase Python SDK

```bash
pip install supabase python-dotenv
```

```python
from supabase import create_client

supabase = create_client(
    "https://xxxxx.supabase.co",
    "your-anon-key"
)
```

### Method 3: Connection String

```bash
# Using psql
psql "postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres"
```

---

## Security Considerations for Supabase

### 1. Use Anon Key for Frontend
```env
SUPABASE_ANON_KEY=your-anon-key
```

### 2. Use Service Key for Backend
```env
SUPABASE_SERVICE_KEY=your-service-key
```

### 3. Enable Row Level Security
Uncomment RLS policies in schema:
```sql
ALTER TABLE surveys ENABLE ROW LEVEL SECURITY;
```

### 4. Use Auth Providers
Supabase supports:
- Email/Password
- Google OAuth
- GitHub OAuth
- Magic Links

---

## Cost Estimate (Supabase)

**Free Tier:**
- 500MB database storage
- 1GB file storage
- Unlimited API requests
- Perfect for development/testing

**Pricing:**
- Database: $25/month for additional storage
- Storage: $5/month per 100GB
- API calls: Included

---

## Advantages Over Self-Hosted PostgreSQL

| Feature | Supabase | Self-Hosted |
|---------|----------|------------|
| Setup time | 5 minutes | 1+ hours |
| Maintenance | 0% | 100% |
| Backups | Automatic | Manual |
| Uptime SLA | 99.9% | Depends |
| Cost (free) | Yes | No |
| Cost (paid) | $25+/month | $5+/month |
| Security updates | Automatic | Manual |

---

## Troubleshooting

### Issue: "Connection refused"
```
Check:
1. Supabase project is running
2. Connection string is correct
3. IP whitelist (Supabase allows all by default)
```

### Issue: "ENUM type not found"
```
Ensure schema ran completely - check for errors in SQL Editor
```

### Issue: "Table doesn't exist"
```
Verify schema executed successfully:
SELECT * FROM information_schema.tables WHERE table_schema='public';
```

### Issue: "Permission denied"
```
Use correct credentials (postgres user, not admin)
```

---

## Next Steps

1. **Create Supabase Account**: [supabase.com](https://supabase.com)
2. **Create Project**: Free tier
3. **Copy Connection Details**: Settings → Database
4. **Run Schema**: SQL Editor → Paste → Run
5. **Update .env**: DB credentials
6. **Start API**: `uvicorn app.main:app --reload`
7. **Test Endpoints**: `http://localhost:8000/docs`

---

## Alternatives to Supabase

If you prefer other managed PostgreSQL services:

| Service | Cost | Notes |
|---------|------|-------|
| **Supabase** | Free tier available | Recommended - Firebase-like features |
| **Railway** | $5/month | Simple, fast deployment |
| **Render** | Free tier available | Good for PostgreSQL |
| **Heroku** | $9+/month | Larger ecosystem |
| **AWS RDS** | $15+/month | Enterprise-grade |
| **DigitalOcean** | $15+/month | Managed databases |

---

## Deployment Architecture with Supabase

```
┌─────────────────────────────────────────┐
│     Sky Survey API (FastAPI)            │
│  (Your app - Python/Uvicorn)            │
└──────────────┬──────────────────────────┘
               │
               │ psycopg2
               │
┌──────────────▼──────────────────────────┐
│   Supabase PostgreSQL                   │
│  (Managed cloud database)               │
│  - 7 normalized tables                  │
│  - Automatic backups                    │
│  - Built-in monitoring                  │
└─────────────────────────────────────────┘
```

---

## Production Checklist for Supabase

- [ ] Enable HTTPS
- [ ] Use environment variables for credentials
- [ ] Enable Row Level Security
- [ ] Set up database backups
- [ ] Monitor database usage
- [ ] Use Service Key for backend operations
- [ ] Use Anon Key for frontend (if applicable)
- [ ] Enable API rate limiting
- [ ] Set up monitoring/alerts
- [ ] Review security settings

---

## Support & Documentation

- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)
- **PostgreSQL Docs**: [postgresql.org/docs](https://www.postgresql.org/docs/)
- **Sky Survey API**: See [README.md](README.md)
- **Database Setup**: See [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)

---

**TL;DR**: Yes! Use `database_schema_supabase.sql`, update `.env` with Supabase credentials, and you're ready to go! ✅
