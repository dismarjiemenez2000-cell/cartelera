"""Punto de composición: arma la aplicación y conecta las piezas (ADR-001)."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import UPLOAD_DIR
from app.database import crear_tablas
from app.rutas import admin, api, web

app = FastAPI(
    title="Cartelera",
    description=(
        "Catálogo de películas del CineClub Barrio con calificación por "
        "estrellas. La misma lógica alimenta la web y esta API."
    ),
    version="1.0.0",
)

crear_tablas()

# El disco de carátulas debe existir antes de montarlo (ADR-004)
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Carpetas servidas tal cual al navegador (ADR-006)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(web.router)    # páginas HTML
app.include_router(api.router)    # API JSON (/docs)
app.include_router(admin.router)  # panel de la coordinadora


@app.get("/salud")
def salud() -> dict:
    """Chequeo mínimo para saber que el servicio está vivo."""
    return {"estado": "ok"}
#Ésto devuelve un jason con el estado ok y listuuu 