"""Tablas de la base de datos, tal como están en docs/contrato.md.

Las tablas no validan rangos al crearse (SQLModel no lo hace con table=True):
las comprobaciones van en las funciones que guardan datos.

Nombres de tablas y columnas en inglés (como las bases y el JSON de la API);
el resto del código en español.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

# Tipo de medida -> (unidad, mínimo válido, máximo válido). Mismos valores que el simulador.
TIPOS_MEDIDA = {
    "temperature": ("ºC", -10.0, 50.0),
    "air_humidity": ("%", 0.0, 100.0),
    "soil_moisture": ("%", 0.0, 100.0),
    "light": ("lx", 0.0, 120000.0),
}

ROLES = ("farmer", "technician")
TIPOS_PARCELA = ("indoor", "outdoor")

# En exterior no se puede ventilar, calentar ni nebulizar: solo regar y sombrear.
ACCIONES_POR_TIPO = {
    "indoor": ("irrigation", "shading", "ventilation", "heating", "misting"),
    "outdoor": ("irrigation", "shading"),
}


def ahora_utc() -> datetime:
    """Fecha y hora actual en UTC. SQLModel exige fechas con zona horaria."""
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    role: str = "farmer"
    created_at: datetime = Field(default_factory=ahora_utc)


class Parcel(SQLModel, table=True):
    __tablename__ = "parcels"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    name: str
    kind: str = "outdoor"
    width_m: float
    length_m: float
    location: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    created_at: datetime = Field(default_factory=ahora_utc)

    nodes: list["Node"] = Relationship(back_populates="parcel")


class ParcelViewer(SQLModel, table=True):
    """Técnicos que pueden ver una parcela que no es suya."""

    __tablename__ = "parcel_viewers"

    parcel_id: int = Field(foreign_key="parcels.id", primary_key=True)
    user_id: int = Field(foreign_key="users.id", primary_key=True)


class Crop(SQLModel, table=True):
    __tablename__ = "crops"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str = ""

    ranges: list["CropRange"] = Relationship(back_populates="crop")


class CropRange(SQLModel, table=True):
    """Rango óptimo de una magnitud para un cultivo. `source` dice de dónde sale el dato."""

    __tablename__ = "crop_ranges"
    __table_args__ = (UniqueConstraint("crop_id", "type"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    crop_id: int = Field(foreign_key="crops.id")
    type: str
    optimal_min: float
    optimal_max: float
    source: str

    crop: Optional[Crop] = Relationship(back_populates="ranges")


class Node(SQLModel, table=True):
    """Aparato colocado en el plano de la parcela; agrupa varios sensores."""

    __tablename__ = "nodes"

    id: Optional[int] = Field(default=None, primary_key=True)
    parcel_id: int = Field(foreign_key="parcels.id", index=True)
    name: str
    crop_id: Optional[int] = Field(default=None, foreign_key="crops.id")
    # Metros desde la esquina superior izquierda de la parcela
    pos_x_m: float
    pos_y_m: float
    radius_m: float = 1.0
    api_key_hash: str
    active: bool = True

    parcel: Optional[Parcel] = Relationship(back_populates="nodes")
    sensors: list["Sensor"] = Relationship(back_populates="node")


class Sensor(SQLModel, table=True):
    __tablename__ = "sensors"

    id: Optional[int] = Field(default=None, primary_key=True)
    node_id: int = Field(foreign_key="nodes.id", index=True)
    type: str
    unit: str
    description: str = ""
    # Si están vacíos se usan los óptimos del cultivo del nodo
    threshold_low: Optional[float] = None
    threshold_high: Optional[float] = None
    active: bool = True

    node: Optional[Node] = Relationship(back_populates="sensors")


class SensorData(SQLModel, table=True):
    __tablename__ = "sensor_data"
    __table_args__ = (Index("ix_sensor_data_sensor_tiempo", "sensor_id", "timestamp"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_id: int = Field(foreign_key="sensors.id")
    timestamp: datetime
    value: float
    raw: Optional[str] = None


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"

    id: Optional[int] = Field(default=None, primary_key=True)
    sensor_id: int = Field(foreign_key="sensors.id", index=True)
    timestamp: datetime = Field(default_factory=ahora_utc)
    type: str  # "LOW" o "HIGH"
    message: str
    acknowledged: bool = False


class Action(SQLModel, table=True):
    """Orden enviada desde la app (regar, ventilar...) que ejecuta el aparato o el simulador."""

    __tablename__ = "actions"

    id: Optional[int] = Field(default=None, primary_key=True)
    parcel_id: int = Field(foreign_key="parcels.id", index=True)
    user_id: int = Field(foreign_key="users.id")
    type: str
    duration_min: Optional[int] = None
    status: str = "pending"  # pending, done o failed
    created_at: datetime = Field(default_factory=ahora_utc)
    done_at: Optional[datetime] = None
