# app/api/v1/endpoints/movimientos.py

from fastapi import APIRouter, HTTPException, status, Depends
import traceback  
from typing import List

# --- Importaciones de dependencias ---
from app.api.v1.deps import SessionDep, get_current_user
from app.schemas.util import APIResponse 
from app.schemas.user import UserFromDB  # Para obtener el usuario del token
from app.schemas.movimientos import MovimientoDelDia  # Nuestro nuevo schema
from app.services import movimientos_service  # Nuestro nuevo servicio
from fastapi.param_functions import Query

router = APIRouter()


@router.get(
    "/getMovimientosDelDia",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista los movimientos del día (Admin ve todo, Usuario ve lo suyo)."
)
def listar_movimientos_del_dia(
    *,
    session: SessionDep,
    # current_user: UserFromDB=Depends(get_current_user)  # Protegido
    Cod_usu: str = Query(..., description="Código del usuario que consulta."),
    rol: str = Query(..., max_length=1, description="Rol del usuario (ej: 'A', 'C').")
):
    """
    Recupera los movimientos bancarios registrados en el día actual (CURDATE()).
    - Si el usuario es Admin (Rol='A'), verá todos los movimientos.
    - Si no es Admin, solo verá los movimientos registrados por él mismo.
    """
    try:
        # 1. Llama al servicio pasando los datos del token
        lista_movimientos: List[MovimientoDelDia] = movimientos_service.listar_movimientos_del_dia_sp(
            session=session,
            cod_usu=Cod_usu,
            rol=rol
        )
        
        # 2. Respuesta de Éxito
        return APIResponse(
            mensaje=f"Consulta exitosa. Se encontraron {len(lista_movimientos)} movimientos.",
            codigo="LIST-OK",
            status_code=status.HTTP_200_OK,
            result=lista_movimientos  # <-- Aquí va la lista de movimientos
        )
    
    except Exception as e:
        # 3. Manejo de Errores Internos
        print("🔴 ERROR INESPERADO AL LISTAR MOVIMIENTOS:", e)
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor.",
                codigo="SYS-500",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )
