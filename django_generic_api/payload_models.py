from enum import Enum
from typing import Optional, Any, List, Union
from abc import ABC
from pydantic import (
    BaseModel,
    field_validator,
    JsonValue,
    ConfigDict,
    SecretStr,
    EmailStr,
)


class PayloadModelConfig(ABC):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Remove white spaces
        extra="forbid",  # Forbid extra fields
    )


class SavePayload(BaseModel, PayloadModelConfig):
    modelName: str
    id: Optional[Union[int, str]] = None
    saveInput: JsonValue


class OperatorByEnum(str, Enum):
    EQ = "eq"
    IN = "in"
    NOT = "not"
    GT = "gt"


class OperationByEnum(str, Enum):
    OR = "or"
    AND = "and"


class FetchFilter(BaseModel, PayloadModelConfig):
    operator: OperatorByEnum
    name: str
    value: List[Any]
    operation: Optional[OperationByEnum] = OperationByEnum.AND

    class Config:
        smart_union = True


class OrderByEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class FetchSort(BaseModel, PayloadModelConfig):
    field: str
    order_by: OrderByEnum


class FetchPayload(BaseModel, PayloadModelConfig):
    modelName: str
    fields: List[str]
    filters: Optional[List[FetchFilter]] = None
    pageNumber: Optional[int] = None
    pageSize: Optional[int] = None
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


class GenericLoginPayload(BaseModel, PayloadModelConfig):
    email: str
    password: SecretStr


class GenericRegisterPayload(BaseModel, PayloadModelConfig):
    email: EmailStr
    password: SecretStr
    password1: SecretStr
