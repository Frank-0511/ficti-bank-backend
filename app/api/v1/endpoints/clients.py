# app/api/v1/endpoints/clientes.py

from fastapi import APIRouter, HTTPException, status, Query
import traceback  
from typing import Optional, List

# --- Importaciones de dependencias ---
from app.api.v1.deps import SessionDep  
# (Asumo que tu schema APIResponse está aquí)
from app.schemas.util import APIResponse 
# (Asumo que tu schema ClientePublic está aquí)
from app.schemas.clients import ClientePublic
# (Importamos el servicio de cliente que creamos)
from app.services import clients_service 

router = APIRouter()


@router.get(
    "/getClientes",
    response_model=APIResponse,  # Usa el modelo de respuesta estandarizado
    status_code=status.HTTP_200_OK,
    summary="Lista los clientes por usuario o todos (Administrador)."
)
def listar_clientes(
    *,
    session: SessionDep,
    # Recibe el 'cod_usu' como parámetro de consulta (query parameter)
    cod_usu: Optional[str]=Query(
        default=None,
        max_length=10,
        description="Código del usuario a filtrar. Si es nulo o vacío, lista todos los clientes."
    )
):
    """
    Recupera los clientes. Puede filtrar por código de usuario.
    """
    try:
        # 1. Llama al servicio
        #    La lógica de limpiar '' a None ya está en el servicio.
        lista_clientes_dto: List[ClientePublic] = clients_service.listar_clientes_sp(
            session=session,
            cod_usu_input=cod_usu
        )
        
        # 2. Verifica si la lista está vacía (si se filtró y no se encontró)
        if not lista_clientes_dto and cod_usu is not None and cod_usu.strip() != '':
            return APIResponse(
                mensaje=f"No se encontraron clientes para el usuario: {cod_usu}.",
                codigo="LIST-OK-EMPTY",
                status_code=status.HTTP_200_OK,
                result=[]
            )

        # 3. Respuesta de Éxito (Status HTTP 200)
        return APIResponse(
            mensaje=f"Consulta exitosa. Se encontraron {len(lista_clientes_dto)} clientes.",
            codigo="LIST-OK",
            status_code=status.HTTP_200_OK,
            result=lista_clientes_dto  # <-- Aquí va la lista de clientes
        )
    
    except Exception as e:
        # 4. Manejo de Errores Internos
        print("🔴 OCURRIÓ UN ERROR INESPERADO AL LISTAR CLIENTES:", e)
        traceback.print_exc()
        
        # Devolver un error HTTP 500 con el formato estandarizado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor durante la consulta.",
                codigo="SYS-500",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )
