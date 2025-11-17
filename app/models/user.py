from typing import Optional
from sqlmodel import Field, SQLModel

class Usuario(SQLModel, table=True):
    __tablename__ = "t_usuario"   # ✔ coincide con tu BD real

    CodUsu: str = Field(primary_key=True, max_length=10)
    Usuario: Optional[str] = Field(default=None, max_length=100, unique=True, index=True)
    Rol: Optional[str] = Field(default=None, max_length=1)
    Estado: Optional[str] = Field(default=None, max_length=1, foreign_key="t_estado.Estado")
    HashedPassword: str = Field(max_length=255)

    # ✔ Relaciones eliminadas (NO necesarias y causaban errores)
