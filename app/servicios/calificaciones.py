"""Servicio de calificaciones: la regla RN-01 vive aquí (ADR-005).

Tanto el widget HTML como el endpoint JSON llegarán a esta MISMA función:
una sola lógica, dos caras (ADR-001).
"""
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modelos import Calificacion, Usuario
from app.repositorios import RepositorioCalificaciones, RepositorioPeliculas


def calificar(sesion: Session, usuario: Usuario, pelicula_id: int, estrellas: int) -> Calificacion:
    """Guarda o reemplaza la calificación del usuario (RF-08, RF-09, RN-01).

    "Recalificar" no crea una segunda fila: actualiza la existente (upsert).
    Si dos peticiones simultáneas lograran colarse, la restricción UNIQUE de
    la base de datos frena a la segunda (lo viste en la guía 2).
    """
    if RepositorioPeliculas(sesion).por_id(pelicula_id) is None:
        raise HTTPException(404, "Película no encontrada.")

    repo = RepositorioCalificaciones(sesion)
    existente = repo.por_usuario_y_pelicula(usuario.id, pelicula_id)

    if existente is not None:
        existente.estrellas = estrellas
        existente.actualizado_en = datetime.now(timezone.utc)
        sesion.commit()
        return existente

    return repo.guardar(
        Calificacion(usuario_id=usuario.id, pelicula_id=pelicula_id, estrellas=estrellas)
    )


def mi_calificacion(sesion: Session, usuario: Usuario | None, pelicula_id: int) -> int:
    """Estrellas que dio este usuario a esta película (0 si no ha calificado)."""
    if usuario is None:
        return 0
    fila = RepositorioCalificaciones(sesion).por_usuario_y_pelicula(usuario.id, pelicula_id)
    return fila.estrellas if fila else 0