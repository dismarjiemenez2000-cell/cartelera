"""Almacenamiento de carátulas (ADR-004) — el ejemplo de DIP del proyecto.

El resto del código depende de la INTERFAZ Almacenamiento, nunca de la clase
concreta. Por eso cambiar "disco local" por "Cloudinary/S3" mañana significa
escribir UNA clase nueva y cambiar UNA línea en este archivo. Ninguna otra
capa se entera.
"""
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from app.config import UPLOAD_DIR


class Almacenamiento(ABC):
    """Contrato: lo que debe saber hacer cualquier almacén de carátulas."""

    @abstractmethod
    def guardar(self, nombre_original: str, contenido: bytes) -> str:
        """Guarda el archivo y devuelve la ruta/nombre con que se registra en la BD."""

    @abstractmethod
    def eliminar(self, ruta: str) -> None:
        """Elimina un archivo guardado previamente."""

    @abstractmethod
    def url_publica(self, ruta: str | None) -> str:
        """URL con la que el navegador puede pedir el archivo."""


class AlmacenamientoLocal(Almacenamiento):
    """Implementación de desarrollo: archivos en la carpeta uploads/.

    ADVERTENCIA (ADR-004): en Render free el disco es EFÍMERO. Los archivos
    subidos desaparecen cuando el servicio se reinicia o se vuelve a
    desplegar. En desarrollo local esto nunca molesta; en producción es la
    lección en vivo del ramo.
    """

    def __init__(self, carpeta: str = UPLOAD_DIR):
        self.carpeta = Path(carpeta)
        self.carpeta.mkdir(parents=True, exist_ok=True)

    def guardar(self, nombre_original: str, contenido: bytes) -> str:
        # Nombre nuevo aleatorio: evita choques y caracteres problemáticos
        # (una carátula llamada "shrek 2 FINAL(2).jpg" nunca debe romper nada)
        extension = Path(nombre_original).suffix.lower()
        nombre = f"{uuid.uuid4().hex}{extension}"
        (self.carpeta / nombre).write_bytes(contenido)
        return nombre

    def eliminar(self, ruta: str) -> None:
        archivo = self.carpeta / ruta
        if archivo.exists():
            archivo.unlink()

    def url_publica(self, ruta: str | None) -> str:
        if not ruta:
            return "/static/img/placeholder.svg"  # sin carátula (RN-05)
        return f"/uploads/{ruta}"


# ---------------------------------------------------------------------------
# PUNTO ÚNICO DE ELECCIÓN. El día que exista AlmacenamientoCloudinary, esta es
# la única línea del proyecto que cambia (junto con el archivo de la clase nueva).
# ---------------------------------------------------------------------------
almacenamiento: Almacenamiento = AlmacenamientoLocal()