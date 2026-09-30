"""Servicio de autenticación: hash, tokens JWT y registro (ADR-003).

La lógica de "quién es" y "qué puede hacer" vive aquí, no en las rutas.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.config import DIAS_TOKEN, SECRET_KEY
from app.modelos import Usuario
from app.repositorios import RepositorioUsuarios

ALGORITMO = "HS256"


# ---------- Contraseñas ----------

def hashear(contrasena: str) -> str:
    """Convierte una contraseña en su hash bcrypt.

    bcrypt incorpora la "sal" automáticamente: la misma contraseña produce un
    hash distinto cada vez (por eso no se puede "des-hashear", solo reintentar
    con checkpw).
    """
    return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar(contrasena: str, hash_almacenado: str) -> bool:
    return bcrypt.checkpw(contrasena.encode("utf-8"), hash_almacenado.encode("utf-8"))


# ---------- Tokens JWT ----------

def crear_token(usuario: Usuario) -> str:
    """Emite el carné: porta el id (sub) y el rol, firmados, con expiración."""
    datos = {
        "sub": str(usuario.id),
        "rol": usuario.rol,
        "exp": datetime.now(timezone.utc) + timedelta(days=DIAS_TOKEN),
    }
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITMO)


def leer_token(token: str) -> dict | None:
    """Devuelve los datos del token si la firma y la expiración son válidas."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
    except jwt.PyJWTError:
        return None  # token falsificado, malformado o vencido


# ---------- Casos de uso ----------

def registrar(sesion: Session, nombre: str, email: str, contrasena: str) -> Usuario:
    """Crea una cuenta (RF-01). Lanza ValueError con mensaje para el usuario."""
    nombre = nombre.strip()
    email = email.strip().lower()

    # Validaciones duplicadas a propósito: la frontera (esquemas, guía 5)
    # también valida, pero el servicio no confía en nadie (defensa en profundidad)
    if len(nombre) < 2:
        raise ValueError("El nombre debe tener al menos 2 caracteres.")
    if len(contrasena) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")

    repo = RepositorioUsuarios(sesion)
    if repo.por_email(email) is not None:
        raise ValueError("Ya existe una cuenta con ese email.")

    usuario = Usuario(nombre=nombre, email=email, password_hash=hashear(contrasena))
    return repo.crear(usuario)


def entrar(sesion: Session, email: str, contrasena: str) -> str:
    """Verifica credenciales y devuelve el token de sesión (RF-02).

    Mensaje genérico a propósito: no le decimos al atacante SI el email existe.
    """
    usuario = RepositorioUsuarios(sesion).por_email(email)
    if usuario is None or not verificar(contrasena, usuario.password_hash):
        raise ValueError("Email o contraseña incorrectos.")
    return crear_token(usuario)