from enum import Enum
from typing import Optional, Any, List, Union

from pydantic import (
    BaseModel,
    field_validator,
    JsonValue,
    SecretStr,
    EmailStr,
    Field,
    model_validator,
)

from .utils import PydanticConfigV1
from django.conf import settings


class SavePayload(BaseModel, PydanticConfigV1):
    modelName: str
    id: Optional[Union[int, str]] = None
    saveInput: JsonValue


class GenericUserUpdatePayload(BaseModel, PydanticConfigV1):
    saveInput: JsonValue


class OperatorByEnum(str, Enum):
    EQ = "eq"
    IN = "in"
    NOT = "not"
    GT = "gt"
    LIKE = "like"
    ILIKE = "ilike"


class OperationByEnum(str, Enum):
    OR = "or"
    AND = "and"


class FetchFilter(BaseModel, PydanticConfigV1):
    operator: OperatorByEnum
    name: str
    value: List[Any]
    operation: Optional[OperationByEnum] = OperationByEnum.AND


class OrderByEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class FetchSort(BaseModel, PydanticConfigV1):
    field: str
    order_by: OrderByEnum


class FetchPayload(BaseModel, PydanticConfigV1):
    modelName: str
    fields: List[str]
    filters: List[FetchFilter]
    pageNumber: Optional[int] = Field(default=1, ge=1)
    pageSize: Optional[int] = Field(default=10, ge=1, le=100)
    sort: Optional[FetchSort] = None
    distinct: Optional[bool] = None

    @field_validator("filters")
    def validate_filters(cls, v):
        if v:
            for f in v:
                value = getattr(f, "value", [])
                len_value = len(value)
                operator = getattr(f, "operator", "")

                if len_value < 1:
                    raise ValueError("Filters must have at least one value")
                elif len_value > 1 and operator != OperatorByEnum.IN:
                    raise ValueError("Multiple filters not supported")
        return v


class GenericLoginPayload(BaseModel, PydanticConfigV1):
    email: EmailStr
    password: SecretStr
    captcha_key: Optional[str] = None
    captcha_value: Optional[str] = None

    @model_validator(mode="before")
    def validate_captcha(cls, values):
        captcha_required = getattr(settings, "CAPTCHA_REQUIRED", False)
        captchaKey = values.get("captcha_key")
        captchaValue = values.get("captcha_value")

        # If CAPTCHA_REQUIRED is True, ensure captcha_key and captcha_value are provided
        if captcha_required:
            if not captchaKey or not captchaValue:
                raise ValueError(
                    "Captcha key and value are required when `CAPTCHA_REQUIRED` is True."
                )
        else:
            # If CAPTCHA_REQUIRED is False, ensure captcha_key and captcha_value are NOT provided
            if captchaKey or captchaValue:
                raise ValueError(
                    "Captcha key and value should not be provided when `CAPTCHA_REQUIRED` is False."
                )

        return values


class GenericRegisterPayload(BaseModel, PydanticConfigV1):
    email: EmailStr
    password: SecretStr
    password1: SecretStr
    captcha_key: Optional[str] = None
    captcha_value: Optional[str] = None

    @model_validator(mode="before")
    def validate_captcha(cls, values):
        captcha_required = getattr(settings, "CAPTCHA_REQUIRED", False)
        captchaKey = values.get("captcha_key")
        captchaValue = values.get("captcha_value")

        # If CAPTCHA_REQUIRED is True, ensure captcha_key and captcha_value are provided
        if captcha_required:
            if not captchaKey or not captchaValue:
                raise ValueError(
                    "Captcha key and value are required when `CAPTCHA_REQUIRED` is True."
                )
        else:
            # If CAPTCHA_REQUIRED is False, ensure captcha_key and captcha_value are NOT provided
            if captchaKey or captchaValue:
                raise ValueError(
                    "Captcha key and value should not be provided when `CAPTCHA_REQUIRED` is False."
                )

        return values


class GenericForgotPasswordPayload(BaseModel, PydanticConfigV1):
    email: EmailStr
    captcha_key: Optional[str] = None
    captcha_value: Optional[str] = None

    @model_validator(mode="before")
    def validate_captcha(cls, values):
        captcha_required = getattr(settings, "CAPTCHA_REQUIRED", False)
        captchaKey = values.get("captcha_key")
        captchaValue = values.get("captcha_value")

        # If CAPTCHA_REQUIRED is True, ensure captcha_key and captcha_value are provided
        if captcha_required:
            if not captchaKey or not captchaValue:
                raise ValueError(
                    "Captcha key and value are required when `CAPTCHA_REQUIRED` is True."
                )
        else:
            # If CAPTCHA_REQUIRED is False, ensure captcha_key and captcha_value are NOT provided
            if captchaKey or captchaValue:
                raise ValueError(
                    "Captcha key and value should not be provided when `CAPTCHA_REQUIRED` is False."
                )

        return values


class GenericNewPasswordPayload(BaseModel, PydanticConfigV1):
    password: SecretStr
    password1: SecretStr
