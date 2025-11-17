# app/schemas/movimiento.py

from sqlmodel import SQLModel
from decimal import Decimal
from datetime import date
from typing import Optional


class MovimientoDelDia(SQLModel):
    """
    Schema para los movimientos del día devueltos por el SP.
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
