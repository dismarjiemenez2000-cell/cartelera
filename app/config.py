"""Configuración central de Cartelera.

Toda la configuración vive en variables de entorno con valores por defecto
pensados para desarrollo local. En producción (Render) se configuran en el
dashboard y este archivo no cambia. Ver docs/04_arquitectura (RNF-03).
"""
import os
from pathlib import Path

# Carpeta raíz del proyecto (este archivo es app/config.py, la raíz está un nivel arriba)
BASE_DIR = Path(__file__).resolve().parent.parent

# Firma de los tokens JWT (ADR-003)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secreto-cambiar-en-produccion")

# URL de la base de datos (ADR-002)
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{(BASE_DIR / 'cartelera.db').as_posix()}"
)

# Carpeta de carátulas subidas (ADR-004)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))

# Vida útil del token, en días (ADR-003)
DIAS_TOKEN = 7
#Este archivo define todas las configuraciones de la aplicación.

# Nombre de la cookie de sesión (ADR-003)
NOMBRE_COOKIE = "sesion"

# Cuenta de coordinadora que crea semilla.py
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "coordinadora@cineclub.cl")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")