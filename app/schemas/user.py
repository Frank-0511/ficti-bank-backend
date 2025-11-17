from typing import Optional
from sqlmodel import SQLModel, Field


class UsuarioBase(SQLModel):
    Usuario: str
    Rol: str  # Ej: 'A' o 'E'


class UsuarioCreate(UsuarioBase):
    CodUsu: str  # El código se genera/asigna al crear
    Password: str = Field(..., min_length=1)


class UsuarioPublic(UsuarioBase):
    CodUsu: str
    Usuario: str
    Rol: str
    Estado: str

class UserFromDB(SQLModel):
    """
    Schema para los datos del usuario tal como se reciben desde la base de datos,
    incluyendo la contraseña hasheada para la verificación.
    """
    CodUsu: str
    Usuario: str
    HashedPassword: str
    Rol: str
    Estado: str
    email: str
    codcliente: str
    nombre_completo: str
    