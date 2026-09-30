"""Panel de administración: publica y elimina películas (RN-04).

El router ENTERO queda protegido por requiere_admin: sin sesión → 401;
con sesión de socia → 403.
"""
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import obtener_sesion
from app.dependencias import requiere_admin, usuario_obligatorio
from app.modelos import Usuario
from app.repositorios import RepositorioPeliculas
from app.rutas.web import _extras_vista
from app.servicios import peliculas as servicio_peliculas

plantillas = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "plantillas")
)

router = APIRouter(
    prefix="/admin", tags=["Administración"], dependencies=[Depends(requiere_admin)]
)


@router.get("")
@router.get("/")
def panel(
    request: Request,
    usuario: Usuario = Depends(usuario_obligatorio),
    sesion: Session = Depends(obtener_sesion),
):
    repo = RepositorioPeliculas(sesion)
    promedios = repo.promedios()
    peliculas = []
    for pelicula in repo.listar():
        datos = servicio_peliculas.a_resumen(pelicula, *promedios.get(pelicula.id, (0.0, 0)))
        datos.update(_extras_vista(*promedios.get(pelicula.id, (0.0, 0))))
        peliculas.append(datos)
    return plantillas.TemplateResponse(
        request=request, name="admin/panel.html",
        context={"usuario": usuario, "peliculas": peliculas},
    )


@router.post("/peliculas")
def crear_pelicula(
    titulo: str = Form(...),
    anio: int = Form(...),
    sinopsis: str = Form(""),
    url_trailer: str = Form(...),
    caratula: UploadFile | None = File(None),
    usuario: Usuario = Depends(usuario_obligatorio),
    sesion: Session = Depends(obtener_sesion),
):
    # Las reglas (YouTube, formato, tamaño) las valida el servicio (RN-03, RN-05)
    servicio_peliculas.crear_pelicula(sesion, titulo, anio, sinopsis, url_trailer, caratula)
    return RedirectResponse("/admin", status_code=303)


@router.post("/peliculas/{pelicula_id}/eliminar")
def eliminar_pelicula(
    pelicula_id: int,
    usuario: Usuario = Depends(usuario_obligatorio),
    sesion: Session = Depends(obtener_sesion),
):
    pelicula = RepositorioPeliculas(sesion).por_id(pelicula_id)
    if pelicula is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    servicio_peliculas.eliminar_pelicula(sesion, pelicula)
    return RedirectResponse("/admin", status_code=303)