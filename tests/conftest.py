import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from agrotechEFA2026.db import seed, session


@pytest.fixture
def claves(monkeypatch):
    """Base de datos en memoria con los datos de ejemplo; devuelve {sensor_id: api_key}."""
    motor = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(motor)
    with Session(motor) as s:
        claves = seed.sembrar(s, {"farmer": "a", "technician": "b"})
    monkeypatch.setattr(session, "_motor", motor)
    yield claves
    SQLModel.metadata.drop_all(motor)


@pytest.fixture
def motor(claves):
    """El motor de la base de datos de prueba, para los tests que guardan datos directamente."""
    return session._motor
