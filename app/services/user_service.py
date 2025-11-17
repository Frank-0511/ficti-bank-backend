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

def authenticate_user_with_sp(session: Session, username: str, password: str) -> Optional[UserFromDB]:
    try:
        query = text("CALL sp_ValidateUserLogin(:p_Username, @p_Out_Message);")
        result_proxy = session.execute(query, {"p_Username": username})

        user_data = result_proxy.mappings().first()

        message_result = session.execute(text("SELECT @p_Out_Message;"))
        message = message_result.scalar_one_or_none()

        if "Error:" in (message or ""):
            return None

        if not user_data:
            return None

        user = UserFromDB.model_validate(user_data)

        if not security.verify_password(password, user.HashedPassword):
            return None

        return user

    except Exception as e:
        print(f"🔴 Error inesperado durante autenticación: {e}")
        return None


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
