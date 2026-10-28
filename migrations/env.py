"""Entorno de Alembic. No se lanza a mano: usa `python -m agrotechEFA2026.db.migrar`."""
from alembic import context
from sqlalchemy import create_engine
from sqlmodel import SQLModel

from agrotechEFA2026.db import models  # noqa: F401  (registra las tablas en SQLModel.metadata)

config = context.config


def _configurar(conexion) -> None:
    context.configure(
        connection=conexion,
        target_metadata=SQLModel.metadata,
        render_as_batch=True,  # SQLite no sabe cambiar columnas: Alembic copia la tabla por dentro
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# migrar.py pasa la conexión ya abierta (así funciona también con bases en memoria)
conexion = config.attributes.get("connection")
if conexion is not None:
    _configurar(conexion)
else:
    with create_engine(config.get_main_option("sqlalchemy.url")).connect() as nueva:
        _configurar(nueva)
