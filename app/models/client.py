from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import date

class Cliente(SQLModel, table=True):
    __tablename__ = "t_cliente"   # ✔ tabla real en BD

    CodCliente: str = Field(primary_key=True, max_length=10)
    Apellidos: Optional[str] = Field(default=None, max_length=100)
    Nombres: Optional[str] = Field(default=None, max_length=100)
    DNI: Optional[str] = Field(default=None, max_length=8)
    Fecha_Nac: Optional[date] = None
    Direccion: Optional[str] = Field(default=None, max_length=100)
    CodUbigeo: Optional[str] = Field(
        default=None, 
        max_length=6, 
        foreign_key="t_ubigeo.CodUbigeo"      # ✔ corregido
    )
    Telefonos: Optional[str] = Field(default=None, max_length=9)
    Movil: Optional[str] = Field(default=None, max_length=11)
    e_mail: Optional[str] = Field(default=None, max_length=50)
    Fech_reg: Optional[date] = None
    Estado: Optional[str] = Field(
        default=None, 
        max_length=1, 
        foreign_key="t_estado.Estado"         # ✔ corregido
    )
    
    CodUsu: Optional[str] = Field(
        default=None, 
        foreign_key="t_usuario.CodUsu"        # ✔ corregido
    )

    # ✔ Relaciones eliminadas
