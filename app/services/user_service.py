# app/services/user_service.py

from typing import Optional, Dict, Any
from sqlmodel import Session
from sqlalchemy import text
from app.core import security
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UserFromDB, UsuarioUpdate


# ============================================================
# 1. AUTENTICACIÓN CON STORED PROCEDURE
# ============================================================

def authenticate_user_with_sp(session: Session, username: str, password: str) -> tuple[Optional[UserFromDB], list]:
    """
    Autentica a un usuario llamando al SP sp_ValidateUserLogin.
    
    DEVUELVE:
    Una tupla: (UsuarioValidado | None, ListaDeResultadosRaw | ListaVacía)
    """
    result_list = []  # Inicializamos la lista de resultados
    try:
        # 1. Preparamos y ejecutamos la llamada al SP.
        query = text("CALL sp_ValidateUserLogin(:p_Username, @p_Out_Message);")
        result_proxy = session.execute(query, {"p_Username": username})
        
        # 2. ¡CAMBIO CLAVE! Leemos el resultado del SELECT como una LISTA
        #    Usamos .all() y lo guardamos en 'result_list'
        result_list = result_proxy.mappings().all()

        # 3. Obtenemos el valor del parámetro OUT.
        message_result = session.execute(text("SELECT @p_Out_Message;"))
        message_from_db = message_result.scalar_one_or_none()

        # --- LÓGICA DE VALIDACIÓN EN PYTHON ---

        if "Error:" in (message_from_db or ""):
            print(f"Error desde la BD para usuario '{username}': {message_from_db}")
            return None, []  # Devolvemos (None, lista vacía)

        # Si la lista está vacía, el usuario no se encontró.
        if not result_list:
            print(f"Usuario '{username}' no encontrado.")
            return None, []  # Devolvemos (None, lista vacía)

        # print(f"Datos recibidos de la BD para '{username}': {result_list}")
        user_data_from_list = result_list[0]
        
        # Validamos el modelo Pydantic/SQLModel
        user = UserFromDB.model_validate(user_data_from_list)

        # Verificamos la contraseña
        if not security.verify_password(password, user.HashedPassword):
            print(f"Contraseña incorrecta para '{username}'.")
            return None, []  # Autenticación fallida, devolvemos (None, lista vacía)

        # ¡Éxito! Devolvemos el objeto User Y la lista 'result'
        return user, result_list

    except Exception as e:
        print(f"🔴 Ocurrió una excepción inesperada durante la autenticación: {e}")
        return None, []  # Devolvemos (None, lista vacía) en caso de excepción


# ============================================================
# 2. CREAR USUARIO
# ============================================================

def create_user(session: Session, user_in: UsuarioCreate) -> Usuario:
    db_user = Usuario(
        CodUsu=user_in.CodUsu,
        Usuario=user_in.Usuario,
        Rol=user_in.Rol,
        HashedPassword=security.get_password_hash(user_in.Password),
        Estado="A"
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# ============================================================
# 3. ACTUALIZAR USUARIO
# ============================================================

def update_user(session: Session, codusu: str, data: UsuarioUpdate) -> Dict[str, Any]:
    user = session.get(Usuario, codusu)

    if not user:
        raise Exception("El usuario no existe")

    if data.Usuario is not None:
        user.Usuario = data.Usuario

    if data.Rol is not None:
        user.Rol = data.Rol

    if data.Estado is not None:
        user.Estado = data.Estado

    if data.Password is not None:
        user.HashedPassword = security.get_password_hash(data.Password)

    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "mensaje": "Usuario actualizado correctamente",
        "CodUsu": user.CodUsu,
        "Usuario": user.Usuario,
        "Rol": user.Rol,
        "Estado": user.Estado
    }


# ============================================================
# 4. LISTAR ADMINISTRADORES (SP)
# ============================================================

def listar_administradores(session: Session):
    query = text("CALL sp_ListarAdministradores();")
    result = session.execute(query)
    return [dict(row) for row in result.mappings().all()]


# ============================================================
# 5. LISTAR EMPLEADOS (SP) → FILTRADO A NIVEL BACKEND
# ============================================================

def listar_empleados(session: Session):
    """
    Lista SOLO usuarios con Rol = 'E'
    (Se filtra en backend para no depender del SP)
    """
    query = text("CALL sp_ListarEmpleados();")
    result = session.execute(query)

    empleados = [dict(row) for row in result.mappings().all()]

    # FILTRAR SOLO ROL 'E'
    empleados_filtrados = [emp for emp in empleados if emp.get("Rol") == "E"]

    return empleados_filtrados
from sqlmodel import Session
from app.schemas.user import StaffRegistrationData
from passlib.context import CryptContext
from typing import Dict, Any

# Contexto de hashing para simulación (si no tienes uno ya)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_staff_sp(session: Session, user_data: StaffRegistrationData) -> Dict[str, Any]:
    """
    SIMULACIÓN: Hashea la contraseña y llama al SP de la BD para registrar el usuario interno.
    """
    
    # 1. Hashear Contraseña (Simulado)
    hashed_password = pwd_context.hash(user_data.Password)
    
    # 2. Llamada al SP de la BD (DEBES CREAR ESTE SP)
    # Aquí iría la lógica para llamar a un SP como 'sp_RegistrarUsuarioInterno'.
    
    # Simulación de éxito:
    return {
        "CodUsu": "USU-" + user_data.Usuario.upper()[:4],
        "Usuario": user_data.Usuario,
        "Rol": user_data.Rol,
        "MensajeSP": f"Éxito: Usuario interno '{user_data.Usuario}' registrado con Rol '{user_data.Rol}'."
    }
from app.schemas.user import StaffRegistrationData
from sqlmodel import Session
from passlib.context import CryptContext
from typing import Dict, Any

# Es posible que ya tengas un contexto de hashing, pero lo definimos aquí por seguridad.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_staff_sp(session: Session, user_data: StaffRegistrationData) -> Dict[str, Any]:
    """
    SIMULACIÓN: Hashea la contraseña y llama al SP de la BD para registrar el usuario interno.
    """
    
    # 1. Simulación de Hashing (si usas passlib)
    hashed_password = pwd_context.hash(user_data.Password)
    
    # 2. Lógica de Llamada al SP de la BD (DEBES IMPLEMENTAR ESTO CON TU SP REAL)
    # Por ahora, simularemos un éxito.
    
    # Si quisieras llamar al SP, el código sería similar a:
    # query = text("CALL sp_RegistrarUsuarioInterno(:usuario, :hash, :rol, ...)")
    # session.execute(query, { "usuario": user_data.Usuario, "hash": hashed_password, "rol": user_data.Rol, ... })
    
    # Simulación de Éxito:
    if user_data.Usuario == "fail_test":
        raise ValueError("El usuario ya existe en la base de datos.")

    return {
        "CodUsu": "USR" + user_data.Rol + str(hash(user_data.Usuario))[:4],
        "Usuario": user_data.Usuario,
        "Rol": user_data.Rol,
        "MensajeSP": f"Éxito: Usuario interno '{user_data.Usuario}' registrado con Rol '{user_data.Rol}'."
    }