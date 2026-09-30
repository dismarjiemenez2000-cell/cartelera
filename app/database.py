"""Conexión a la base de datos y sesión de SQLAlchemy (ADR-002).

El motor se elige por la URL de config.py: SQLite en desarrollo, Postgres en
producción. El resto del código nunca sabe cuál está usando.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL

# SQLite necesita este parámetro porque FastAPI atiende peticiones desde varios
# hilos y, por defecto, la librería sqlite3 rechaza conexiones cruzadas.
es_sqlite = DATABASE_URL.startswith("sqlite")
motor = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if es_sqlite else {},
)

# expire_on_commit=False: los objetos siguen útiles después de guardarlos
# (podremos leer u1.id después de un commit sin recargar nada)
SesionLocal = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Clase padre de todos los modelos ORM."""


def crear_tablas() -> None:
    """Crea las tablas si no existen.

    Cómodo para un proyecto de aprendizaje; en un sistema real se usan
    migraciones versionadas (Alembic), porque create_all NO modifica tablas
    ya creadas. Ver ADR-002.
    """
    from app import modelos  # noqa: F401 — importar registra los modelos en Base

    Base.metadata.create_all(bind=motor)


def obtener_sesion():
    """Dependencia de FastAPI: una sesión por petición, cerrada al final."""
    sesion: Session = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()