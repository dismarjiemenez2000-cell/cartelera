"""Rutas web: las páginas HTML del sitio (ADR-001 capa de rutas, ADR-006 SSR)."""
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import DIAS_TOKEN, NOMBRE_COOKIE
from app.database import obtener_sesion
from app.dependencias import obtener_usuario_actual
from app.esquemas import UsuarioCrear
from app.modelos import Usuario
from app.repositorios import RepositorioPeliculas
from app.servicios import autenticacion
from app.servicios import calificaciones as servicio_calificaciones
from app.servicios import peliculas as servicio_peliculas

plantillas = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "plantillas")
)

router = APIRouter(tags=["Web"])

# Mensajes en español para los errores que Pydantic reporta en inglés
MENSAJES_CAMPO = {
    "nombre": "El nombre debe tener al menos 2 caracteres.",
    "email": "El email no tiene un formato válido.",
    "contrasena": "La contraseña debe tener al menos 8 caracteres.",
}


def _extras_vista(promedio: float, total: int) -> dict:
    """Presentación del bloque de estrellas (formato chileno: coma decimal)."""
    if total > 0:
        texto_promedio = f"{promedio:.1f}".replace(".", ",")
        return {
            "llenas": round(promedio),
            "texto": f"{texto_promedio} · {total} calificación{'es' if total != 1 else ''}",
        }
    return {"llenas": 0, "texto": "Sin calificaciones"}


# ---------- Catálogo público ----------

@router.get("/")
def inicio(
    request: Request,
    usuario: Usuario | None = Depends(obtener_usuario_actual),
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
        request=request, name="index.html",
        context={"usuario": usuario, "peliculas": peliculas},
    )


@router.get("/pelicula/{pelicula_id}")
def ficha(
    pelicula_id: int,
    request: Request,
    usuario: Usuario | None = Depends(obtener_usuario_actual),
    sesion: Session = Depends(obtener_sesion),
):
    repo = RepositorioPeliculas(sesion)
    pelicula = repo.por_id(pelicula_id)
    if pelicula is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")

    promedio, total = repo.promedio(pelicula_id)
    datos = servicio_peliculas.a_detalle(pelicula, promedio, total)
    datos.update(_extras_vista(promedio, total))

    return plantillas.TemplateResponse(
        request=request,
        name="detalle.html",
        context={
            "usuario": usuario,
            "pelicula": datos,
            "mi_calificacion": servicio_calificaciones.mi_calificacion(sesion, usuario, pelicula_id),
        },
    )


# ---------- Cuentas ----------

@router.get("/registro")
def formulario_registro(request: Request):
    return plantillas.TemplateResponse(
        request=request, name="registro.html",
        context={"usuario": None, "error": None, "valores": {}},
    )


@router.post("/registro")
def registrar(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    contrasena: str = Form(...),
    sesion: Session = Depends(obtener_sesion),
):
    valores = {"nombre": nombre, "email": email}
    try:
        # El MISMO esquema de la API valida el formulario web: una sola
        # definición de "cómo se ve un registro correcto" (ADR-001 en acción)
        UsuarioCrear(nombre=nombre.strip(), email=email.strip().lower(), contrasena=contrasena)
    except ValidationError as error:
        campo = str(error.errors()[0]["loc"][-1])
        return plantillas.TemplateResponse(
            request=request, name="registro.html",
            context={"usuario": None,
                     "error": MENSAJES_CAMPO.get(campo, "Datos inválidos."),
                     "valores": valores},
        )

    try:
        autenticacion.registrar(sesion, nombre, email, contrasena)
    except ValueError as error:  # email duplicado u otra regla del servicio
        return plantillas.TemplateResponse(
            request=request, name="registro.html",
            context={"usuario": None, "error": str(error), "valores": valores},
        )

    return RedirectResponse("/login?registrado=1", status_code=303)


@router.get("/login")
def formulario_login(request: Request, registrado: int = 0):
    return plantillas.TemplateResponse(
        request=request, name="login.html",
        context={"usuario": None, "error": None, "registrado": bool(registrado)},
    )


@router.post("/login")
def iniciar_sesion(
    request: Request,
    email: str = Form(...),
    contrasena: str = Form(...),
    sesion: Session = Depends(obtener_sesion),
):
    try:
        token = autenticacion.entrar(sesion, email, contrasena)
    except ValueError as error:
        return plantillas.TemplateResponse(
            request=request, name="login.html",
            context={"usuario": None, "error": str(error), "registrado": False},
        )

    respuesta = RedirectResponse("/", status_code=303)
    # HttpOnly: el JavaScript de la página no puede leer la cookie (ADR-003)
    respuesta.set_cookie(
        NOMBRE_COOKIE, token,
        max_age=DIAS_TOKEN * 24 * 3600, httponly=True, samesite="lax",
    )
    return respuesta


@router.get("/salir")
def salir():
    respuesta = RedirectResponse("/", status_code=303)
    respuesta.delete_cookie(NOMBRE_COOKIE)
    return respuesta

