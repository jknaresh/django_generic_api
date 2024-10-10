from enum import Enum
from typing import Optional, Any, List, Union

from pydantic import BaseModel, field_validator, JsonValue, ConfigDict


class SavePayload(BaseModel, str_strip_whitespace=True):
    modelName: str
    id: Optional[Union[int, str]] = None
    saveInput: JsonValue

    # does not allow extra attributes
    model_config = ConfigDict(extra="forbid")

    # Additional validations if needed
    @field_validator("modelName")
    def validate_model_name(cls, v):
        if not v:
            raise ValueError("modelName is required")
        return v

    # only allows str and int for id
    @field_validator("id")
    def validate_value_type(cls, v):
        if not isinstance(v, (int, str, type(None))):
            raise ValueError("id must be an integer or a string")
        return v


class OperatorByEnum(str, Enum):
    EQ = "eq"
    IN = "in"
    NOT = "not"


class OperationByEnum(str, Enum):
    OR = "or"
    AND = "and"


class FetchFilter(BaseModel, str_strip_whitespace=True):
    operator: OperatorByEnum
    name: str
    value: List[Any]
    operation: Optional[OperationByEnum] = OperationByEnum.AND

    model_config = ConfigDict(
        extra="forbid"
    )  # does not allow extra attributes


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
