# app/schemas/movimiento.py

from sqlmodel import SQLModel
from decimal import Decimal
from datetime import date


class MovimientoDelDia(SQLModel):
    """
    Schema para los movimientos devueltos por el stored procedure
    (últimos 20 o movimientos del día).
    """
    Fech_Ope: date
    NroCta: str
    NroOperNumber: int
    Usuario: str
    nombres: str
    TipoCuenta: str
    TipoMovimiento: str
    Monto: Decimal
    EstadoMovimiento: str
