"""Migraciones: cambiar las tablas sin perder los datos (con Alembic).

Uso (desde la raíz del repo):
    python -m agrotechEFA2026.db.migrar                         # pone tu agrotech.db al día
    python -m agrotechEFA2026.db.migrar nueva "añade X a Y"     # tras cambiar models.py
    python -m agrotechEFA2026.db.migrar unir                    # si dos personas crearon una a la vez

Las «recetas» de cambios están en migrations/versions/ y se suben a GitHub con el código.
La app aplica las que falten al arrancar. La configuración no va en un alembic.ini en la
raíz porque ese nombre lo usa Reflex para su propio sistema de migraciones.
"""
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from .session import obtener_motor

CARPETA = Path(__file__).resolve().parents[2] / "migrations"
PRIMERA_REVISION = "0001"


class BaseDeDatosAntigua(RuntimeError):
    """La base de datos es de antes de las migraciones y no se puede adoptar."""


def configuracion(motor: Engine) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(CARPETA))
    # Alembic trata «%» como variable de su configuración: hay que doblarlo
    cfg.set_main_option("sqlalchemy.url", motor.url.render_as_string(hide_password=False).replace("%", "%%"))
    return cfg


def _adoptar_si_hace_falta(cfg: Config, conexion) -> None:
    """Una base creada antes de las migraciones (con create_all) se marca como revisión 0001.

    Solo si ya tiene las tablas de esa revisión (sectores). Si es más antigua (nodos),
    no se puede saber qué le falta y es mejor recrearla: son datos de prueba.
    """
    tablas = set(inspect(conexion).get_table_names())
    if not tablas or "alembic_version" in tablas:
        return
    if "sectors" not in tablas:
        raise BaseDeDatosAntigua(
            "Tu agrotech.db es de una versión antigua (antes de los sectores). "
            "Bórrala y créala otra vez con: python -m agrotechEFA2026.db.seed"
        )
    cfg.attributes["connection"] = conexion
    command.stamp(cfg, PRIMERA_REVISION)


def actualizar_bd(motor: Engine | None = None) -> None:
    """Aplica las migraciones que falten. No borra datos."""
    motor = motor or obtener_motor()
    cfg = configuracion(motor)
    with motor.begin() as conexion:
        _adoptar_si_hace_falta(cfg, conexion)
        cfg.attributes["connection"] = conexion
        command.upgrade(cfg, "head")


def nueva_migracion(mensaje: str, motor: Engine | None = None) -> None:
    """Genera una receta comparando models.py con la base de datos (que debe estar al día)."""
    motor = motor or obtener_motor()
    cfg = configuracion(motor)
    actuales = list(ScriptDirectory.from_config(cfg).walk_revisions())
    numero = f"{len(actuales) + 1:04d}"  # 0001, 0002...: más fácil de leer que un código al azar
    with motor.begin() as conexion:
        cfg.attributes["connection"] = conexion
        command.revision(cfg, message=mensaje, autogenerate=True, rev_id=numero)
    print(f"Receta {numero} creada en migrations/versions/. Revísala antes de subirla.")


def unir_migraciones(motor: Engine | None = None) -> None:
    """Junta dos migraciones creadas a la vez (dos «cabezas») en una sola línea."""
    cfg = configuracion(motor or obtener_motor())
    cabezas = ScriptDirectory.from_config(cfg).get_heads()
    if len(cabezas) < 2:
        print("No hay nada que unir: solo hay una línea de migraciones.")
        return
    numero = f"{len(list(ScriptDirectory.from_config(cfg).walk_revisions())) + 1:04d}"
    command.merge(cfg, cabezas, message="une " + " y ".join(cabezas), rev_id=numero)
    print(f"Receta {numero} creada: une {', '.join(cabezas)}.")


def main(argumentos: list[str]) -> None:
    if not argumentos:
        actualizar_bd()
        print("Base de datos al día.")
    elif argumentos[0] == "nueva" and len(argumentos) == 2:
        actualizar_bd()
        nueva_migracion(argumentos[1])
    elif argumentos == ["unir"]:
        unir_migraciones()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
