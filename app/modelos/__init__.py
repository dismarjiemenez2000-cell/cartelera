"""Modelos ORM de Cartelera.

Importarlos todos aquí hace que database.crear_tablas() los registre en Base.
"""
from app.modelos.calificacion import Calificacion
from app.modelos.pelicula import Pelicula
from app.modelos.usuario import Usuario

__all__ = ["Usuario", "Pelicula", "Calificacion"]