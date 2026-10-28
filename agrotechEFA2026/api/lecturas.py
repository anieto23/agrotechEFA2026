"""POST /api/sensors/{sensor_id}/data: entrada de lecturas (cabecera X-API-Key)."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from ..db.lecturas import ClaveIncorrecta, NoEncontrado, guardar_lectura

router = APIRouter(tags=["lecturas"])


class LecturaEntrada(BaseModel):
    """Mismo formato que envía scripts/gen_sample_data.py. Solo `value` es obligatorio."""

    value: float
    timestamp: Optional[datetime] = None
    sensor_id: Optional[int] = None
    type: Optional[str] = None
    unit: Optional[str] = None


class AlertaSalida(BaseModel):
    type: str
    message: str


class LecturaSalida(BaseModel):
    id: int
    sensor_id: int
    timestamp: datetime
    value: float
    alert: Optional[AlertaSalida]


@router.post("/sensors/{sensor_id}/data", status_code=201, response_model=LecturaSalida)
def recibir_lectura(
    sensor_id: int,
    lectura: LecturaEntrada,
    x_api_key: str = Header(default="", description="Clave del aparato del sector al que pertenece el sensor"),
) -> LecturaSalida:
    if lectura.sensor_id is not None and lectura.sensor_id != sensor_id:
        raise HTTPException(422, "El sensor_id del cuerpo no coincide con el de la dirección.")
    try:
        resultado = guardar_lectura(
            sensor_id, x_api_key, lectura.value, lectura.timestamp, lectura.type, lectura.unit
        )
    except NoEncontrado as error:
        raise HTTPException(404, str(error))
    except ClaveIncorrecta as error:
        raise HTTPException(401, str(error))
    except ValueError as error:
        raise HTTPException(422, str(error))

    guardada, alerta = resultado.lectura, resultado.alerta
    return LecturaSalida(
        id=guardada.id,
        sensor_id=guardada.sensor_id,
        timestamp=guardada.timestamp,
        value=guardada.value,
        alert=AlertaSalida(type=alerta.type, message=alerta.message) if alerta else None,
    )
