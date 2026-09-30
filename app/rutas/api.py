"""API JSON, documentada automáticamente en /docs (RF-10, contrato_api.yaml).

Punto pedagógico clave (ADR-001): estas rutas llaman a los MISMOS servicios
que usarán las páginas HTML de la guía 6. Dos caras, una sola lógica.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import obtener_sesion
from app.dependencias import usuario_obligatorio
from app.esquemas import (
    CalificacionEntrada,
    CalificacionRespuesta,
    PeliculaDetalle,
    PeliculaResumen,
    SolicitudSesion,
    UsuarioCrear,
    UsuarioOut,
)
from app.modelos import Usuario
from app.repositorios import RepositorioPeliculas
from app.servicios import autenticacion
from app.servicios import calificaciones as servicio_calificaciones
from app.servicios import peliculas as servicio_peliculas

router = APIRouter(prefix="/api", tags=["API JSON"])


@router.get("/peliculas", response_model=list[PeliculaResumen])
def listar_peliculas(sesion: Session = Depends(obtener_sesion)):
    repo = RepositorioPeliculas(sesion)
    promedios = repo.promedios()  # una sola consulta para todo el catálogo
    return [
        servicio_peliculas.a_resumen(p, *promedios.get(p.id, (0.0, 0)))
        for p in repo.listar()
    ]


@router.get("/peliculas/{pelicula_id}", response_model=PeliculaDetalle)
def ver_pelicula(pelicula_id: int, sesion: Session = Depends(obtener_sesion)):
    pelicula = RepositorioPeliculas(sesion).por_id(pelicula_id)
    if pelicula is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    promedio, total = RepositorioPeliculas(sesion).promedio(pelicula_id)
    return servicio_peliculas.a_detalle(pelicula, promedio, total)


@router.post("/usuarios", response_model=UsuarioOut, status_code=201)
def crear_usuario(datos: UsuarioCrear, sesion: Session = Depends(obtener_sesion)):
    try:
        return autenticacion.registrar(sesion, datos.nombre, datos.email, datos.contrasena)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.post("/sesion")
def iniciar_sesion(datos: SolicitudSesion, sesion: Session = Depends(obtener_sesion)):
    """Devuelve el token JWT para usar en las demás rutas (cabecera Bearer)."""
    try:
        token = autenticacion.entrar(sesion, datos.email, datos.contrasena)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))
    return {"token": token}


@router.get("/yo", response_model=UsuarioOut)
def quien_soy(usuario: Usuario = Depends(usuario_obligatorio)):
    """Prueba rápida del token (botón Authorize en /docs)."""
    return usuario


@router.post("/calificaciones", response_model=CalificacionRespuesta)
def calificar(
    datos: CalificacionEntrada,
    usuario: Usuario = Depends(usuario_obligatorio),
    sesion: Session = Depends(obtener_sesion),
):
    fila = servicio_calificaciones.calificar(
        sesion, usuario, datos.pelicula_id, datos.estrellas
    )
    promedio, total = RepositorioPeliculas(sesion).promedio(datos.pelicula_id)
    return CalificacionRespuesta(
        promedio=round(promedio, 1),
        total_calificaciones=total,
        mi_calificacion=fila.estrellas,
    )