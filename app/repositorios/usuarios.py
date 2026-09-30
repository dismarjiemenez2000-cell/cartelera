"""Repositorio de usuarios: SOLO acceso a datos, sin lógica de negocio (ADR-001)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modelos import Usuario


class RepositorioUsuarios:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def por_id(self, usuario_id: int) -> Usuario | None:
        return self.sesion.get(Usuario, usuario_id)

    def por_email(self, email: str) -> Usuario | None:
        consulta = select(Usuario).where(Usuario.email == email.lower().strip())
        return self.sesion.scalars(consulta).first()

    def crear(self, usuario: Usuario) -> Usuario:
        self.sesion.add(usuario)
        self.sesion.commit()
        self.sesion.refresh(usuario)
        return usuario