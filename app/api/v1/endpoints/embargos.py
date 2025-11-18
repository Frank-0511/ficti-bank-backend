# app/api/v1/endpoints/embargos.py

from fastapi import APIRouter, HTTPException, status, Depends
import traceback  
from typing import Dict, Any

# --- Importaciones de dependencias ---
from app.api.v1.deps import SessionDep
# Asumo que tienes una dependencia para obtener el usuario del token
from app.api.v1.deps import get_current_user 
from app.schemas.util import APIResponse 
# Importamos el schema de REQUEST que creamos
from app.schemas.embargos import EmbargoCreate
# Importamos el schema del Usuario (para obtener el CodUsu del token)
from app.schemas.user import UserFromDB
# Importamos el servicio de embargo
from app.services import embargos_service 

router = APIRouter()


@router.post(
    "/registrarEmbargo",
    response_model=APIResponse,  # Usa el modelo de respuesta estandarizado
    status_code=status.HTTP_201_CREATED,  # 201 CREATED es el estándar para POST exitoso
    summary="Registra un nuevo embargo (total o parcial) en una cuenta."
)
def registrar_embargo(
    *,
    session: SessionDep,
    datos_embargo: EmbargoCreate,  # Recibe el cuerpo JSON
):
    """
    Registra un nuevo embargo.
    El SP maneja la lógica de si es total o parcial basado en el saldo.
    El usuario que registra se obtiene del token de autenticación.
    """
    try:
        # 1. Llamada al servicio
        #    Pasamos los datos del body Y el CodUsu del token
        resultado_sp: Dict[str, Any] = embargos_service.registrar_embargo_sp(
            session=session,
            datos_embargo=datos_embargo,
        )
        
        # 2. Respuesta de Éxito (Status HTTP 201 CREATED)
        return APIResponse(
            mensaje=resultado_sp["MensajeSP"],
            codigo=str(resultado_sp["IdEmbargo"]),  # Devolvemos el ID del embargo
            status_code=status.HTTP_201_CREATED,
            result=[resultado_sp]  # Opcional: devolver todo el dict
        )
    
    except ValueError as ve:
        # 3. Manejo de Errores de Negocio (del SP)
        error_message = str(ve)
        
        # Error 404 si la cuenta no existe, 400 para otros errores de validación
        error_code = status.HTTP_404_NOT_FOUND if "cuenta no existe" in error_message else status.HTTP_400_BAD_REQUEST
        
        raise HTTPException(
            status_code=error_code,
            detail=APIResponse(
                mensaje=error_message,
                codigo="EMBARGO-ERR",
                status_code=error_code
            ).model_dump()
        )
    
    except Exception as e:
        # 4. Manejo de Errores Internos (500)
        print("🔴 ERROR INESPERADO AL REGISTRAR EMBARGO:", e)
        traceback.print_exc()  
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor.",
                codigo="SYS-500",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )
