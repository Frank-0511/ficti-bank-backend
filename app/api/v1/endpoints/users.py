# app/api/v1/endpoints/users.py

from fastapi import APIRouter, HTTPException
from app.api.v1.deps import SessionDep, CurrentUser
from app.schemas.user import (
    UsuarioCreate,
    UsuarioPublic,
    UsuarioUpdate
)
from app.services import user_service

router = APIRouter()


# ============================================================
# 1. REGISTRAR USUARIO
# ============================================================

@router.post("/", response_model=UsuarioPublic)
def register_user(session: SessionDep, user_in: UsuarioCreate):
    try:
        return user_service.create_user(session=session, user_in=user_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================
# 2. OBTENER USUARIO ACTUAL
# ============================================================

@router.get("/me", response_model=UsuarioPublic)
def read_users_me(current_user: CurrentUser):
    return current_user



# ============================================================
# 3. ACTUALIZAR USUARIO
# ============================================================

@router.patch("/update/{codusu}", response_model=dict)
def update_user(codusu: str, data: UsuarioUpdate, session: SessionDep):
    try:
        return user_service.update_user(
            session=session,
            codusu=codusu,
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================
# 4. LISTAR ADMINISTRADORES
# ============================================================

@router.get("/admins", response_model=list[dict])
def listar_administradores(session: SessionDep):
    try:
        return user_service.listar_administradores(session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================
# 5. LISTAR EMPLEADOS
# ============================================================

@router.get("/employees", response_model=list[dict])
def listar_empleados(session: SessionDep):
    try:
        return user_service.listar_empleados(session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
