# app/api/v1/endpoints/cuentas.py

from fastapi import APIRouter, HTTPException, status, Query
import traceback 
from typing import Optional, List


# Importaciones de dependencias (asume que existen)
from app.api.v1.deps import SessionDep 
from app.schemas.account import CuentaCreationData, CuentaDetailsDTO, CuentaEstadoUpdate 
from app.schemas.transaction import DepositoRequest, RetiroRequest, TransaccionDetailsDTO
from app.services import account_service 
from app.schemas.util import APIResponse 
router = APIRouter()                     

@router.post(
    "/deposito",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Realiza un depósito de dinero con validación de monto y embargo."
)
def depositar_dinero(
    *,
    session: SessionDep,
    datos_deposito: DepositoRequest
):
    try:
        limite = 2000.00
        
        # --- 1. Lógica CRÍTICA de Autorización (VERIFICADA) ---
        if datos_deposito.Monto > limite and datos_deposito.Moneda == "PEN":
            if not datos_deposito.Autorizacion:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail=APIResponse(
                        mensaje=f"Depósito de S/{datos_deposito.Monto} excede el límite. Se requiere autorización.",
                        codigo="AUTH-REQ",
                        status_code=status.HTTP_403_FORBIDDEN
                    ).model_dump()
                )
        
        # --- 2. LLAMADA AL SERVICIO CORREGIDA ---
        try:
            # CORRECCIÓN: Usar account_service.insertar_deposito_sp
            resultado_sp = account_service.insertar_deposito_sp( 
                session=session, datos=datos_deposito
            )
        except ValueError as ve:
            # Manejo de Errores de Negocio devueltos por el Servicio/SP
            error_message = str(ve)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=APIResponse(
                    mensaje=error_message,
                    codigo="DEP-400",
                    status_code=status.HTTP_400_BAD_REQUEST
                ).model_dump()
            )
            
        # 3. Respuesta de Éxito (Usando los datos REALES del SP)
        return APIResponse(
            mensaje=resultado_sp["MensajeSP"],
            codigo=resultado_sp["NroTransaccion"],
            status_code=status.HTTP_200_OK,
            result={
                "NuevoSaldoDisponible": resultado_sp["NuevoSaldoDisponible"],
                "NuevoSaldoEmbargado": resultado_sp["NuevoSaldoEmbargado"]
            }
        )
    
    except HTTPException as h_e:
        raise h_e 
        
    except Exception as e:
        import traceback; traceback.print_exc() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor durante el depósito.",
                codigo="SYS-500",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )

@router.post(
    "/retiro",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Realiza un retiro de dinero con validaciones de embargo, sobregiro y saldo."
)
def retirar_dinero(
    *,
    session: SessionDep,
    datos_retiro: RetiroRequest
):
    try:
        # 1. LLAMADA AL SERVICIO CORREGIDA
        try:
            # CORRECCIÓN: Usar account_service.insertar_retiro_sp
            resultado_sp = account_service.insertar_retiro_sp( 
                session=session, datos=datos_retiro
            )
        except ValueError as ve:
            # --- CORRECCIÓN DE ERROR 500: Lanza HTTPException aquí ---
            error_message = str(ve)
            
            # Patrón para devolver 403 (Embargo/Plazo) o 400 (Saldo Insuficiente)
            if "embargo" in error_message.lower() or "plazo" in error_message.lower():
                error_code = status.HTTP_403_FORBIDDEN # Para errores que prohíben la acción
            else:
                error_code = status.HTTP_400_BAD_REQUEST # Para errores de datos o insuficiencia

            raise HTTPException(
                status_code=error_code,
                detail=APIResponse(
                    mensaje=error_message,
                    codigo="RET-FAIL",
                    status_code=error_code
                ).model_dump()
            )
            
        # 2. Respuesta de Éxito
        return APIResponse(
            mensaje=resultado_sp["MensajeSP"],
            codigo=resultado_sp["NroTransaccion"],
            status_code=status.HTTP_200_OK,
            result={
                "NuevoSaldoDisponible": resultado_sp["NuevoSaldoDisponible"],
                "NuevoSaldoEmbargado": resultado_sp["NuevoSaldoEmbargado"]
            }
        )
    
    except HTTPException as h_e:
        raise h_e # Propaga los errores 403/400 que acabamos de lanzar
        
    except Exception as e:
        import traceback; traceback.print_exc() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor durante el retiro.",
                codigo="SYS-500",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )

