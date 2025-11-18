# app/services/account_service.py

from typing import Dict, Any, Optional, List
from sqlmodel import Session
from sqlalchemy import text, Row
from app.schemas.account import CuentaCreationData, CuentaDetailsDTO, CuentaEstadoUpdate
# 🛑 NUEVAS IMPORTACIONES REQUERIDAS para Depósito y Retiro
from app.schemas.transaction import DepositoRequest, RetiroRequest


def insertar_nueva_cuenta_sp(session: Session, datos: CuentaCreationData) -> Dict[str, Any]:
    """
    Llama al stored procedure sp_InsertarNuevaCuenta y maneja los parámetros OUT.
    """
    try:
        query = text("""
            CALL sp_InsertarNuevaCuenta(
                :p_TipoCta, :p_Moneda, :p_Saldoni, :p_CodUsu,
                @p_Out_NroCta, @p_Out_Message
            );
        """)
        
        # 1. Ejecutamos la llamada al SP
        session.execute(query, {
            "p_TipoCta": datos.TipoCta,
            "p_Moneda": datos.Moneda,
            "p_Saldoni": datos.SaldoInicial,
            "p_CodUsu": datos.CodUsu
        })
        
        # 2. Obtenemos los valores de las variables de salida
        out_params_result: Optional[Row] = session.execute(
            text("SELECT @p_Out_NroCta AS NroCta, @p_Out_Message AS Mensaje;")
        ).first()

        # 3. Validación de la respuesta de la base de datos
        if out_params_result is None:
            raise Exception("La base de datos no devolvió el resultado del OUT SELECT.")
            
        try:
            nro_cta_generada = out_params_result.NroCta
            output_message = out_params_result.Mensaje
        except AttributeError:
            # Fallback por si el acceso por alias falla
            nro_cta_generada = out_params_result[0]
            output_message = out_params_result[1]

        # 4. VERIFICACIÓN DE ÉXITO/ERROR (La parte modificada)
        
        if not output_message.lower().startswith('éxito'): 
            
            # Si el SP devolvió cualquier cosa que no sea un éxito, lo tratamos como error
            raise ValueError(output_message)

        # 5. Si pasa la verificación (el mensaje comienza con "Éxito:"), devolvemos los datos
        return {
            "NroCta": nro_cta_generada,
            "MensajeSP": output_message
        }

    except Exception as e:
        session.rollback()
        raise e


def listar_cuentas_sp(session: Session, cod_usu_input: Optional[str]) -> List[CuentaDetailsDTO]:
    
    # ... (lógica para limpiar p_cod_usu)
    p_cod_usu = cod_usu_input if cod_usu_input and cod_usu_input != '' else None
    
    query = text("CALL sp_ListarCuentas(:p_CodUsu);")
    
    try:
        # 1. Ejecutamos la llamada
        results = session.execute(query, {"p_CodUsu": p_cod_usu}).mappings().all()
        
        # 2. Mapeamos cada diccionario/fila (Row) al DTO
        lista_cuentas_dto = [CuentaDetailsDTO.model_validate(row) for row in results]
        
        return lista_cuentas_dto

    except Exception as e:
        session.rollback()
        raise e


def actualizar_estado_cuenta_sp(session: Session, datos: CuentaEstadoUpdate) -> Dict[str, Any]:
    """
    Llama al stored procedure sp_ActualizarEstadoCuenta.
    """
    try:
        # La llamada al SP (solo tiene un parámetro OUT: @p_Out_Message)
        query = text("""
            CALL sp_ActualizarEstadoCuenta(
                :p_NroCta, :p_NuevoEstado, :p_CodUsuModifica,
                @p_Out_Message
            );
        """)
        
        # 1. Ejecutamos la llamada
        session.execute(query, {
            "p_NroCta": datos.nro_cta,
            "p_NuevoEstado": datos.nuevo_estado,
            "p_CodUsuModifica": datos.cod_usu_modifica
        })
        
        # 2. Obtenemos el valor del parámetro de salida
        out_params_result: Optional[Row] = session.execute(
            text("SELECT @p_Out_Message AS Mensaje;")
        ).first()

        # 3. Validación de la respuesta
        if out_params_result is None:
            raise Exception("La base de datos no devolvió el mensaje de estado.")
            
        # Accedemos al mensaje por el alias
        output_message = out_params_result.Mensaje

        # 4. Verificación de Éxito/Error (Revisa si NO comienza con "Éxito:")
        if not output_message.lower().startswith('éxito'): 
            # Si el SP devolvió cualquier mensaje que no sea Éxito (incluyendo "Error:"), lanzamos un error
            raise ValueError(output_message)

        # 5. Éxito
        return {
            "NroCta": datos.nro_cta,
            "MensajeSP": output_message
        }

    except Exception as e:
        session.rollback()
        raise e

