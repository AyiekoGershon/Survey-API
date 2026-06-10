# Sky Survey API

A comprehensive REST API for survey management built with FastAPI and MySQL. This API allows administrators to create and manage surveys while enabling users to respond to surveys through web and mobile applications.

## Features

### Survey Management
- Create surveys
- Edit surveys  
- View surveys
- Delete surveys (soft and hard delete)

### Question Management
- Add questions to surveys
- Edit questions
- Delete questions
- Support for multiple question types:
  - Short Text
  - Long Text
  - Email
  - Single Choice
  - Multiple Choice
  - File Upload
- Manage options for choice-based questions

### Survey Responses
- Submit survey responses with multipart/form-data support
- Handle multiple file uploads
- View submitted responses
- Pagination support
- Filter responses by email address
- Download uploaded certificates

## Prerequisites

- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd simple-survey-api
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up the database:**
   - Create a MySQL database using the provided schema:
   ```bash
   mysql -u root -p < database_schema.sql
   ```

5. **Configure environment variables:**
   - Create a `.env` file in the root directory:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=sky_survey_db
   DB_POOL_SIZE=10
   ```

## Running Locally

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Surveys
- `POST /api/surveys` - Create a new survey
- `GET /api/surveys` - Get all surveys
- `GET /api/surveys/{survey_id}` - Get a specific survey
- `PUT /api/surveys/{survey_id}` - Update a survey
- `DELETE /api/surveys/{survey_id}` - Delete a survey

### Questions
- `POST /api/surveys/{survey_id}/questions` - Create a question
- `GET /api/surveys/{survey_id}/questions` - Get survey questions
- `PUT /api/questions/{question_id}` - Update a question
- `DELETE /api/questions/{question_id}` - Delete a question

### Responses
- `POST /api/surveys/{survey_id}/responses` - Submit a survey response
- `GET /api/surveys/{survey_id}/responses` - Get survey responses (with pagination and filtering)

### Certificates
- `GET /api/certificates/{certificate_id}` - Download a certificate
- `GET /api/responses/{response_id}/certificates` - Get certificates for a response

## Response Format

All API responses are in XML format by default. The API uses a flexible XML serialization system that converts Python dictionaries to XML.

### Example Response
```xml
<?xml version="1.0" encoding="utf-8"?>
<surveys>
    <survey_1>
        <@id>1</@id>
        <name>Graduate Developer Survey</name>
        <description>Initial screening survey</description>
    </survey_1>
</surveys>
```

## Database Schema

The database consists of the following main tables:

- **surveys**: Main survey records
- **questions**: Survey questions with type information
- **options**: Answer options for choice-based questions
- **responses**: User responses to surveys
- **answer_texts**: Text-based answers
- **answer_choices**: Choice-based answers
- **certificates**: Uploaded file certificates

For detailed schema information, refer to `database_schema.sql`.

## Technologies Used

- **Framework**: FastAPI 0.104.1
- **Web Server**: Uvicorn
- **Database**: MySQL 5.7+
- **Language**: Python 3.8+
- **Data Validation**: Pydantic

## Project Structure

```
simple-survey-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application setup
│   ├── database.py             # Database connection management
│   ├── models.py               # Data models
│   ├── schemas.py              # Request/response schemas
│   ├── routers/                # API route handlers
│   │   ├── surveys.py
│   │   ├── questions.py
│   │   ├── responses.py
│   │   └── certificates.py
│   ├── services/               # Business logic
│   │   ├── xml_service.py      # XML serialization
│   │   └── file_service.py     # File handling
│   └── uploads/                # Uploaded files storage
├── database_schema.sql         # Database initialization script
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
└── README.md                   # This file
```

## Assumptions Made

1. **Database Pool**: Connection pooling is implemented using MySQL's built-in pooling for performance
2. **Soft Delete**: By default, surveys are soft deleted (marked inactive) rather than hard deleted
3. **File Uploads**: File uploads are stored in `app/uploads/<response_id>/` directory
4. **XML Response**: All responses are in XML format for API consistency
5. **Email Validation**: Email validation is performed at the API level
6. **Concurrent Responses**: Multiple users can respond to the same survey simultaneously
7. **File Formats**: File uploads are primarily PDF format by default but can be configured
8. **Timezone**: All timestamps use the server's timezone (CURRENT_TIMESTAMP)

## Error Handling

The API returns standard HTTP status codes and error messages:

- `200 OK` - Successful GET request
- `201 Created` - Successful resource creation
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Contributing

To maintain code quality:
1. Follow PEP 8 style guidelines
2. Add meaningful commit messages
3. Test changes locally before submitting
4. Update documentation for API changes

## License

This project is part of the Sky World Limited Software Engineering Internship Program.
