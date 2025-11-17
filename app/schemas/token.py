from typing import Optional
from pydantic import BaseModel

class UserLoginDTO(BaseModel):
    CodUsu: str
    Usuario: str
    Rol: str
    Estado: str
    email: str
    codcliente: str
    nombre_completo: str

class Token(BaseModel):
    access_token: str
    token_type: str
    result: Optional[list[UserLoginDTO]]


class TokenData(BaseModel):
    username: Optional[str] = None
    
