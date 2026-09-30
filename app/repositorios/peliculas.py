"""Repositorio de películas: SOLO acceso a datos (ADR-001).

Incluye las consultas de promedio (ADR-005): AVG y COUNT se calculan en la
base de datos, no trayendo todas las filas a Python.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modelos import Calificacion, Pelicula


class RepositorioPeliculas:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def listar(self) -> list[Pelicula]:
        return list(
            self.sesion.scalars(select(Pelicula).order_by(Pelicula.creado_en.desc()))
        )

    def por_id(self, pelicula_id: int) -> Pelicula | None:
        return self.sesion.get(Pelicula, pelicula_id)

    def crear(self, pelicula: Pelicula) -> Pelicula:
        self.sesion.add(pelicula)
        self.sesion.commit()
        self.sesion.refresh(pelicula)
        return pelicula

    def eliminar(self, pelicula: Pelicula) -> None:
        # las calificaciones asociadas se eliminan en cascada (guía 2)
        self.sesion.delete(pelicula)
        self.sesion.commit()

    def promedio(self, pelicula_id: int) -> tuple[float, int]:
        """(promedio, cantidad) de una película. (0.0, 0) si nadie ha votado."""
        consulta = select(
            func.coalesce(func.avg(Calificacion.estrellas), 0.0),
            func.count(),
        ).where(Calificacion.pelicula_id == pelicula_id)
        fila = self.sesion.execute(consulta).one()
        return float(fila[0]), int(fila[1])

    def promedios(self) -> dict[int, tuple[float, int]]:
        """Promedios de TODAS las películas en una sola consulta.

        Evita el problema N+1: una consulta para el catálogo completo en vez
        de una de promedio por cada película.
        """
        consulta = select(
            Calificacion.pelicula_id,
            func.avg(Calificacion.estrellas),
            func.count(),
        ).group_by(Calificacion.pelicula_id)
        filas = self.sesion.execute(consulta).all()
        return {fila[0]: (float(fila[1]), int(fila[2])) for fila in filas}