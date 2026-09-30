"""Tabla de usuarios (diseño §2.2): socios y la coordinadora."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    # unique=True: la base impide cuentas duplicadas (RF-01)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    # Nunca la contraseña en texto plano (RNF-01): aquí vive su hash bcrypt
    password_hash: Mapped[str] = mapped_column(String(200))
    # Dos roles alcanzan (ADR-003): 'socio' califica, 'admin' además gestiona
    rol: Mapped[str] = mapped_column(String(20), default="socio")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Si se elimina un usuario, sus calificaciones se van con él
    calificaciones = relationship(
        "Calificacion", back_populates="usuario", cascade="all, delete-orphan"
    )