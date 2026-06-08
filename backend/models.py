from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, Field, field_validator, model_validator


FlagStatus = Literal["Aprovado", "Revisão Manual", "Inconsistente"]


class LocationPayload(BaseModel):
    latitude: float
    longitude: float
    accuracy: float | None = None


class RegistroIn(BaseModel):
    id: str
    nome_propriedade: str = Field(
        validation_alias=AliasChoices("nome_propriedade", "propertyName")
    )
    observacao: str = Field(
        default="",
        validation_alias=AliasChoices("observacao", "observation"),
    )
    latitude: float | None = None
    longitude: float | None = None
    area_hectares: float | None = None
    base64_da_foto: str | None = Field(
        default=None,
        validation_alias=AliasChoices("base64_da_foto", "photoDataUrl"),
    )
    data_coleta: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        validation_alias=AliasChoices("data_coleta", "createdAt"),
    )
    location: LocationPayload | None = None

    @field_validator("nome_propriedade")
    @classmethod
    def validate_nome(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("nome_propriedade é obrigatório")
        return value

    @model_validator(mode="after")
    def normalize_location(self) -> "RegistroIn":
        if self.location:
            self.latitude = self.location.latitude
            self.longitude = self.location.longitude
        return self


class SyncPayload(BaseModel):
    records: list[RegistroIn] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def accept_single_or_batch(cls, data: Any) -> Any:
        if isinstance(data, list):
            return {"records": data}
        if isinstance(data, dict) and "records" not in data:
            return {"records": [data]}
        return data


class RegistroOut(BaseModel):
    id: str
    nome_propriedade: str
    propriedade: str
    observacao: str
    latitude: float | None
    longitude: float | None
    coordenadas: str
    area_hectares: float | None
    data_coleta: datetime
    confidence_score: int
    score: int
    flag_status: FlagStatus
    status_ia: FlagStatus
    justificativa_ia: str | None = None
    mcp_tool_result: dict[str, Any] | None = None
    criado_em: datetime


class SyncResponse(BaseModel):
    ok: bool
    recebidos: int
    registros: list[RegistroOut]
