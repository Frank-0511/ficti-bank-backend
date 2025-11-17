from fastapi import FastAPI
from app.api.v1.api import api_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Sistema Bancario API")

# ❗ No crear tablas automáticamente
def safe_create_db_and_tables():
    try:
        # create_db_and_tables()   ← NO USAR SQLModel.create_all()
        logger.info("🔵 Modo producción/desarrollo: NO se crean tablas automáticamente.")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo conectar a la BD al iniciar: {e}")

@app.on_event("startup")
def on_startup():
    # ❗ NO LLAMAR safe_create_db_and_tables
    logger.info("🚀 Sistema Bancario API iniciado correctamente (sin crear tablas).")

# Registrar rutas
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Bienvenido al API del Sistema Bancario"}
