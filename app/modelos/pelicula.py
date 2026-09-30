"""Tabla de películas (diseño §2.2)."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Pelicula(Base):
    __tablename__ = "peliculas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(120), index=True)
    anio: Mapped[int] = mapped_column(Integer)
    sinopsis: Mapped[str] = mapped_column(Text, default="")
    # Ya normalizada a formato embed (RN-03); la guía 4 hará la conversión
    url_trailer: Mapped[str] = mapped_column(String(300), default="")
    # Nombre del archivo en uploads/ (ADR-004); vacía → imagen genérica (RN-05)
    ruta_caratula: Mapped[str | None] = mapped_column(String(300), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Si se elimina una película, sus calificaciones se van en cascada (HU-07)
    calificaciones = relationship(
        "Calificacion", back_populates="pelicula", cascade="all, delete-orphan"
    )