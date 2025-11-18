# app/api/v1/endpoints/movimientos.py

from fastapi import APIRouter, HTTPException, status, Depends, Query
import traceback
from typing import List

# Importaciones internas
from app.api.v1.deps import SessionDep
from app.schemas.util import APIResponse
from app.schemas.movimientos import MovimientoDelDia
from app.services import movimientos_service


router = APIRouter()


# ============================================================
#   1. Movimientos del día (SP existente)
# ============================================================
@router.get(
    "/getMovimientosDelDia",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista los movimientos del día (Admin ve todo, Usuario ve lo suyo)."
)
def listar_movimientos_del_dia(
    *,
    session: SessionDep,
    Cod_usu: str = Query(..., description="Código del usuario que consulta."),
    rol: str = Query(..., max_length=1, description="Rol del usuario (A=Admin, C=Cliente)."),
):
    """
    Obtiene los movimientos registrados en la fecha actual.
    Rol A: Admin → ve todo
    Rol C: Cliente → solo ve sus propios movimientos
    """
    try:
        lista = movimientos_service.listar_movimientos_del_dia_sp(
            session=session,
            cod_usu=Cod_usu,
            rol=rol
        )

        return APIResponse(
            mensaje=f"Consulta exitosa. Se encontraron {len(lista)} movimientos.",
            codigo="LIST-OK",
            status_code=status.HTTP_200_OK,
            result=lista
        )

    except Exception as e:
        print("🔴 ERROR INESPERADO AL LISTAR MOVIMIENTOS DEL DÍA:", e)
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor.",
                codigo="SYS-500",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )


# ============================================================
#   2. Últimos 20 movimientos (NUEVO SP)
# ============================================================
@router.get(
    "/getLastMovimientosByCuenta",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtiene los últimos 20 movimientos de una cuenta bancaria."
)
def listar_ultimos_movimientos(
    *,
    session: SessionDep,
    nro_cuenta: str = Query(..., description="Número de cuenta. Ejemplo: CA-1088340")
):
    """
    Recupera los últimos 20 movimientos históricos de una cuenta,
    ordenados desde el más reciente al más antiguo.
    """
    try:
        lista = movimientos_service.listar_ultimos_movimientos_sp(
            session=session,
            nro_cuenta=nro_cuenta
        )

        if not lista:
            return APIResponse(
                mensaje="No se encontraron movimientos para esta cuenta.",
                codigo="MOV-404",
                status_code=status.HTTP_200_OK,
                result=[]
            )

        return APIResponse(
            mensaje=f"Consulta exitosa. Se encontraron {len(lista)} movimientos.",
            codigo="MOV-OK",
            status_code=status.HTTP_200_OK,
            result=lista
        )

    except Exception as e:
        print("🔴 ERROR INESPERADO AL LISTAR ÚLTIMOS MOVIMIENTOS:", e)
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor.",
                codigo="SYS-500",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )
