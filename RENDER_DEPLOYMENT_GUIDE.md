# 🚀 Deploy Sky Survey API to Render

A complete step-by-step guide to deploying your FastAPI survey API on Render.com with PostgreSQL.

---

## 📋 Prerequisites

- [ ] A **GitHub** account (free — [github.com](https://github.com))
- [ ] A **Render** account (free — [render.com](https://render.com))
- [ ] Your code pushed to a GitHub repository

---

## Step 1: Push Your Code to GitHub

Open a terminal in `c:\Users\Admin\Desktop\sky\simple-survey-api` and run:

```bash
# Initialize Git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit — Sky Survey API"

# Create a repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/simple-survey-api.git
git branch -M main
git push -u origin main
```

> **Important:** Make sure to replace `YOUR_USERNAME` with your actual GitHub username.

---

## Step 2: Create a PostgreSQL Database on Render

1. Log in to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Fill in the form:

   | Field | Value |
   |-------|-------|
   | **Name** | `sky-survey-db` |
   | **Database** | `sky_survey_db` |
   | **User** | (auto-generated) |
   | **Region** | Pick one closest to your users (e.g. `Frankfurt`) |
   | **PostgreSQL Version** | `15` |
   | **Plan** | **Free** (expires after 90 days, fine for dev) or **Starter** ($7/month) |

4. Click **"Create Database"**
5. Wait ~2-3 minutes for it to provision ⏳

### Get your database credentials

Once the database is ready, scroll down to **"Connections"** and copy:
- **Internal Database URL** (used if your web service is on Render)
- **External Database URL** (used to connect from your local machine)

You'll see individual fields too:
- `Hostname` → your `DB_HOST`
- `Port` → your `DB_PORT` (usually `5432`)
- `Database` → your `DB_NAME`
- `Username` → your `DB_USER`
- `Password` → your `DB_PASSWORD`

---

## Step 3: Run the Database Schema on Render's PostgreSQL

### Option A: Using Render's Shell (if available on paid plans)

```bash
PGPASSWORD=<password> psql -h <host> -U <user> -d <database> -f database_schema_postgres.sql
```

### Option B: Using Supabase SQL Editor (if using Supabase as intermediary)

Since your `.env` already points to Supabase, you just need to ensure the schema is applied there. Go to your Supabase dashboard → **SQL Editor** → paste `database_schema_supabase.sql` → **Run**.

### Option C: Using pgAdmin or any PostgreSQL client

1. Download [pgAdmin](https://www.pgadmin.org/download/) or use DBeaver
2. Connect using the External Database URL from Render
3. Open and run `database_schema_postgres.sql`

---

## Step 4: Deploy the Web Service on Render

### Method A: Deploy via Render Dashboard (Easiest)

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. **Connect your GitHub repo**: Click "Connect" and select `simple-survey-api`
4. Fill in the form:

   | Field | Value |
   |-------|-------|
   | **Name** | `sky-survey-api` |
   | **Region** | Same as your database (e.g. `Frankfurt`) |
   | **Branch** | `main` |
   | **Runtime** | `Python` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | **Plan** | **Free** |

5. Scroll to **"Environment Variables"** and add:

   | Key | Value |
   |-----|-------|
   | `DB_HOST` | Your Render DB hostname |
   | `DB_PORT` | `5432` |
   | `DB_USER` | Your Render DB username |
   | `DB_PASSWORD` | Your Render DB password |
   | `DB_NAME` | `sky_survey_db` |
   | `DB_POOL_SIZE` | `5` |

6. Click **"Create Web Service"**

### Method B: Deploy via render.yaml (Blueprint - Automated)

If you want a fully automated setup, use the provided `render.yaml` file:

1. Push `render.yaml` to GitHub (it's already created for you)
2. On Render dashboard, click **"New +"** → **"Blueprint"**
3. Connect your GitHub repo
4. Render will automatically create **both the database AND the web service**
5. You'll just need to review and click **"Apply"**

> ⚠️ **Note:** Before using `render.yaml`, edit it and replace `YOUR_USERNAME` with your actual GitHub username in the `repo` field.

---

## Step 5: Wait for Deployment

After creating the web service:

1. Render will start building your app (takes 2-5 minutes)
2. Watch the **"Events"** and **"Logs"** tabs for progress
3. When you see: `Application startup complete.` ✅ — it's live!

Your app will be available at:
```
https://sky-survey-api.onrender.com
```

---

## Step 6: Verify It's Working

### Test the root endpoint:

```bash
curl https://sky-survey-api.onrender.com/
```

Expected response:
```json
{"message": "Sky Survey API", "docs": "/docs", "redoc": "/redoc"}
```

### Test the health endpoint:

```bash
curl https://sky-survey-api.onrender.com/health
```

Expected response:
```json
{"status": "healthy"}
```

### Open the interactive API docs:

```
https://sky-survey-api.onrender.com/docs
```

---

## Step 7: Set Up a Custom Domain (Optional)

1. In your Render dashboard, go to **"Settings"** → **"Custom Domain"**
2. Enter your domain (e.g. `api.yoursite.com`)
3. Add the DNS `CNAME` record at your domain provider pointing to `sky-survey-api.onrender.com`
4. Wait for SSL certificate provisioning (~5 minutes)

---

## 🔄 Redeploying After Changes

### Automatic (recommended):
- Every time you push to `main` branch, Render automatically redeploys

### Manual:
1. Go to Render dashboard → your web service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## ⚙️ Environment Variables in Render

You can manage environment variables at any time:

1. Go to Render dashboard → your web service → **"Environment"**
2. Click **"Add Environment Variable"** or **"Edit"**

### Required Variables:

```env
DB_HOST=<your-render-database-hostname>
DB_PORT=5432
DB_USER=<your-render-database-username>
DB_PASSWORD=<your-render-database-password>
DB_NAME=sky_survey_db
DB_POOL_SIZE=5
```

---

## 🗄️ Persistent Disk for File Uploads

The API saves uploaded certificates to `app/uploads/`. Render's **free plan** has an **ephemeral filesystem** — files disappear after redeploy.

### Solution: Add a Render Disk

1. Go to your web service → **"Disks"**
2. Click **"Add Disk"**
3. Set mount path: `/opt/render/project/src/app/uploads`
4. Size: `1 GB` (free)
5. Click **Save**

After adding the disk, the `file_service.py` will use the persistent disk path instead.

> **Better long-term solution:** Use Supabase Storage or AWS S3 for file uploads.

---

## 🔐 Important Security Notes

1. **Database credentials** are automatically encrypted in Render
2. **Never commit your `.env`** file to GitHub — it's already in `.gitignore` ✅
3. **Use Render's environment variables** (not a `.env` file) in production
4. **The free database expires** after 90 days — set a reminder to migrate

---

## 💰 Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| Web Service | Free | $0/month |
| PostgreSQL | Free | $0/month (90 days) |
| **Total** | | **$0/month (for 90 days)** |

To keep it running longer, upgrade to:
- **PostgreSQL Starter**: $7/month
- **Web Service Starter**: $7/month
- **Total**: **$14/month**

---

## 🛠 Troubleshooting

### ❌ "Application crashed on startup"
1. Check **"Logs"** tab in Render dashboard
2. Most common cause: missing `psycopg2-binary` — ensure `requirements.txt` includes it
3. Verify DB credentials are correct in environment variables

### ❌ "psycopg2 not found" error
Run locally to test:
```bash
pip install psycopg2-binary
```

### ❌ "Connection refused" to database
1. Ensure web service and database are in the **same region**
2. Use **Internal Database URL** (not External) if both are on Render
3. Check that the database user has correct permissions

### ❌ "Database does not exist"
1. Connect to Render PostgreSQL using psql or pgAdmin
2. Run: `CREATE DATABASE sky_survey_db;`
3. Then run the schema SQL

### ❌ "No module named app.main"
1. Make sure `startCommand` is: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
2. Verify your file structure has `app/main.py`

### ❌ Can't access `/docs`
The Swagger docs should work automatically. Try:
```
https://sky-survey-api.onrender.com/docs
```

---

## 📚 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Render PostgreSQL Guide**: https://render.com/docs/postgresql
- **FastAPI Deployment Docs**: https://fastapi.tiangolo.com/deployment/

---

## ✅ Deployment Checklist Recap

- [ ] **Step 1:** Push code to GitHub
- [ ] **Step 2:** Create PostgreSQL database on Render
- [ ] **Step 3:** Run schema SQL on the database
- [ ] **Step 4:** Create web service on Render
- [ ] **Step 5:** Wait for build & deploy
- [ ] **Step 6:** Verify with `/health` endpoint
- [ ] **Step 7:** (Optional) Set up custom domain
- [ ] **Step 8:** Add persistent disk for file uploads
- [ ] **Step 9:** Test with `/docs` (Swagger UI)
- [ ] **Step 10:** 🎉 Celebrate!

---

_Having issues? Check the Render dashboard logs or open an issue on GitHub._