@router.post(
    "/crearCuentasBancarias",
    response_model=APIResponse,  # Indica el esquema de respuesta estándar
    status_code=status.HTTP_201_CREATED
) 
def crear_nueva_cuenta(
    *,
    session: SessionDep,
    datos_cuenta: CuentaCreationData
):
    """
    Endpoint para crear una nueva cuenta llamando al SP.
    Aplica el formato de respuesta estandarizado.
    """
    try:
        # 1. Llamada al servicio
        resultado_sp = account_service.insertar_nueva_cuenta_sp(
            session=session, datos=datos_cuenta
        )
        
        # 2. Respuesta de Éxito (Status HTTP 201)
        return APIResponse(
            mensaje=resultado_sp["MensajeSP"],
            codigo=resultado_sp["NroCta"],  # El NroCta es nuestro código de referencia/ID
            status_code=status.HTTP_201_CREATED
        )
    
    except ValueError as ve:
        # 3. Manejo de Errores de Negocio (del SP): Cliente no encontrado, etc.
        error_message = str(ve)
        
        # Usamos 400 Bad Request para errores que el usuario podría haber prevenido
        # o 409 Conflict si fuera por duplicidad, pero 400 es seguro para datos erróneos
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=APIResponse(
                mensaje=error_message,
                codigo="",  # Código de error de negocio interno para "Datos Inválidos"
                status_code=status.HTTP_400_BAD_REQUEST
            ).model_dump()  # Convierte el modelo a un diccionario
        )
    
    except Exception as e:
        # 4. Manejo de Errores Internos Inesperados
        print("🔴 OCURRIÓ UN ERROR INESPERADO:", e)
        traceback.print_exc() 
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor.",
                codigo="",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )
        

@router.get(
    "/getCuentasBancarias",
    response_model=APIResponse,  # Define el modelo de respuesta estandarizado
    status_code=status.HTTP_200_OK,
    summary="Lista las cuentas bancarias por usuario o todas (Administrador)."
)
def listar_cuentas(
    *,
    session: SessionDep,
    # Recibe el código de usuario como parámetro de consulta (query parameter) opcional
    cod_usu: Optional[str]=Query(
        default=None,
        max_length=10,
        description="Código del usuario a filtrar. Si es nulo o vacío, lista todas las cuentas."
    )
):
    """
    Recupera las cuentas bancarias. Puede filtrar por código de usuario.
    """
    try:
        # Llama al servicio, pasando el parámetro de consulta directamente.
        # La limpieza de p_cod_usu = '' a None se maneja dentro del servicio/SP.
        lista_cuentas_dto: List[CuentaDetailsDTO] = listar_cuentas_sp(
            session=session,
            cod_usu_input=cod_usu
        )
        
        # 1. Verifica si la lista está vacía (posiblemente porque el usuario no tiene cuentas)
        if not lista_cuentas_dto and cod_usu is not None and cod_usu != '':
            return APIResponse(
                mensaje=f"No se encontraron cuentas para el usuario: {cod_usu}.",
                codigo="LIST-OK-EMPTY",
                status_code=status.HTTP_200_OK,
                result=[]
            )

        # 2. Respuesta de Éxito (Status HTTP 200)
        return APIResponse(
            mensaje=f"Consulta exitosa. Se encontraron {len(lista_cuentas_dto)} cuentas.",
            codigo="LIST-OK",
            status_code=status.HTTP_200_OK,
            result=lista_cuentas_dto  # Aquí va la lista de DTOs mapeados
        )
    
    except Exception as e:
        # 3. Manejo de Errores Internos
        print("🔴 OCURRIÓ UN ERROR INESPERADO AL LISTAR CUENTAS:", e)
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


@router.patch(
    "/updateEstadoCuenta",  # Usamos PATCH /api/v1/cuentas/estado
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,  # 200 OK es común para actualizaciones exitosas
    summary="Actualiza el estado de una cuenta bancaria (Bloquear/Activar)."
)
def actualizar_estado(
    *,
    session: SessionDep,
    datos_actualizacion: CuentaEstadoUpdate  # Recibe el cuerpo JSON
):
    """
    Actualiza el estado (A, I, B) de una cuenta específica.
    """
    try:
        # 1. Llamada al servicio
        resultado_sp = actualizar_estado_cuenta_sp(
            session=session, datos=datos_actualizacion
        )
        
        # 2. Respuesta de Éxito (Status HTTP 200 OK)
        return APIResponse(
            mensaje=resultado_sp["MensajeSP"],
            codigo=resultado_sp["NroCta"],  # Devolvemos el NroCta modificado como código
            status_code=status.HTTP_200_OK
        )
    
    except ValueError as ve:
        # 3. Manejo de Errores de Negocio (Cuenta no encontrada, etc.)
        error_message = str(ve)
        
        # 404 Not Found si el error es 'No se encontró la cuenta'
        error_code = status.HTTP_404_NOT_FOUND if error_message.startswith('Error: No se encontró') else status.HTTP_400_BAD_REQUEST
        
        raise HTTPException(
            status_code=error_code,
            detail=APIResponse(
                mensaje=error_message,
                codigo="",
                status_code=error_code
            ).model_dump()
        )
    
    except Exception as e:
        # 4. Manejo de Errores Internos (500)
        print("🔴 ERROR INESPERADO AL ACTUALIZAR ESTADO:", e)
        traceback.print_exc() 
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse(
                mensaje="Ocurrió un error interno del servidor.",
                codigo="",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            ).model_dump()
        )
