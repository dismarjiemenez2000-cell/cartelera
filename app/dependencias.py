"""Dependencias de FastAPI: identificar y autorizar al usuario (ADR-003)."""
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import NOMBRE_COOKIE
from app.database import obtener_sesion
from app.modelos import Usuario
from app.repositorios import RepositorioUsuarios
from app.servicios import autenticacion

# Declarar el esquema Bearer hace DOS trabajos: FastAPI extrae el encabezado
# Authorization por nosotros Y publica el esquema de seguridad en el OpenAPI
# generado — sin esto, /docs no muestra el botón Authorize.
# auto_error=False: sin encabezado devuelve None (nuestro usuario web llega
# por cookie), en vez de rechazar con un 403 automático.
seguridad_bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    request: Request,
    credenciales: HTTPAuthorizationCredentials | None = Depends(seguridad_bearer),
    sesion: Session = Depends(obtener_sesion),
) -> Usuario | None:
    """Identifica al usuario a partir del token, o None si es anónimo.

    Acepta el token de dos formas (ADR-003):
      - cabecera Authorization: Bearer <token> (pruebas desde /docs)
      - cookie 'sesion' (navegador web — la setea el login de la guía 6)
    """
    token = credenciales.credentials if credenciales is not None else None
    if not token:
        token = request.cookies.get(NOMBRE_COOKIE)

    if not token:
        return None

    datos = autenticacion.leer_token(token)
    if datos is None:
        return None

    return RepositorioUsuarios(sesion).por_id(int(datos["sub"]))


def usuario_obligatorio(
    usuario: Usuario | None = Depends(obtener_usuario_actual),
) -> Usuario:
    """Para rutas que exigen sesión (RF-03)."""
    if usuario is None:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión.")
    return usuario


def requiere_admin(
    usuario: Usuario = Depends(usuario_obligatorio),
) -> Usuario:
    """Para rutas solo de la coordinadora (RN-04)."""
    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="Esta acción es solo para administradores.")
    return usuario