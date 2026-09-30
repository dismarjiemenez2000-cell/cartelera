from app.database import SesionLocal, crear_tablas
from app.modelos import Usuario
from app.repositorios import RepositorioUsuarios
from app.servicios import autenticacion

crear_tablas()
with SesionLocal() as sesion:
    repo = RepositorioUsuarios(sesion)
    if repo.por_email("coordinadora@cineclub.cl") is None:
        repo.crear(Usuario(
            nombre="Arielys",
            email="coordinadora@cineclub.cl",
            password_hash=autenticacion.hashear("admin1234"),
            rol="admin",
        ))
        print("Coordinadora creada: coordinadora@cineclub.cl / admin1234")