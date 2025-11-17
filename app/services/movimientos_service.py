# app/services/movimiento_service.py

from typing import List, Optional
from sqlmodel import Session
from sqlalchemy import text

# Importamos el schema de respuesta
from app.schemas.movimientos import MovimientoDelDia


def listar_movimientos_del_dia_sp(
    session: Session,
    cod_usu: str,
    rol: str
) -> List[MovimientoDelDia]:
    """
    Obtiene los movimientos del día llamando al SP sp_ListarMovimientosDelDia,
    aplicando la lógica de seguridad (Admin ve todo, usuario ve lo suyo).
    """
    
    # 1. Definimos la consulta al SP
    query = text("CALL sp_ListarMovimientosDelDia(:p_CodUsu, :p_Rol);")
    
    # 2. Definimos los parámetros
    params = {"p_CodUsu": cod_usu, "p_Rol": rol}
    
    try:
        # 3. Ejecutamos la consulta
        results = session.execute(query, params).mappings().all()
        
        # 4. Mapeamos los resultados al DTO (Schema)
        lista_movimientos_dto = [MovimientoDelDia.model_validate(row) for row in results]
        
        return lista_movimientos_dto

    except Exception as e:
        print(f"🔴 Error al ejecutar sp_ListarMovimientosDelDia: {e}")
        session.rollback()
        raise e
