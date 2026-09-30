"""Tabla de calificaciones (diseño §2.2, ADR-005)."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Calificacion(Base):
    __tablename__ = "calificaciones"

    # RN-01: la BASE DE DATOS impide dos votos del mismo socio a la misma
    # película, aunque el código tenga un bug (diseño §2.3.1, ADR-005)
    __table_args__ = (
        UniqueConstraint("usuario_id", "pelicula_id", name="uq_usuario_pelicula"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    pelicula_id: Mapped[int] = mapped_column(ForeignKey("peliculas.id"))
    estrellas: Mapped[int] = mapped_column(Integer)  # 1–5, se valida en la frontera (RN-02)

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    usuario = relationship("Usuario", back_populates="calificaciones")
    pelicula = relationship("Pelicula", back_populates="calificaciones")
    #mapped = este tipo de datos esta mapeado a un tipo whatever..