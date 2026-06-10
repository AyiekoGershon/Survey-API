# Quick Reference Guide

## 📋 Most Useful Commands

### Setup & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Create database
mysql -u root -p < database_schema.sql

# Validate project
python validate.py
```

### Running the API
```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app

# Custom port
uvicorn app.main:app --port 8001

# With workers (production)
uvicorn app.main:app --workers 4
```

### Testing
```bash
# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/

# Create survey
curl -X POST "http://localhost:8000/api/surveys" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "name=My+Survey&description=Test"

# List surveys
curl http://localhost:8000/api/surveys

# Get specific survey
curl http://localhost:8000/api/surveys/1
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `app/main.py` | Application entry point |
| `app/database.py` | Database connection |
| `app/routers/surveys.py` | Survey endpoints |
| `app/routers/questions.py` | Question endpoints |
| `app/routers/responses.py` | Response endpoints |
| `app/routers/certificates.py` | Certificate endpoints |
| `app/services/xml_service.py` | XML conversion |
| `database_schema.sql` | Database schema |
| `.env` | Configuration |
| `requirements.txt` | Dependencies |

---

## 🔗 API Endpoints Summary

### Surveys
- `POST /api/surveys` - Create
- `GET /api/surveys` - List
- `GET /api/surveys/{id}` - Get
- `PUT /api/surveys/{id}` - Update
- `DELETE /api/surveys/{id}` - Delete

### Questions
- `POST /api/surveys/{id}/questions` - Create
- `GET /api/surveys/{id}/questions` - List
- `PUT /api/questions/{id}` - Update
- `DELETE /api/questions/{id}` - Delete

### Responses
- `POST /api/surveys/{id}/responses` - Submit
- `GET /api/surveys/{id}/responses` - List

### Certificates
- `GET /api/certificates/{id}` - Download
- `GET /api/responses/{id}/certificates` - List

---

## 🐛 Common Issues & Solutions

### Problem: "Port 8000 in use"
```bash
# Use different port
uvicorn app.main:app --port 8001
```

### Problem: "No module named 'mysql'"
```bash
# Install dependencies
pip install -r requirements.txt
```

### Problem: "Can't connect to database"
```bash
# Check .env configuration
cat .env

# Test database connection
mysql -u root -p -h localhost
```

### Problem: "Upload directory not found"
```bash
# Create uploads directory
mkdir -p app/uploads
```

---

## 📊 Response Format

All responses are in XML:
```xml
<survey>
  <id>1</id>
  <name>My Survey</name>
  <description>A test survey</description>
</survey>
```

---

## 🚀 Deployment Tips

1. Use environment-specific `.env` files
2. Update CORS settings for production
3. Enable HTTPS
4. Setup database backups
5. Monitor API health with `/health` endpoint
6. Use Postman for testing
7. Check logs for errors
8. Load test before going live

---

## 📚 Documentation Links

- **Full Setup**: See [README.md](README.md)
- **Implementation Details**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Verification Guide**: See [VERIFICATION.md](VERIFICATION.md)
- **Complete Summary**: See [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)
- **API Tests**: See [Sky_Survey_API.postman_collection.json](Sky_Survey_API.postman_collection.json)

---

## 🔑 Environment Variables

```env
DB_HOST=localhost          # Database host
DB_PORT=3306              # Database port
DB_USER=root              # Database user
DB_PASSWORD=              # Database password
DB_NAME=sky_survey_db     # Database name
DB_POOL_SIZE=10           # Connection pool size
```

---

## 📦 Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
mysql-connector-python==8.2.0
pydantic==2.5.0
python-dotenv==1.0.0
python-multipart==0.0.6
pydantic-extra-types==2.4.0
```

---

## ✅ Quick Validation

```bash
# Validate everything
python validate.py

# Check specific file
python -m py_compile app/main.py

# List endpoints (from Swagger UI)
# Visit: http://localhost:8000/docs
```

---

## 🎯 Development Workflow

1. Make code changes
2. Run validation: `python validate.py`
3. Start API: `uvicorn app.main:app --reload`
4. Test endpoints in Swagger UI: `http://localhost:8000/docs`
5. Check logs for errors
6. Commit changes when ready

---

## 💾 Database Management

```bash
# Create database
mysql -u root -p < database_schema.sql

# Access database
mysql -u root -p sky_survey_db

# View tables
SHOW TABLES;

# View survey structure
DESCRIBE surveys;

# Clear test data (recreate)
mysql -u root -p sky_survey_db < database_schema.sql
```

---

## 📝 Common Tasks

### Add a new survey
```bash
curl -X POST "http://localhost:8000/api/surveys" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "name=Customer+Survey&description=For+customer+feedback"
```

### Add question to survey
```bash
curl -X POST "http://localhost:8000/api/surveys/1/questions" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "name=q1&type=short_text&text=What+is+your+name?"
```

### Submit response
Use Postman or form submission with email and answers

### Download certificate
```bash
curl "http://localhost:8000/api/certificates/1" > certificate.pdf
```

---

## 🔍 Debugging Tips

1. **Check logs**: Look at terminal output when running API
2. **Use Swagger UI**: http://localhost:8000/docs for interactive testing
3. **Test with curl**: Verify endpoints from command line
4. **Check database**: Connect directly to verify data
5. **Validate syntax**: `python validate.py`
6. **Check imports**: `python -c "import app.main"`

---

**For more details, see the full documentation in README.md and VERIFICATION.md**
