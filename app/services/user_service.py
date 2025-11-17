# app/services/user_service.py

# --- 1. Importaciones Corregidas y Completas ---
from typing import Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy import text
from app.core import security
from app.models.user import Usuario
from app.schemas.user import UsuarioCreate, UserFromDB


# --- 2. Función de Autenticación con Stored Procedure (Mejorada) ---

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


# --- 3. Función para Crear Usuario (ya la tenías) ---

def create_user(session: Session, user_in: UsuarioCreate) -> Usuario:
    """
    Crea un nuevo usuario en la base de datos.
    """
    db_user = Usuario(
        CodUsu=user_in.CodUsu,
        Usuario=user_in.Usuario,
        Rol=user_in.Rol,
        HashedPassword=security.get_password_hash(user_in.Password),
        Estado='A'  # 'A' de Activo por defecto
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user