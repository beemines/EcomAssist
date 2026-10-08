from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RequestType(StrEnum):
    REFUND = "refund"
    RETURN_REFUND = "return_refund"
    EXCHANGE = "exchange"
    REPAIR = "repair"
    LOGISTICS = "logistics"
    OTHER = "other"
    UNKNOWN = "unknown"


class ExtractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=20000)

    # 拒绝只有空白的待抽取文本。
    @field_validator("text")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class AfterSalesResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str | None
    request_type: RequestType
    expected_solution: str | None

    # 允许缺失信息使用 null，拒绝用空白字符串替代有效字段。
    @field_validator("order_id", "expected_solution")
    @classmethod
    def nullable_string_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must be a nonblank string or null")
        return value
