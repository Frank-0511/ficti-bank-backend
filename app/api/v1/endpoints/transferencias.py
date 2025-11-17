from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.transferencias_schema import TransferenciaRequest, TransferenciaResponse
from app.services.transferencias_service import TransferenciaService

router = APIRouter(
    tags=["Transferencias"]
)

@router.post("/", response_model=TransferenciaResponse)
def realizar_transferencia(payload: TransferenciaRequest):
    try:
        resultado = TransferenciaService.realizar_transferencia(payload)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
