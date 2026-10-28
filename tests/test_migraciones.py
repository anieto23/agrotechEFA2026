import shutil

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine, select

from agrotechEFA2026.db import migrar, seed
from agrotechEFA2026.db.migrar import BaseDeDatosAntigua, actualizar_bd, configuracion
from agrotechEFA2026.db.models import SensorData, ahora_utc


@pytest.fixture
def motor(tmp_path):
    # Archivo de verdad (no en memoria), como agrotech.db
    return create_engine(f"sqlite:///{tmp_path / 'prueba.db'}")


def _cabeza(motor) -> str:
    """La última receta (la revisión a la que llega una base al día)."""
    return ScriptDirectory.from_config(configuracion(motor)).get_current_head()


def test_las_migraciones_crean_lo_mismo_que_models(motor):
    """Si falla: alguien cambió models.py sin crear su migración.

    Solución: python -m agrotechEFA2026.db.migrar nueva "qué has cambiado"
    """
    actualizar_bd(motor)
    with motor.connect() as conexion:
        diferencias = compare_metadata(MigrationContext.configure(conexion), SQLModel.metadata)
    assert diferencias == []


def test_una_sola_linea_de_migraciones(motor):
    """Si falla: dos personas crearon una migración a la vez. Hay que unirlas (alembic merge)."""
    assert len(ScriptDirectory.from_config(configuracion(motor)).get_heads()) == 1


def test_actualizar_dos_veces_no_pierde_datos(motor):
    actualizar_bd(motor)
    with Session(motor) as s:
        seed.sembrar(s, {"farmer": "a", "technician": "b"})
        s.add(SensorData(sensor_id=1, timestamp=ahora_utc(), value=21.5))
        s.commit()
    actualizar_bd(motor)  # como al arrancar la app otra vez
    with Session(motor) as s:
        assert len(s.exec(select(SensorData)).all()) == 1


def test_adopta_una_base_creada_antes_de_las_migraciones(motor):
    # Así estaban las agrotech.db del equipo: las tablas de la 0001, creadas con create_all
    # y sin alembic_version
    cfg = configuracion(motor)
    with motor.begin() as conexion:
        cfg.attributes["connection"] = conexion
        command.upgrade(cfg, migrar.PRIMERA_REVISION)
        conexion.execute(text("drop table alembic_version"))
        conexion.execute(text("insert into users (username, password_hash, role, created_at) "
                              "values ('ana', 'x', 'farmer', '2026-10-28')"))
    actualizar_bd(motor)
    with motor.connect() as conexion:
        assert conexion.execute(text("select version_num from alembic_version")).scalar() == _cabeza(motor)
        assert conexion.execute(text("select username from users")).scalar() == "ana"  # datos intactos


def test_unir_dos_migraciones_creadas_a_la_vez(motor, tmp_path, monkeypatch):
    # Copia de las recetas con dos nuevas hechas por dos personas a la vez
    carpeta = tmp_path / "migrations"
    shutil.copytree(migrar.CARPETA, carpeta, ignore=shutil.ignore_patterns("__pycache__"))
    cabeza = _cabeza(motor)
    for rev in ("nueva_a", "nueva_b"):
        (carpeta / "versions" / f"{rev}_prueba.py").write_text(
            f'revision = "{rev}"\ndown_revision = "{cabeza}"\nbranch_labels = None\ndepends_on = None\n\n\n'
            "def upgrade():\n    pass\n\n\ndef downgrade():\n    pass\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(migrar, "CARPETA", carpeta)
    assert len(ScriptDirectory.from_config(configuracion(motor)).get_heads()) == 2
    migrar.unir_migraciones(motor)
    assert len(ScriptDirectory.from_config(configuracion(motor)).get_heads()) == 1
    actualizar_bd(motor)  # y se puede aplicar todo


def test_base_anterior_a_los_sectores_da_un_error_claro(motor):
    with motor.begin() as conexion:
        conexion.execute(text("create table nodes (id integer primary key)"))
    with pytest.raises(BaseDeDatosAntigua, match="Bórrala"):
        actualizar_bd(motor)
    assert "parcels" not in inspect(motor).get_table_names()  # no ha tocado nada
