from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import date
from decimal import Decimal


class Cuenta(SQLModel, table=True):
    __tablename__ = "t_cuentas"
    
    NroCta: str = Field(primary_key=True, max_length=20)
    TipoCta: Optional[str] = Field(default=None, max_length=2, foreign_key="t_tipocuentas.TipoCta")
    CodCliente: Optional[str] = Field(default=None, max_length=10, foreign_key="t_cliente.CodCliente")

    Moneda: Optional[str] = Field(default=None, max_length=2)
    Fech_Apert: Optional[date] = None
    Fech_Cierre: Optional[date] = None
    Fech_Bloq: Optional[date] = None
    Fech_Ult_M: Optional[date] = None

    Saldoni: Optional[Decimal] = Field(default=0.0, max_digits=10, decimal_places=2)
    SaldAct: Optional[Decimal] = Field(default=0.0, max_digits=10, decimal_places=2)
    SaldoPro: Optional[Decimal] = Field(default=0.0, max_digits=10, decimal_places=2)

    CodUsu: Optional[str] = Field(default=None, foreign_key="t_usuario.CodUsu")
    Estado: Optional[str] = Field(default=None, max_length=1, foreign_key="t_estado.Estado")


class Movimiento(SQLModel, table=True):
    __tablename__ = "t_movimientos"

    TipoCta: str = Field(primary_key=True, max_length=2, foreign_key="t_tipocuentas.TipoCta")
    NroCta: str = Field(primary_key=True, max_length=20, foreign_key="t_cuentas.NroCta")
    NroOperNumber: int = Field(primary_key=True)

    Fech_Ope: Optional[date] = None
    CodUsu: Optional[str] = Field(default=None, max_length=10, foreign_key="t_usuario.CodUsu")
    TipoMov: Optional[str] = Field(default=None, max_length=2, foreign_key="t_tipomovi.TipoMov")
    MonOpe: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    Estado: Optional[str] = Field(default=None, max_length=1, foreign_key="t_estado.Estado")
