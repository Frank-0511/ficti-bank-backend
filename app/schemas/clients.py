from sqlmodel import SQLModel
from typing import Optional

class ClientePublic(SQLModel):
    """
    Schema para la información pública de un cliente,
    tal como la devuelve el SP sp_ListarClientes.
    """
    CodCliente: str
    nombres: Optional[str] = None
    tipo: Optional[str] = None
    documento: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None
    CodUsu: Optional[str] = None
    
class getClientePublic(SQLModel):
    CodUsu: str