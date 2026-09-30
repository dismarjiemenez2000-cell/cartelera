"""Repositorio de calificaciones: SOLO acceso a datos (ADR-001, ADR-005)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modelos import Calificacion


class RepositorioCalificaciones:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def por_usuario_y_pelicula(self, usuario_id: int, pelicula_id: int) -> Calificacion | None:
        consulta = select(Calificacion).where(
            Calificacion.usuario_id == usuario_id,
            Calificacion.pelicula_id == pelicula_id,
        )
        return self.sesion.scalars(consulta).first()

    def guardar(self, calificacion: Calificacion) -> Calificacion:
        self.sesion.add(calificacion)
        self.sesion.commit()
        self.sesion.refresh(calificacion)
        return calificacion