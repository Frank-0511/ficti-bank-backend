from sqlmodel import SQLModel, Field
from typing import Optional
from decimal import Decimal

class EmbargoCreate(SQLModel):
    """
    Schema para los datos que se envían en el BODY
    de la petición POST para registrar un nuevo embargo.
    """
    NroCta: str = Field(..., max_length=20, description="Número de cuenta a embargar")
    MontoEmbargado: Decimal = Field(..., gt=0, description="Monto total solicitado")
    TipoEmbargo: str = Field(..., max_length=1, description="Tipo de embargo (ej: J, C)")
    Observaciones: Optional[str] = Field(default=None, description="Expediente, juzgado, etc.")
    