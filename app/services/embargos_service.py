# app/services/embargo_service.py

from typing import Dict, Any, Optional
from sqlmodel import Session
from sqlalchemy import text
from decimal import Decimal

# Importamos el schema de request que acabamos de definir
from app.schemas.embargos import EmbargoCreate 


def registrar_embargo_sp(
    session: Session,
    datos_embargo: EmbargoCreate,
) -> Dict[str, Any]:
    """
    Registra un nuevo embargo llamando al SP sp_RegistrarEmbargo.
    Devuelve un diccionario con el ID del embargo y el mensaje del SP.
    
    Lanza un ValueError si el SP devuelve un mensaje de error de negocio.
    """
    
    try:
        # 1. Definimos la consulta al Stored Procedure
        #    Usamos variables de sesión de MySQL para capturar los OUT
        query = text("""
            CALL sp_RegistrarEmbargo(
                :p_NroCta,
                :p_MontoEmbargado,
                :p_TipoEmbargo,
                :p_Observaciones,
                :p_UsrRegistro,
                @p_Out_IdEmbargo,
                @p_Out_Message
            );
        """)

        # 2. Definimos los parámetros de entrada (IN)
        params = {
            "p_NroCta": datos_embargo.NroCta,
            "p_MontoEmbargado": datos_embargo.MontoEmbargado,
            "p_TipoEmbargo": datos_embargo.TipoEmbargo,
            "p_Observaciones": datos_embargo.Observaciones,
            "p_UsrRegistro": datos_embargo.CodUsu  # Este viene del token (ver endpoint)
        }

        # 3. Ejecutamos la llamada al SP
        #    No usamos .mappings() aquí porque el CALL no devuelve un SELECT
        session.execute(query, params)

        # 4. ¡Clave! Ejecutamos una segunda consulta para leer las variables OUT
        out_params_query = text("SELECT @p_Out_IdEmbargo AS IdEmbargo, @p_Out_Message AS MensajeSP;")
        
        # Usamos .mappings().first() para obtener un dict
        result = session.execute(out_params_query).mappings().first()
        
        # Convertimos el resultado (RowMapping) a un dict estándar
        resultado_sp = dict(result)

        # 5. Verificamos si el SP devolvió un error de negocio
        #    (Ej: "Error: La cuenta no existe.")
        if "Error:" in (resultado_sp.get("MensajeSP") or ""):
            # Lanzamos un ValueError, que el endpoint convertirá en HTTP 400
            raise ValueError(resultado_sp.get("MensajeSP"))

        # 6. Si todo fue bien, devolvemos el dict con los resultados
        return resultado_sp

    except ValueError as ve:
        # Relanzamos el error de negocio (ValueError) para que el endpoint lo capture
        raise ve
    
    except Exception as e:
        # 5. Manejo de errores (el SP ya hizo ROLLBACK)
        print(f"🔴 Error al ejecutar sp_RegistrarEmbargo: {e}")
        # Relanzamos la excepción para que el endpoint la capture como HTTP 500
        raise e
