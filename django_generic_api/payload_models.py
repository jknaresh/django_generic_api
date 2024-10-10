from enum import Enum
from typing import Optional, Any, List, Union

from pydantic import (
    BaseModel,
    field_validator,
    JsonValue,
    ConfigDict,
    SecretStr,
    EmailStr,
)


class SavePayload(BaseModel, str_strip_whitespace=True):
    modelName: str
    id: Optional[Union[int, str]] = None
    saveInput: JsonValue

    # does not allow extra attributes
    model_config = ConfigDict(extra="forbid")


class OperatorByEnum(str, Enum):
    EQ = "eq"
    IN = "in"
    NOT = "not"


class OperationByEnum(str, Enum):
    OR = "or"
    AND = "and"


class FetchFilter(BaseModel):
    operator: OperatorByEnum
    name: str
    value: List[Any]
    operation: Optional[OperationByEnum] = OperationByEnum.AND

    # model_config = ConfigDict(extra="forbid")  # does not allow extra attributes
    class Config:
        # Set configuration options here
        str_strip_whitespace = True
        smart_union = True
        extra = "forbid"


class OrderByEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class FetchSort(BaseModel, str_strip_whitespace=True):
    field: str
    order_by: OrderByEnum


class FetchPayload(BaseModel, str_strip_whitespace=True):
    modelName: str
    fields: List[str]
    filters: Optional[List[FetchFilter]] = None
    pageNumber: Optional[int] = None
    pageSize: Optional[int] = None
    sort: Optional[FetchSort] = None
    distinct: Optional[bool] = None

    model_config = ConfigDict(
        extra="forbid"
    )  # does not allow extra attributes

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


class GenericLoginPayload(BaseModel, str_strip_whitespace=True):
    email: str
    password: SecretStr

    model_config = ConfigDict(
        extra="forbid"
    )  # does not allow extra attributes


class GenericRegisterPayload(BaseModel, str_strip_whitespace=True):
    email: EmailStr
    password: SecretStr
    password1: SecretStr

    model_config = ConfigDict(
        extra="forbid"
    )  # does not allow extra attributes
