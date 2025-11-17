from pydantic import BaseModel

class TransferenciaRequest(BaseModel):
    cuenta_origen: str
    cuenta_destino: str
    monto: float
    descripcion: str | None = None
    cod_usuario: str   # <-- NECESARIO PARA registrar en t_movimientos


class TransferenciaResponse(BaseModel):
    mensaje: str
    saldo_origen: float
    saldo_destino: float
