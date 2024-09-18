from typing import Optional, Any, List

from pydantic import BaseModel, EmailStr, field_validator, JsonValue


class SaveInputTemplate(BaseModel):
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
    saveInput: JsonValue

    # Additional validations if needed
    @field_validator("modelName")
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

    @field_validator("modelName")
    def validate_model_name(cls, v):
        if not v:
            raise ValueError("modelName is required")
        return v

    @field_validator("fields")
    def validate_fields(cls, v):
        if not v:
            raise ValueError("fields must not be empty")
        return v
