from typing import Optional
from sqlmodel import Field, SQLModel


class Estado(SQLModel, table=True):
    __tablename__ = "t_estado"
    Estado: str = Field(primary_key=True, max_length=1)
    Descripcion: Optional[str] = Field(default=None, max_length=20)
    CEstado: Optional[str] = Field(default=None, max_length=1)


class Ubigeo(SQLModel, table=True):
    __tablename__ = "t_ubigeo"
    CodUbigeo: str = Field(primary_key=True, max_length=6)
    Depart: Optional[str] = Field(default=None, max_length=50)
    Provin: Optional[str] = Field(default=None, max_length=50)
    Distrit: Optional[str] = Field(default=None, max_length=50)


class TipoCuenta(SQLModel, table=True):
    __tablename__ = "t_tipocuentas"   # ← nombre correcto según tu BD
    TipoCta: str = Field(primary_key=True, max_length=2)
    Descripcion: Optional[str] = Field(default=None, max_length=50)
    Estado: Optional[str] = Field(default=None, max_length=1, foreign_key="t_estado.Estado")


class TipoMovimiento(SQLModel, table=True):
    __tablename__ = "t_tipomovi"
    TipoMov: str = Field(primary_key=True, max_length=2)
    Descrip: Optional[str] = Field(default=None, max_length=100)
    Estado: Optional[str] = Field(default=None, max_length=1, foreign_key="t_estado.Estado")
