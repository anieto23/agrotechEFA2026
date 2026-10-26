"""Funciones de acceso a datos para la interfaz (B, C y E). Ver docs/contrato.md.

Todas reciben el id del usuario y solo devuelven o cambian lo que ese usuario puede ver.
Si los datos no son válidos lanzan ValueError y si no hay permiso PermissionError,
siempre con un mensaje en español listo para mostrar en pantalla.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, col, select

from .models import (
    ACCIONES_POR_TIPO,
    TIPOS_MEDIDA,
    TIPOS_PARCELA,
    Action,
    Alert,
    Crop,
    CropRange,
    Node,
    Parcel,
    ParcelViewer,
    Sensor,
    SensorData,
    User,
)
from .seguridad import generar_api_key, hash_api_key
from .session import sesion

LADO_MAXIMO_M = 5000.0  # 5 km: más grande ya no es una parcela, es un error al teclear
LIMITE_HISTORICO = 5000
DURACION_MAXIMA_MIN = 240


# Mismos nombres que el JSON de la API, para poder devolverlos tal cual
@dataclass
class EstadoSensor:
    sensor_id: int
    node_id: int
    node_name: str
    type: str
    unit: str
    value: Optional[float]
    timestamp: Optional[datetime]
    optimal_min: Optional[float]
    optimal_max: Optional[float]
    status: str  # low, ok, high, no_data o no_range


@dataclass
class CultivoConRangos:
    id: int
    name: str
    description: str
    ranges: list[dict] = field(default_factory=list)


# ---------- Reglas (sin base de datos, fáciles de probar) ----------

def evaluar_estado(valor: Optional[float], minimo: Optional[float], maximo: Optional[float]) -> str:
    """Compara una lectura con su rango. Sirve con solo uno de los dos límites."""
    if valor is None:
        return "no_data"
    if minimo is None and maximo is None:
        return "no_range"
    if minimo is not None and valor < minimo:
        return "low"
    if maximo is not None and valor > maximo:
        return "high"
    return "ok"


def _en_utc(fecha: datetime) -> datetime:
    # Una fecha sin zona horaria se entiende como UTC
    return fecha.replace(tzinfo=timezone.utc) if fecha.tzinfo is None else fecha.astimezone(timezone.utc)


def _texto(valor: str, que: str, maximo: int = 100) -> str:
    valor = (valor or "").strip()
    if not valor:
        raise ValueError(f"Falta {que}.")
    if len(valor) > maximo:
        raise ValueError(f"{que.capitalize()} no puede tener más de {maximo} caracteres.")
    return valor


def _medida(valor: float, que: str, maximo: float) -> float:
    if not 0 < valor <= maximo:
        raise ValueError(f"{que.capitalize()} debe estar entre 0 y {maximo:g} m.")
    return float(valor)


# ---------- Permisos ----------

def _usuario(s: Session, usuario_id: int) -> User:
    usuario = s.get(User, usuario_id)
    if usuario is None:
        raise PermissionError("Sesión no válida: vuelve a iniciar sesión.")
    return usuario


def _puede_ver(s: Session, usuario: User, parcela: Parcel) -> bool:
    if parcela.owner_id == usuario.id:
        return True
    return s.get(ParcelViewer, (parcela.id, usuario.id)) is not None


def _parcela_visible(s: Session, usuario_id: int, parcela_id: int) -> Parcel:
    usuario = _usuario(s, usuario_id)
    parcela = s.get(Parcel, parcela_id)
    if parcela is None:
        raise ValueError("La parcela no existe.")
    if not _puede_ver(s, usuario, parcela):
        raise PermissionError("No tienes acceso a esta parcela.")
    return parcela


def _parcela_editable(s: Session, usuario_id: int, parcela_id: int) -> Parcel:
    """Solo el agricultor dueño de la parcela puede cambiarla o dar órdenes."""
    parcela = _parcela_visible(s, usuario_id, parcela_id)
    usuario = s.get(User, usuario_id)
    if usuario.role != "farmer" or parcela.owner_id != usuario.id:
        raise PermissionError("Solo el agricultor dueño de la parcela puede hacer cambios.")
    return parcela


def _ids_parcelas_visibles(s: Session, usuario_id: int) -> list[int]:
    propias = s.exec(select(Parcel.id).where(Parcel.owner_id == usuario_id)).all()
    compartidas = s.exec(select(ParcelViewer.parcel_id).where(ParcelViewer.user_id == usuario_id)).all()
    return list(set(propias) | set(compartidas))


def limites_sensor(s: Session, sensor: Sensor, nodo: Node) -> tuple[Optional[float], Optional[float]]:
    """Umbrales del sensor; los que falten se toman del óptimo del cultivo del nodo."""
    rango = None
    if nodo.crop_id is not None:
        rango = s.exec(
            select(CropRange).where(CropRange.crop_id == nodo.crop_id, CropRange.type == sensor.type)
        ).first()
    minimo = sensor.threshold_low if sensor.threshold_low is not None else (rango.optimal_min if rango else None)
    maximo = sensor.threshold_high if sensor.threshold_high is not None else (rango.optimal_max if rango else None)
    return minimo, maximo


# ---------- Parcelas ----------

def listar_parcelas(usuario_id: int) -> list[Parcel]:
    with sesion() as s:
        _usuario(s, usuario_id)
        ids = _ids_parcelas_visibles(s, usuario_id)
        return list(s.exec(select(Parcel).where(col(Parcel.id).in_(ids)).order_by(Parcel.name)).all())


def obtener_parcela(usuario_id: int, parcela_id: int) -> Optional[Parcel]:
    """La parcela, o None si no existe o el usuario no puede verla."""
    with sesion() as s:
        try:
            return _parcela_visible(s, usuario_id, parcela_id)
        except (ValueError, PermissionError):
            return None


def crear_parcela(usuario_id: int, nombre: str, tipo: str, ancho_m: float, largo_m: float) -> Parcel:
    with sesion() as s:
        usuario = _usuario(s, usuario_id)
        if usuario.role != "farmer":
            raise PermissionError("Solo un agricultor puede crear parcelas.")
        if tipo not in TIPOS_PARCELA:
            raise ValueError("El tipo de parcela debe ser interior (indoor) o exterior (outdoor).")
        parcela = Parcel(
            owner_id=usuario.id,
            name=_texto(nombre, "el nombre"),
            kind=tipo,
            width_m=_medida(ancho_m, "el ancho", LADO_MAXIMO_M),
            length_m=_medida(largo_m, "el largo", LADO_MAXIMO_M),
        )
        s.add(parcela)
        s.commit()
        return parcela


# ---------- Nodos y sensores ----------

def _comprobar_posicion(parcela: Parcel, x_m: float, y_m: float) -> None:
    if not (0 <= x_m <= parcela.width_m and 0 <= y_m <= parcela.length_m):
        raise ValueError(
            f"La posición ({x_m:g}, {y_m:g}) m queda fuera de la parcela "
            f"({parcela.width_m:g} x {parcela.length_m:g} m)."
        )


def colocar_nodo(
    usuario_id: int,
    parcela_id: int,
    nombre: str,
    x_m: float,
    y_m: float,
    radio_m: float,
    cultivo_id: Optional[int] = None,
) -> tuple[Node, str]:
    """Coloca un aparato en el plano. Devuelve el nodo y su clave, que solo se muestra esta vez."""
    with sesion() as s:
        parcela = _parcela_editable(s, usuario_id, parcela_id)
        _comprobar_posicion(parcela, x_m, y_m)
        radio = _medida(radio_m, "el radio", max(parcela.width_m, parcela.length_m))
        if cultivo_id is not None and s.get(Crop, cultivo_id) is None:
            raise ValueError("El cultivo elegido no existe.")
        clave = generar_api_key()
        nodo = Node(
            parcel_id=parcela.id,
            name=_texto(nombre, "el nombre del aparato"),
            pos_x_m=float(x_m),
            pos_y_m=float(y_m),
            radius_m=radio,
            crop_id=cultivo_id,
            api_key_hash=hash_api_key(clave),
        )
        s.add(nodo)
        s.commit()
        return nodo, clave


def _nodo_editable(s: Session, usuario_id: int, nodo_id: int) -> tuple[Node, Parcel]:
    nodo = s.get(Node, nodo_id)
    if nodo is None:
        raise ValueError("El aparato no existe.")
    return nodo, _parcela_editable(s, usuario_id, nodo.parcel_id)


def mover_nodo(usuario_id: int, nodo_id: int, x_m: float, y_m: float) -> Node:
    with sesion() as s:
        nodo, parcela = _nodo_editable(s, usuario_id, nodo_id)
        _comprobar_posicion(parcela, x_m, y_m)
        nodo.pos_x_m, nodo.pos_y_m = float(x_m), float(y_m)
        s.add(nodo)
        s.commit()
        return nodo


def crear_sensor(
    usuario_id: int,
    nodo_id: int,
    tipo: str,
    umbral_bajo: Optional[float] = None,
    umbral_alto: Optional[float] = None,
) -> Sensor:
    with sesion() as s:
        nodo, _ = _nodo_editable(s, usuario_id, nodo_id)
        if tipo not in TIPOS_MEDIDA:
            raise ValueError(f"Tipo de medida no válido. Opciones: {', '.join(TIPOS_MEDIDA)}.")
        unidad, minimo, maximo = TIPOS_MEDIDA[tipo]
        for umbral in (umbral_bajo, umbral_alto):
            if umbral is not None and not minimo <= umbral <= maximo:
                raise ValueError(f"Los umbrales deben estar entre {minimo:g} y {maximo:g} {unidad}.")
        if umbral_bajo is not None and umbral_alto is not None and umbral_bajo >= umbral_alto:
            raise ValueError("El umbral bajo debe ser menor que el alto.")
        sensor = Sensor(node_id=nodo.id, type=tipo, unit=unidad, threshold_low=umbral_bajo, threshold_high=umbral_alto)
        s.add(sensor)
        s.commit()
        return sensor


# ---------- Lecturas ----------

def ultimas_lecturas(usuario_id: int, parcela_id: int) -> list[EstadoSensor]:
    """Última lectura de cada sensor activo de la parcela, comparada con su rango."""
    with sesion() as s:
        _parcela_visible(s, usuario_id, parcela_id)
        filas = s.exec(
            select(Sensor, Node)
            .join(Node, Sensor.node_id == Node.id)
            .where(Node.parcel_id == parcela_id, Sensor.active == True)  # noqa: E712 (SQL, no Python)
            .order_by(Node.id, Sensor.id)
        ).all()
        estados = []
        for sensor, nodo in filas:
            ultima = s.exec(
                select(SensorData)
                .where(SensorData.sensor_id == sensor.id)
                .order_by(col(SensorData.timestamp).desc())
                .limit(1)
            ).first()
            minimo, maximo = limites_sensor(s, sensor, nodo)
            valor = ultima.value if ultima else None
            estados.append(
                EstadoSensor(
                    sensor_id=sensor.id,
                    node_id=nodo.id,
                    node_name=nodo.name,
                    type=sensor.type,
                    unit=sensor.unit,
                    value=valor,
                    timestamp=ultima.timestamp if ultima else None,
                    optimal_min=minimo,
                    optimal_max=maximo,
                    status=evaluar_estado(valor, minimo, maximo),
                )
            )
        return estados


def historico(
    usuario_id: int, sensor_id: int, desde: datetime, hasta: datetime, limite: int = 500
) -> list[SensorData]:
    """Lecturas de un sensor entre dos fechas, de la más antigua a la más reciente."""
    if not 1 <= limite <= LIMITE_HISTORICO:
        raise ValueError(f"El límite debe estar entre 1 y {LIMITE_HISTORICO}.")
    desde, hasta = _en_utc(desde), _en_utc(hasta)
    if desde > hasta:
        raise ValueError("La fecha de inicio debe ser anterior a la de fin.")
    with sesion() as s:
        sensor = s.get(Sensor, sensor_id)
        if sensor is None:
            raise ValueError("El sensor no existe.")
        _parcela_visible(s, usuario_id, s.get(Node, sensor.node_id).parcel_id)
        return list(
            s.exec(
                select(SensorData)
                .where(SensorData.sensor_id == sensor_id, SensorData.timestamp >= desde, SensorData.timestamp <= hasta)
                .order_by(SensorData.timestamp)
                .limit(limite)
            ).all()
        )


# ---------- Cultivos ----------

def listar_cultivos() -> list[CultivoConRangos]:
    with sesion() as s:
        cultivos = []
        for cultivo in s.exec(select(Crop).order_by(Crop.name)):
            rangos = [
                {"type": r.type, "unit": TIPOS_MEDIDA[r.type][0], "optimal_min": r.optimal_min,
                 "optimal_max": r.optimal_max, "source": r.source}
                for r in s.exec(select(CropRange).where(CropRange.crop_id == cultivo.id))
            ]
            cultivos.append(CultivoConRangos(cultivo.id, cultivo.name, cultivo.description, rangos))
        return cultivos


# ---------- Alertas ----------

def alertas_pendientes(usuario_id: int) -> list[Alert]:
    """Alertas sin leer de las parcelas que ve el usuario, de la más reciente a la más antigua."""
    with sesion() as s:
        _usuario(s, usuario_id)
        ids = _ids_parcelas_visibles(s, usuario_id)
        return list(
            s.exec(
                select(Alert)
                .join(Sensor, Alert.sensor_id == Sensor.id)
                .join(Node, Sensor.node_id == Node.id)
                .where(col(Node.parcel_id).in_(ids), Alert.acknowledged == False)  # noqa: E712
                .order_by(col(Alert.timestamp).desc())
            ).all()
        )


def marcar_alerta_leida(usuario_id: int, alerta_id: int) -> None:
    with sesion() as s:
        alerta = s.get(Alert, alerta_id)
        if alerta is None:
            raise ValueError("La alerta no existe.")
        nodo = s.get(Node, s.get(Sensor, alerta.sensor_id).node_id)
        _parcela_editable(s, usuario_id, nodo.parcel_id)
        alerta.acknowledged = True
        s.add(alerta)
        s.commit()


# ---------- Acciones ----------

def crear_accion(usuario_id: int, parcela_id: int, tipo: str, duracion_min: Optional[int] = None) -> Action:
    """Orden para el aparato o el simulador (regar, ventilar...). Queda pendiente hasta que la ejecute."""
    with sesion() as s:
        parcela = _parcela_editable(s, usuario_id, parcela_id)
        permitidas = ACCIONES_POR_TIPO[parcela.kind]
        if tipo not in permitidas:
            donde = "interior" if parcela.kind == "indoor" else "exterior"
            raise ValueError(f"En una parcela de {donde} solo se puede: {', '.join(permitidas)}.")
        if duracion_min is not None and not 1 <= duracion_min <= DURACION_MAXIMA_MIN:
            raise ValueError(f"La duración debe estar entre 1 y {DURACION_MAXIMA_MIN} minutos.")
        accion = Action(parcel_id=parcela.id, user_id=usuario_id, type=tipo, duration_min=duracion_min)
        s.add(accion)
        s.commit()
        return accion
