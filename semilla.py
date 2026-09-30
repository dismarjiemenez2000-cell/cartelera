"""Datos iniciales: la cuenta de la coordinadora y películas de ejemplo.

Uso (desde la raíz del proyecto):
    python semilla.py

Idempotente: si el admin ya existe o ya hay películas, no duplica nada.
En PRODUCCIÓN lo corre el build de Render en cada deploy (ver fase 7);
a mano también se puede, apuntando la base de Neon desde una red que
permita el puerto 5432:

    # Git Bash / Linux / macOS
    DATABASE_URL="postgresql+psycopg2://usuario:clave@host/bd" python semilla.py

    # PowerShell
    $env:DATABASE_URL="postgresql+psycopg2://usuario:clave@host/bd"; python semilla.py
"""
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.database import SesionLocal, crear_tablas
from app.modelos import Pelicula, Usuario
from app.repositorios import RepositorioPeliculas, RepositorioUsuarios
from app.servicios import autenticacion

# Películas clásicas con tráilers oficiales en YouTube. Sin carátula a
# propósito: se muestra la imagen genérica y subir una real es parte del
# ejercicio desde el panel de administración.
PELICULAS_EJEMPLO = [
    {
        "titulo": "El Padrino",
        "anio": 1972,
        "sinopsis": "La saga de la familia Corleone y el ascenso de Michael, el hijo que nunca quiso pertenecer a los negocios de su padre.",
        "url_trailer": "https://www.youtube.com/embed/sY1S34973zA",
    },
    {
        "titulo": "Interestelar",
        "anio": 2014,
        "sinopsis": "Con la Tierra agonizando, un grupo de astronautas cruza un agujero negro en busca de un nuevo hogar para la humanidad.",
        "url_trailer": "https://www.youtube.com/embed/zSWdZVtXT7E",
    },
    {
        "titulo": "Coco",
        "anio": 2017,
        "sinopsis": "Miguel viaja por accidente a la Tierra de los Muertos y descubre la verdad sobre la historia de su familia.",
        "url_trailer": "https://www.youtube.com/embed/Ga6RYejo6Hk",
    },
    {
        "titulo": "Spider-Man: Un nuevo universo",
        "anio": 2018,
        "sinopsis": "Miles Morales descubre que no es el único Spider-Man cuando héroes de dimensiones paralelas llegan a la suya.",
        "url_trailer": "https://www.youtube.com/embed/g4Hbz2jLxvQ",
    },
]


def main() -> None:
    crear_tablas()

    with SesionLocal() as sesion:
        repo_usuarios = RepositorioUsuarios(sesion)

        if repo_usuarios.por_email(ADMIN_EMAIL) is None:
            repo_usuarios.crear(
                Usuario(
                    nombre="Macarena",
                    email=ADMIN_EMAIL,
                    password_hash=autenticacion.hashear(ADMIN_PASSWORD),
                    rol="admin",
                )
            )
            print(f"[+] Coordinadora creada: {ADMIN_EMAIL} (contraseña: {ADMIN_PASSWORD})")
        else:
            print("[=] La coordinadora ya existía")

        if RepositorioPeliculas(sesion).listar():
            print("[=] Ya hay películas en el catálogo, no agrego ejemplos")
        else:
            for datos in PELICULAS_EJEMPLO:
                sesion.add(Pelicula(**datos))
            sesion.commit()
            print(f"[+] {len(PELICULAS_EJEMPLO)} películas de ejemplo (sin carátula: súbelas desde el panel)")


if __name__ == "__main__":
    main()