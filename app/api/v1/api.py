from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, registration, accounts, clients, embargos, movimientos
from app.api.v1.endpoints.transferencias import router as transferencias_router

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(registration.router, prefix="/registration", tags=["Registro"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clientes"])
api_router.include_router(accounts.router, prefix="/account", tags=["Cuentas"])
api_router.include_router(transferencias_router, prefix="/transferencias", tags=["Transferencias"])
api_router.include_router(embargos.router, prefix="/embargos", tags=["Embargos"])
api_router.include_router(movimientos.router, prefix="/movements", tags=["Movimientos"])