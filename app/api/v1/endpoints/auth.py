from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.api.v1.deps import SessionDep
from app.core.security import create_access_token
from app.schemas.token import Token
from app.services import user_service

router = APIRouter()

@router.post("/token", response_model=Token)
def login_for_access_token(
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Endpoint para el login de usuarios.
    Recibe 'username' y 'password' en un form-data.
    Devuelve el token Y los datos del usuario en la variable 'result'.
    """
    print(f"Intentando autenticar al usuario: {form_data.username}")

    # 1. ¡CAMBIO! La función ahora devuelve una tupla
    user, result_data = user_service.authenticate_user_with_sp(
        session=session, username=form_data.username, password=form_data.password
    )

    if not user:
        # 'user' es None, la autenticación falló
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Si el login fue exitoso, `user` contiene el objeto UserFromDB.
    access_token = create_access_token(data={"sub": user.Usuario})
    
    # 2. ¡CAMBIO! Convertimos los datos de la lista (que son RowMappings)
    #    a una lista de diccionarios (JSON)
    result_json_list = [dict(row) for row in result_data]

    # 3. ¡CAMBIO! Devolvemos el token Y la variable 'result'
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "result": result_json_list  #
    }