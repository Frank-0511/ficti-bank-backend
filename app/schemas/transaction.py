# Contenido de app/schemas/transaction.py

from typing import Optional
from sqlmodel import SQLModel, Field 

class DepositoRequest(SQLModel):
    Cuenta: str = Field(..., max_length=10)
    Monto: float = Field(..., gt=0)
    Moneda: str = Field(..., max_length=3)
    Autorizacion: Optional[str] = Field(default=None, max_length=50)

class RetiroRequest(SQLModel):
    Cuenta: str = Field(..., max_length=10)
    Monto: float = Field(..., gt=0)

# Opcional: Si quieres un DTO específico para el resultado de la transacción
# Esto no es el APIResponse final, sino el 'result' que va dentro del APIResponse.
class TransaccionDetailsDTO(SQLModel):
    NroTransaccion: str
    FechaHora: str
    TipoCuenta: str
    NuevoSaldoDisponible: float
    NuevoSaldoEmbargado: float