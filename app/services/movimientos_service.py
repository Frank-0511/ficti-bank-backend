# app/services/movimiento_service.py

from typing import List
from sqlmodel import Session
from sqlalchemy import text

from app.schemas.movimientos import MovimientoDelDia



# ============================================================
#   1. Movimientos del día (SP ya existente)
# ============================================================
def listar_movimientos_del_dia_sp(
    session: Session,
    cod_usu: str,
    rol: str
) -> List[MovimientoDelDia]:
    """
    Obtiene los movimientos del día llamando al SP sp_ListarMovimientosDelDia,
    aplicando la lógica de seguridad (Admin ve todo, usuario ve lo suyo).
    """

    query = text("CALL sp_ListarMovimientosDelDia(:p_CodUsu, :p_Rol);")
    params = {"p_CodUsu": cod_usu, "p_Rol": rol}

    try:
        results = session.execute(query, params).mappings().all()
        return [MovimientoDelDia.model_validate(row) for row in results]

    except Exception as e:
        print(f"🔴 Error al ejecutar sp_ListarMovimientosDelDia: {e}")
        session.rollback()
        raise e


# ============================================================
#   2. ÚLTIMOS 20 MOVIMIENTOS (NUEVO SP: sp_GetLastMovements)
# ============================================================
def listar_ultimos_movimientos_sp(
    session: Session,
    nro_cuenta: str
) -> List[MovimientoDelDia]:
    """
    Obtiene los últimos 20 movimientos de una cuenta 
    llamando al SP sp_GetLastMovements(p_NroCta).
    """

    query = text("CALL sp_GetLastMovements(:p_NroCta);")
    params = {"p_NroCta": nro_cuenta}

    try:
        results = session.execute(query, params).mappings().all()
        return [MovimientoDelDia.model_validate(row) for row in results]

    except Exception as e:
        print(f"🔴 Error al ejecutar sp_GetLastMovements: {e}")
        session.rollback()
        raise e
