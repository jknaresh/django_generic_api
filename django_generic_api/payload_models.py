from enum import Enum
from typing import Optional, Any, List, Union

from pydantic import (
    BaseModel,
    field_validator,
    JsonValue,
    SecretStr,
    EmailStr,
    Field,
)

from .utils import PydanticConfigV1


class SavePayload(BaseModel, PydanticConfigV1):
    modelName: str
    id: Optional[Union[int, str]] = None
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


class GenericRegisterPayload(BaseModel, PydanticConfigV1):
    email: EmailStr
    password: SecretStr
    password1: SecretStr
    captcha_key: str
    captcha_value: str


class GenericForgotPasswordPayload(BaseModel, PydanticConfigV1):
    email: EmailStr
    captcha_key: str
    captcha_value: str


class GenericNewPasswordPayload(BaseModel, PydanticConfigV1):
    password: SecretStr
    password1: SecretStr
