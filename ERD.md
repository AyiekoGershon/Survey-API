# Sky Survey API - Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    SURVEYS ||--o{ QUESTIONS : "has"
    SURVEYS ||--o{ RESPONSES : "receives"
    QUESTIONS ||--o{ OPTIONS : "has"
    QUESTIONS ||--o{ ANSWER_TEXTS : "text-answered-by"
    QUESTIONS ||--o{ ANSWER_CHOICES : "choice-answered-by"
    RESPONSES ||--o{ ANSWER_TEXTS : "contains"
    RESPONSES ||--o{ ANSWER_CHOICES : "contains"
    RESPONSES ||--o{ CERTIFICATES : "has"

    SURVEYS {
        int id PK "Primary Key, auto-increment"
        varchar name "Survey name, max 255 chars"
        text description "Optional description"
        timestamp created_at "Default: CURRENT_TIMESTAMP"
        timestamp updated_at "Default: CURRENT_TIMESTAMP"
        boolean is_active "Default: TRUE, soft delete flag"
    }

    QUESTIONS {
        int id PK "Primary Key, auto-increment"
        int survey_id FK "References surveys(id)"
        varchar name "Question name, max 255 chars, unique per survey"
        enum type "Question type enum"
        varchar text "Question text, max 500 chars"
        text description "Optional question description"
        boolean required "Default: FALSE"
        int sort_order "Display order, default: 0"
        json file_properties "File upload config {format, max_size_mb, multiple}"
        timestamp created_at "Default: CURRENT_TIMESTAMP"
        timestamp updated_at "Default: CURRENT_TIMESTAMP"
    }

    OPTIONS {
        int id PK "Primary Key, auto-increment"
        int question_id FK "References questions(id)"
        varchar option_value "Option value for storage"
        varchar option_label "Option label for display"
        int sort_order "Display order, default: 0"
        timestamp created_at "Default: CURRENT_TIMESTAMP"
    }

    RESPONSES {
        int id PK "Primary Key, auto-increment"
        int survey_id FK "References surveys(id)"
        varchar user_email "Respondent email address"
        timestamp submitted_at "Submission timestamp"
        timestamp created_at "Default: CURRENT_TIMESTAMP"
    }

    ANSWER_TEXTS {
        int id PK "Primary Key, auto-increment"
        int response_id FK "References responses(id)"
        int question_id FK "References questions(id)"
        text value "Text answer value"
        timestamp created_at "Default: CURRENT_TIMESTAMP"
    }

    ANSWER_CHOICES {
        int id PK "Primary Key, auto-increment"
        int response_id FK "References responses(id)"
        int question_id FK "References questions(id)"
        json selected_values "Selected option values (JSON array)"
        timestamp created_at "Default: CURRENT_TIMESTAMP"
    }

    CERTIFICATES {
        int id PK "Primary Key, auto-increment"
        int response_id FK "References responses(id)"
        varchar filename "Uploaded file name, max 500 chars"
        varchar file_path "Server file path, max 500 chars"
        timestamp uploaded_at "Upload timestamp"
    }
```

## Table Relationships Summary

| Parent Table | Child Table | Relationship | Foreign Key | Constraint |
|---|---|---|---|---|
| **surveys** | **questions** | One-to-Many | `survey_id` | ON DELETE CASCADE |
| **surveys** | **responses** | One-to-Many | `survey_id` | ON DELETE CASCADE |
| **questions** | **options** | One-to-Many | `question_id` | ON DELETE CASCADE |
| **questions** | **answer_texts** | One-to-Many | `question_id` | ON DELETE CASCADE |
| **questions** | **answer_choices** | One-to-Many | `question_id` | ON DELETE CASCADE |
| **responses** | **answer_texts** | One-to-Many | `response_id` | ON DELETE CASCADE |
| **responses** | **answer_choices** | One-to-Many | `response_id` | ON DELETE CASCADE |
| **responses** | **certificates** | One-to-Many | `response_id` | ON DELETE CASCADE |

## Unique Constraints

| Table | Constraint Name | Columns |
|---|---|---|
| **questions** | `unique_survey_question` | `(survey_id, name)` |
| **answer_texts** | `unique_answer_text` | `(response_id, question_id)` |
| **answer_choices** | `unique_answer_choice` | `(response_id, question_id)` |

## Question Types (ENUM)

| Value | Description |
|---|---|
| `short_text` | Short text answer |
| `long_text` | Long text/paragraph answer |
| `email` | Email address answer |
| `single_choice` | Single choice (radio button) |
| `multiple_choice` | Multiple choice (checkbox) |
| `file` | File upload (e.g., PDF certificate) |
