"""Conexión a la base de datos.

Por defecto SQLite en `agrotech.db` (ignorado por git). Para usar MySQL/MariaDB basta con
definir AGROTECH_DB_URL, p. ej. `mysql+pymysql://usuario:clave@host/agrotech`.
"""
import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from . import models  # noqa: F401  (registra las tablas en SQLModel.metadata)

URL_POR_DEFECTO = "sqlite:///agrotech.db"

_motor: Engine | None = None


def crear_motor(url: str | None = None) -> Engine:
    url = url or os.environ.get("AGROTECH_DB_URL", URL_POR_DEFECTO)
    # SQLite solo deja usar la conexión desde el hilo que la creó, y Reflex usa varios
    argumentos = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=argumentos)


def obtener_motor() -> Engine:
    """Motor compartido por toda la app; se crea la primera vez que se pide."""
    global _motor
    if _motor is None:
        _motor = crear_motor()
    return _motor


def crear_tablas(motor: Engine | None = None) -> None:
    """Crea las tablas que falten. No cambia las que ya existen (para eso, migraciones)."""
    SQLModel.metadata.create_all(motor or obtener_motor())


@contextmanager
def sesion(motor: Engine | None = None) -> Iterator[Session]:
    """Abre una sesión corta: `with sesion() as s: ...`."""
    with Session(motor or obtener_motor()) as s:
        yield s
