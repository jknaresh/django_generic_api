from pydantic import BaseModel, EmailStr, Field, constr, validator
from typing import Optional, Dict, Any, List


class SaveInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    organization_id: str
    phone_number: Optional[str] = None
    job_title: Optional[str] = None
    description: Optional[str] = None


class SavePayload(BaseModel):
    modelName: str
    id: Optional[str] = None
    saveInput: SaveInput

    # Additional validations if needed
    @validator("modelName")
    def validate_model_name(cls, v):
        if not v:
            raise ValueError("modelName is required")
        return v


class FetchFilter(BaseModel):
    operator: str
    name: str
    value: List[Any]


class FetchPayload(BaseModel):
    modelName: str
    fields: List[str]
    filters: Optional[List[FetchFilter]] = None

    @validator("modelName")
    def validate_model_name(cls, v):
        if not v:
            raise ValueError("modelName is required")
        return v

    @validator("fields")
    def validate_fields(cls, v):
        if not v:
            raise ValueError("fields must not be empty")
        return v

    @validator("filters")
    def validate_fields(cls, v):
        if not v:
            raise ValueError("filters must not be empty")
        return v
