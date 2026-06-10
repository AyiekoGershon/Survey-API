from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

class QuestionType(str, Enum):
    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"
    EMAIL = "email"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    FILE = "file"


# Database Models (for ORM-like operations)
class SurveyDB:
    def __init__(self, id: Optional[int] = None, name: Optional[str] = None,
                 description: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 is_active: bool = True):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_active = is_active


class QuestionDB:
    def __init__(self, id: Optional[int] = None, survey_id: Optional[int] = None,
                 name: Optional[str] = None, type: Optional[str] = None,
                 text: Optional[str] = None, description: Optional[str] = None,
                 required: bool = False, sort_order: int = 0,
                 file_properties: Optional[Dict[str, Any]] = None):
        self.id = id
        self.survey_id = survey_id
        self.name = name
        self.type = type
        self.text = text
        self.description = description
        self.required = required
        self.sort_order = sort_order
        self.file_properties = file_properties


class OptionDB:
    def __init__(self, id: Optional[int] = None, question_id: Optional[int] = None,
                 option_value: Optional[str] = None,
                 option_label: Optional[str] = None,
                 sort_order: int = 0):
        self.id = id
        self.question_id = question_id
        self.option_value = option_value
        self.option_label = option_label
        self.sort_order = sort_order


class ResponseDB:
    def __init__(self, id: Optional[int] = None, survey_id: Optional[int] = None,
                 user_email: Optional[str] = None,
                 submitted_at: Optional[datetime] = None):
        self.id = id
        self.survey_id = survey_id
        self.user_email = user_email
        self.submitted_at = submitted_at


class AnswerTextDB:
    def __init__(self, id: Optional[int] = None, response_id: Optional[int] = None,
                 question_id: Optional[int] = None, value: Optional[str] = None):
        self.id = id
        self.response_id = response_id
        self.question_id = question_id
        self.value = value


class CertificateDB:
    def __init__(self, id: Optional[int] = None, response_id: Optional[int] = None,
                 filename: Optional[str] = None, file_path: Optional[str] = None,
                 uploaded_at: Optional[datetime] = None):
        self.id = id
        self.response_id = response_id
        self.filename = filename
        self.file_path = file_path
        self.uploaded_at = uploaded_at
