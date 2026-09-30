"""Esquemas Pydantic de películas (contrato: schemas PeliculaResumen, PeliculaDetalle)."""
from pydantic import BaseModel


class PeliculaResumen(BaseModel):
    id: int
    titulo: str
    anio: int
    promedio: float
    total_calificaciones: int
    imagen: str  # URL pública de la carátula o placeholder (RN-05)


class PeliculaDetalle(PeliculaResumen):
    sinopsis: str
    url_trailer: str