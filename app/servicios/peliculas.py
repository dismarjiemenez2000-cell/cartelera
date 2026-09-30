"""Servicio de películas: reglas del catálogo (RN-03, RN-05) y armado de vistas."""
import os
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.modelos import Pelicula
from app.repositorios import RepositorioPeliculas
from app.servicios.almacenamiento import almacenamiento

# RN-05: formatos y tamaño máximo de la carátula
EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
TAMANO_MAXIMO = 5 * 1024 * 1024  # 5 MB


def normalizar_trailer(url: str) -> str:
    """Valida que el link sea de YouTube y lo convierte a formato embed (RN-03).

    Acepta los tres formatos que la gente pega:
      - https://www.youtube.com/watch?v=ID
      - https://youtu.be/ID
      - https://www.youtube.com/shorts/ID
    Lanza ValueError con mensaje si el link no sirve.
    """
    partes = urlparse(url.strip())
    dominio = partes.netloc.lower().removeprefix("www.")

    if dominio not in ("youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"):
        raise ValueError("El tráiler debe ser un link de YouTube.")

    video_id = ""
    if dominio == "youtu.be":
        video_id = partes.path.lstrip("/")
    else:
        video_id = parse_qs(partes.query).get("v", [""])[0]
        if not video_id and "/shorts/" in partes.path:
            video_id = partes.path.split("/shorts/")[1].split("/")[0]

    video_id = video_id.strip("/")
    if not video_id:
        raise ValueError("No se pudo encontrar el video en el link de YouTube.")

    return f"https://www.youtube.com/embed/{video_id}"


def crear_pelicula(
    sesion: Session,
    titulo: str,
    anio: int,
    sinopsis: str,
    url_trailer: str,
    caratula: UploadFile | None,
) -> Pelicula:
    """Crea la película validando las reglas (RF-04, RN-03, RN-05)."""
    titulo = titulo.strip()
    if not titulo:
        raise HTTPException(400, "El título es obligatorio.")

    try:
        trailer_embed = normalizar_trailer(url_trailer)
    except ValueError as error:
        raise HTTPException(400, str(error))

    ruta = None
    if caratula is not None and caratula.filename:
        extension = os.path.splitext(caratula.filename)[1].lower()
        if extension not in EXTENSIONES_PERMITIDAS:
            raise HTTPException(
                400, f"Carátula no permitida ({extension}). Usa JPG, PNG o WebP."
            )
        contenido = caratula.file.read()
        if len(contenido) > TAMANO_MAXIMO:
            raise HTTPException(400, "La carátula supera el máximo de 5 MB.")
        ruta = almacenamiento.guardar(caratula.filename, contenido)

    pelicula = Pelicula(
        titulo=titulo,
        anio=anio,
        sinopsis=sinopsis.strip(),
        url_trailer=trailer_embed,
        ruta_caratula=ruta,
    )
    return RepositorioPeliculas(sesion).crear(pelicula)


def eliminar_pelicula(sesion: Session, pelicula: Pelicula) -> None:
    """Elimina la película y su carátula del disco (RF-07)."""
    if pelicula.ruta_caratula:
        almacenamiento.eliminar(pelicula.ruta_caratula)
    RepositorioPeliculas(sesion).eliminar(pelicula)


def a_resumen(pelicula: Pelicula, promedio: float, total: int) -> dict:
    """Cómo una película se muestra en listas (lo usarán la web y la API)."""
    return {
        "id": pelicula.id,
        "titulo": pelicula.titulo,
        "anio": pelicula.anio,
        "promedio": round(promedio, 1),
        "total_calificaciones": total,
        "imagen": almacenamiento.url_publica(pelicula.ruta_caratula),
    }


def a_detalle(pelicula: Pelicula, promedio: float, total: int) -> dict:
    """La ficha completa (agrega sinopsis y tráiler al resumen)."""
    datos = a_resumen(pelicula, promedio, total)
    datos["sinopsis"] = pelicula.sinopsis
    datos["url_trailer"] = pelicula.url_trailer
    return datos