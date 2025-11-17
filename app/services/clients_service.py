# app/services/cliente_service.py

from typing import List, Optional
from sqlmodel import Session
from sqlalchemy import text

# Importamos el schema de respuesta que definiste
from app.schemas.clients import ClientePublic


def listar_clientes_sp(session: Session, cod_usu_input: Optional[str]) -> List[ClientePublic]:
    """
    Obtiene una lista de clientes llamando al Stored Procedure sp_ListarClientes.

    Args:
        session: La sesión de la base de datos.
        cod_usu_input: El código de usuario para filtrar.
                         Si es None o '', se listan todos los clientes.

    Returns:
        Una lista de objetos ClientePublic.
    """
    
    # 1. Limpiamos el parámetro de entrada
    #    El SP espera NULL (no '') para "listar todos".
    p_cod_usu = cod_usu_input if cod_usu_input and cod_usu_input.strip() != '' else None
    
    # 2. Definimos la consulta al Stored Procedure
    query = text("CALL sp_ListarClientes(:p_CodUsu);")
    
    try:
        # 3. Ejecutamos la consulta
        results = session.execute(query, {"p_CodUsu": p_cod_usu}).mappings().all()
        
        # 4. Mapeamos los resultados al modelo Pydantic/SQLModel
        #    Esto valida que los datos de la BD coincidan con el schema
        lista_clientes_dto = [ClientePublic.model_validate(row) for row in results]
        
        return lista_clientes_dto

    except Exception as e:
        # 5. Manejo de errores
        print(f"🔴 Error al ejecutar sp_ListarClientes: {e}")
        session.rollback()
        # Es buena idea relanzar el error para que el endpoint lo maneje
        raise e
