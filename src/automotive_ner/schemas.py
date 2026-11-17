"""Validated API input and output contracts."""

from pydantic import BaseModel, ConfigDict, Field


class ExtractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=10000)


class Entity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_id: str
    canonical_name: str
    text: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)


class ExtractionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    redacted_text: str
    entities: list[Entity]
