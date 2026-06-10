from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import QuestionType

# Survey schemas
class SurveyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = ""

class SurveyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None

class SurveyResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

# Option schemas
class OptionCreate(BaseModel):
    value: str
    label: str

class OptionResponse(BaseModel):
    id: int
    value: str
    label: str
    sort_order: int

# File properties schema
class FileProperties(BaseModel):
    format: str = ".pdf"
    max_size_mb: int = 1
    multiple: bool = True

# Question schemas
class QuestionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: QuestionType
    text: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = ""
    required: bool = False
    options: Optional[List[OptionCreate]] = None
    file_properties: Optional[FileProperties] = None

class QuestionUpdate(BaseModel):
    name: Optional[str] = None
    text: Optional[str] = None
    description: Optional[str] = None
    required: Optional[bool] = None
    sort_order: Optional[int] = None

class QuestionResponse(BaseModel):
    id: int
    survey_id: int
    name: str
    type: QuestionType
    text: str
    description: str
    required: bool
    sort_order: int
    options: Optional[List[OptionResponse]] = None
    file_properties: Optional[FileProperties] = None

# Response schemas
class AnswerSubmit(BaseModel):
    question_name: str
    value: Any

class ResponseSubmit(BaseModel):
    email: EmailStr
    answers: Dict[str, Any]  # question_name -> answer

class AnswerResponse(BaseModel):
    question_id: int
    question_name: str
    value: str

class CertificateResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime

class ResponseDetailResponse(BaseModel):
    id: int
    user_email: str
    submitted_at: datetime
    answers: List[AnswerResponse]
    certificates: List[CertificateResponse]

class ResponseListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    responses: List[ResponseDetailResponse]