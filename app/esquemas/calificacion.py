"""Esquemas Pydantic de calificaciones (contrato: schemas CalificacionEntrada/Respuesta)."""
from pydantic import BaseModel, Field


class CalificacionEntrada(BaseModel):
    pelicula_id: int
    estrellas: int = Field(ge=1, le=5)  # RN-02: entero 1–5; fuera de rango → 422


class CalificacionRespuesta(BaseModel):
    promedio: float
    total_calificaciones: int
    mi_calificacion: int