# ===============================================================
# FUNCIONES DE SIMULACIÓN (Depósito y Retiro)
# ===============================================================

def insertar_deposito_sp(session: Session, datos: DepositoRequest) -> Dict[str, Any]:
    """
    SIMULACIÓN: Registra el depósito aplicando la lógica de embargo/desembargo 
    en memoria para permitir la prueba del endpoint. (NO HACE LLAMADAS A DB)
    """
    
    # Simulación de verificación de cuenta
    if datos.Cuenta == "CUENTA_INVALIDA":
        raise ValueError("Error: Cuenta bancaria no encontrada.")
        
    # --- LÓGICA DE SIMULACIÓN DE EMBARGO/DESEMBARGO ---
    
    tiene_embargo = True if datos.Cuenta == "CUE0002" else False
    
    if tiene_embargo:
        # 🧪 Caso de Prueba: CUE0002 (El depósito va al embargo)
        mensaje_final = f"Éxito: Depósito de {datos.Monto} aplicado a SALDO EMBARGADO."
        nuevo_saldo_disponible = 100.00
        nuevo_saldo_embargado = 2500.00 + datos.Monto
    else:
        # 🧪 Caso de Prueba: CUE0001 (El depósito va al disponible)
        mensaje_final = f"Éxito: Depósito de {datos.Monto} aplicado a SALDO DISPONIBLE."
        nuevo_saldo_disponible = 1000.00 + datos.Monto
        nuevo_saldo_embargado = 0.00 
        
    # --- Devolver el resultado de la simulación ---
    return {
        "NroTransaccion": "TXD" + str(hash(datos.Cuenta))[:6],
        "MensajeSP": mensaje_final,
        "NuevoSaldoDisponible": nuevo_saldo_disponible,
        "NuevoSaldoEmbargado": nuevo_saldo_embargado
    }

def insertar_retiro_sp(session: Session, datos: RetiroRequest) -> Dict[str, Any]:
    """
    SIMULACIÓN: Llama al SP para el retiro aplicando la lógica de Embargo, Saldo, Sobregiro
    en memoria para permitir la prueba del endpoint. (NO HACE LLAMADAS A DB)
    """
    
    # 1. SIMULACIÓN DE CASOS DE FALLO CRÍTICOS (EMBARGO/PLAZO/SALDO)
    if datos.Cuenta == "CUE9999": # Prueba de Embargo Total
        raise ValueError("Error: Retiro no autorizado. Cuenta con embargo total activo.")
    
    if datos.Cuenta == "CUE8888" and datos.Monto > 500: # Prueba de Saldo Insuficiente
        raise ValueError("Error: El monto a retirar excede el saldo disponible (S/500).")
        
    if datos.Cuenta == "CUE7777": # Prueba de Cuenta a Plazo Fijo
        raise ValueError("Error: Retiro no permitido. Cuenta a plazo fijo no ha cumplido el término.")
        
    # --- SIMULACIÓN DE ÉXITO (Si no falló en los casos anteriores) ---
    
    # 2. Devolver el resultado de la simulación
    return {
        "MensajeSP": "Éxito: Retiro procesado correctamente.",
        "NroTransaccion": "TXR" + str(hash(datos.Cuenta))[:6],
        "NuevoSaldoDisponible": 10000.00 - datos.Monto, 
        "NuevoSaldoEmbargado": 0.00
    }