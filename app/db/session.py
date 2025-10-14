from sqlmodel import create_engine, Session, SQLModel
from app.core.config import DATABASE_URL, DB_HOST
import logging

ssl_args = {'ssl': {'ca': 'ca.pem'}}
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LÓGICA DE CONEXIÓN CONDICIONAL ---

# 2. Verificamos si estamos en un entorno local
if DB_HOST in ("localhost", "127.0.0.1"):
    # Conexión simple para desarrollo local, sin SSL
    logger.info("🔧 Detectado entorno local. Creando engine de base de datos sin SSL.")
    engine = create_engine(DATABASE_URL)
else:
    # Conexión segura para producción/nube, con SSL
    logger.info("☁️ Detectado entorno de nube/producción. Creando engine con SSL.")
    ssl_args = {'ssl': {'ca': 'ca.pem'}}
    engine = create_engine(DATABASE_URL, connect_args=ssl_args)

#engine = create_engine(DATABASE_URL, echo=True) ## usar esto cuando no se vaya a usar ssl

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
