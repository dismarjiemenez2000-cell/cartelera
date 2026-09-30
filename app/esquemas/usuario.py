"""Esquemas Pydantic de usuarios (contrato: schemas UsuarioCrear, SolicitudSesion, UsuarioOut)."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    email: EmailStr
    contrasena: str = Field(min_length=8, max_length=100)


class SolicitudSesion(BaseModel):
    email: EmailStr
    contrasena: str


class UsuarioOut(BaseModel):
    """Un usuario visible en respuestas. El hash jamás aparece: no está declarado."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    rol: str  # 'socio' | 'admin' — enum del contrato