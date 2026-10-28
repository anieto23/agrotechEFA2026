"""Funciones de acceso a datos para la interfaz (B, C y E). Ver docs/contrato.md.

Todas reciben el id del usuario y solo devuelven o cambian lo que ese usuario puede ver.
Si los datos no son válidos lanzan ValueError y si no hay permiso PermissionError,
siempre con un mensaje en español listo para mostrar en pantalla.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete
from sqlmodel import Session, col, func, select

from .models import (
    ACCIONES_POR_TIPO,
    FORMAS_PARCELA,
    TIPOS_MEDIDA,
    TIPOS_PARCELA,
    Action,
    Alert,
    Crop,
    CropRange,
    Parcel,
    ParcelViewer,
    Sector,
    Sensor,
    SensorData,
    User,
)
from .seguridad import generar_api_key, hash_api_key
from .session import sesion

CONTORNO_MAX_VERTICES = 100
AREA_MAXIMA_M2 = 10_000_000.0  # 1000 ha: más grande ya no es una parcela, es un error al teclear
LADO_MINIMO_PCT = 2.0  # por debajo, el sector ya no se ve ni se puede pulsar en el plano
LIMITE_HISTORICO = 5000
DURACION_MAXIMA_MIN = 240


# Mismos nombres que el JSON de la API, para poder devolverlos tal cual
@dataclass
class EstadoSensor:
    sensor_id: int
    sector_id: int
    sector_name: str
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


def _orientacion(a, b, c) -> float:
    # > 0 si c queda a la izquierda de a→b, < 0 a la derecha, 0 si están en línea
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _se_tocan(a, b, c, d) -> bool:
    """Si los segmentos a-b y c-d se cruzan o se tocan."""
    o1, o2, o3, o4 = _orientacion(a, b, c), _orientacion(a, b, d), _orientacion(c, d, a), _orientacion(c, d, b)
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True

    def sobre(p, q, r):  # r, en línea con p-q, cae dentro del segmento
        return min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])

    return (o1 == 0 and sobre(a, b, c)) or (o2 == 0 and sobre(a, b, d)) or (
        o3 == 0 and sobre(c, d, a)) or (o4 == 0 and sobre(c, d, b))


def validar_contorno(vertices) -> list[list[float]]:
    """Comprueba un contorno dibujado ([[x, y], ...] en % del plano) y lo devuelve listo para guardar."""
    try:
        puntos = [(float(x), float(y)) for x, y in vertices or []]
    except (TypeError, ValueError):
        raise ValueError("Cada vértice tiene que ser un par de números (x, y).") from None
    if len(puntos) < 3:
        raise ValueError("Añade al menos tres vértices para cerrar el contorno.")
    if len(puntos) > CONTORNO_MAX_VERTICES:
        raise ValueError(f"El contorno no puede tener más de {CONTORNO_MAX_VERTICES} vértices.")
    if any(not (0 <= x <= 100 and 0 <= y <= 100) for x, y in puntos):
        raise ValueError("Los vértices deben estar dentro del plano (0 a 100 %).")
    if len(set(puntos)) != len(puntos):
        raise ValueError("El contorno no puede repetir vértices.")
    lados = list(zip(puntos, puntos[1:] + puntos[:1]))
    if sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in lados) == 0:
        raise ValueError("Los vértices deben formar una superficie.")
    # Los lados vecinos comparten un vértice; solo se miran los que no se tocan por los extremos
    for i in range(len(lados)):
        for j in range(i + 2, len(lados)):
            if i == 0 and j == len(lados) - 1:
                continue
            if _se_tocan(*lados[i], *lados[j]):
                raise ValueError("El contorno no puede cruzarse a sí mismo.")
    return [[x, y] for x, y in puntos]


def _en_utc(fecha: datetime) -> datetime:
    # Una fecha sin zona horaria se entiende como UTC
    return fecha.replace(tzinfo=timezone.utc) if fecha.tzinfo is None else fecha.astimezone(timezone.utc)


def _texto(valor: str, que: str, maximo: int = 80) -> str:
    valor = (valor or "").strip()
    if not valor:
        raise ValueError(f"Falta {que}.")
    if len(valor) > maximo:
        raise ValueError(f"{que.capitalize()} no puede tener más de {maximo} caracteres.")
    return valor


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


def _sector_editable(s: Session, usuario_id: int, sector_id: int) -> tuple[Sector, Parcel]:
    sector = s.get(Sector, sector_id)
    if sector is None:
        raise ValueError("El sector no existe.")
    return sector, _parcela_editable(s, usuario_id, sector.parcel_id)


def _ids_parcelas_visibles(s: Session, usuario_id: int) -> list[int]:
    propias = s.exec(select(Parcel.id).where(Parcel.owner_id == usuario_id)).all()
    compartidas = s.exec(select(ParcelViewer.parcel_id).where(ParcelViewer.user_id == usuario_id)).all()
    return list(set(propias) | set(compartidas))


def limites_sensor(s: Session, sensor: Sensor, sector: Sector) -> tuple[Optional[float], Optional[float]]:
    """Umbrales del sensor; los que falten se toman del óptimo del cultivo del sector."""
    rango = None
    if sector.crop_id is not None:
        rango = s.exec(
            select(CropRange).where(CropRange.crop_id == sector.crop_id, CropRange.type == sensor.type)
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


def crear_parcela(
    usuario_id: int, nombre: str, tipo: str, area_m2: float, forma: str, contorno: Optional[list] = None
) -> Parcel:
    """Crea la parcela con un primer sector que la ocupa entera, como hace el panel.

    `contorno` ([[x, y], ...] en % del plano) es obligatorio si la forma es «drawn» y no se usa con las demás.
    """
    with sesion() as s:
        usuario = _usuario(s, usuario_id)
        if usuario.role != "farmer":
            raise PermissionError("Solo un agricultor puede crear parcelas.")
        if tipo not in TIPOS_PARCELA:
            raise ValueError("Elige si la parcela es de interior (invernadero) o de exterior.")
        if forma not in FORMAS_PARCELA:
            raise ValueError("Selecciona una forma válida.")
        if not 0 < area_m2 <= AREA_MAXIMA_M2:
            raise ValueError(f"La superficie debe estar entre 0 y {AREA_MAXIMA_M2:,.0f} m².".replace(",", "."))
        if forma == "drawn":
            contorno = validar_contorno(contorno)
        elif contorno is not None:
            raise ValueError("Solo una parcela dibujada lleva contorno.")
        parcela = Parcel(
            owner_id=usuario.id,
            name=_texto(nombre, "el nombre"),
            kind=tipo,
            area_m2=float(area_m2),
            shape=forma,
            outline=contorno,
        )
        s.add(parcela)
        s.flush()  # para tener el id de la parcela
        s.add(Sector(parcel_id=parcela.id, name="Sector 1", api_key_hash=hash_api_key(generar_api_key())))
        s.commit()
        return parcela


def eliminar_parcela(usuario_id: int, parcela_id: int) -> None:
    """Borra la parcela con todo lo suyo: sectores, sensores, lecturas, alertas y acciones."""
    with sesion() as s:
        _parcela_editable(s, usuario_id, parcela_id)
        sectores = select(Sector.id).where(Sector.parcel_id == parcela_id)
        sensores = select(Sensor.id).where(col(Sensor.sector_id).in_(sectores))
        # De las hojas a la raíz, para no dejar filas que apunten a algo borrado
        s.exec(delete(Alert).where(col(Alert.sensor_id).in_(sensores)))
        s.exec(delete(SensorData).where(col(SensorData.sensor_id).in_(sensores)))
        s.exec(delete(Sensor).where(col(Sensor.sector_id).in_(sectores)))
        s.exec(delete(Sector).where(Sector.parcel_id == parcela_id))
        s.exec(delete(Action).where(Action.parcel_id == parcela_id))
        s.exec(delete(ParcelViewer).where(ParcelViewer.parcel_id == parcela_id))
        s.exec(delete(Parcel).where(Parcel.id == parcela_id))
        s.commit()


# ---------- Sectores y sensores ----------

def listar_sectores(usuario_id: int, parcela_id: int) -> list[Sector]:
    with sesion() as s:
        _parcela_visible(s, usuario_id, parcela_id)
        return list(s.exec(select(Sector).where(Sector.parcel_id == parcela_id).order_by(Sector.id)).all())


def dividir_sector(usuario_id: int, sector_id: int, orientacion: str) -> tuple[Sector, Sector]:
    """Parte un sector por la mitad. El nuevo conserva el cultivo pero empieza sin sensores."""
    if orientacion not in ("vertical", "horizontal"):
        raise ValueError("La división debe ser vertical u horizontal.")
    with sesion() as s:
        sector, parcela = _sector_editable(s, usuario_id, sector_id)
        lado = "width_pct" if orientacion == "vertical" else "height_pct"
        mitad = getattr(sector, lado) / 2
        if mitad < LADO_MINIMO_PCT:
            raise ValueError("El sector es demasiado pequeño para dividirlo otra vez.")
        cuantos = s.exec(select(func.count()).select_from(Sector).where(Sector.parcel_id == parcela.id)).one()
        nuevo = Sector(
            parcel_id=parcela.id,
            name=f"Sector {cuantos + 1}",
            crop_id=sector.crop_id,
            left_pct=sector.left_pct + (mitad if orientacion == "vertical" else 0),
            top_pct=sector.top_pct + (mitad if orientacion == "horizontal" else 0),
            width_pct=mitad if orientacion == "vertical" else sector.width_pct,
            height_pct=mitad if orientacion == "horizontal" else sector.height_pct,
            api_key_hash=hash_api_key(generar_api_key()),
        )
        setattr(sector, lado, mitad)
        s.add_all([sector, nuevo])
        s.commit()
        return sector, nuevo


def cambiar_cultivo(usuario_id: int, sector_id: int, cultivo_id: Optional[int]) -> Sector:
    """Asigna un cultivo al sector; None lo deja «sin cultivo»."""
    with sesion() as s:
        sector, _ = _sector_editable(s, usuario_id, sector_id)
        if cultivo_id is not None and s.get(Crop, cultivo_id) is None:
            raise ValueError("El cultivo elegido no existe.")
        sector.crop_id = cultivo_id
        s.add(sector)
        s.commit()
        return sector


def generar_clave_sector(usuario_id: int, sector_id: int) -> str:
    """Nueva clave para el aparato del sector. Se muestra una sola vez; la anterior deja de valer."""
    with sesion() as s:
        sector, _ = _sector_editable(s, usuario_id, sector_id)
        clave = generar_api_key()
        sector.api_key_hash = hash_api_key(clave)
        s.add(sector)
        s.commit()
        return clave


def crear_sensor(
    usuario_id: int,
    sector_id: int,
    tipo: str,
    umbral_bajo: Optional[float] = None,
    umbral_alto: Optional[float] = None,
) -> Sensor:
    with sesion() as s:
        sector, _ = _sector_editable(s, usuario_id, sector_id)
        if tipo not in TIPOS_MEDIDA:
            raise ValueError(f"Tipo de medida no válido. Opciones: {', '.join(TIPOS_MEDIDA)}.")
        if s.exec(select(Sensor).where(Sensor.sector_id == sector.id, Sensor.type == tipo)).first():
            raise ValueError("Ese sector ya tiene este tipo de sensor.")
        unidad, minimo, maximo = TIPOS_MEDIDA[tipo]
        for umbral in (umbral_bajo, umbral_alto):
            if umbral is not None and not minimo <= umbral <= maximo:
                raise ValueError(f"Los umbrales deben estar entre {minimo:g} y {maximo:g} {unidad}.")
        if umbral_bajo is not None and umbral_alto is not None and umbral_bajo >= umbral_alto:
            raise ValueError("El umbral bajo debe ser menor que el alto.")
        sensor = Sensor(sector_id=sector.id, type=tipo, unit=unidad, threshold_low=umbral_bajo, threshold_high=umbral_alto)
        s.add(sensor)
        s.commit()
        return sensor


# ---------- Lecturas ----------

def ultimas_lecturas(usuario_id: int, parcela_id: int) -> list[EstadoSensor]:
    """Última lectura de cada sensor activo de la parcela, comparada con su rango."""
    with sesion() as s:
        _parcela_visible(s, usuario_id, parcela_id)
        filas = s.exec(
            select(Sensor, Sector)
            .join(Sector, Sensor.sector_id == Sector.id)
            .where(Sector.parcel_id == parcela_id, Sensor.active == True)  # noqa: E712 (SQL, no Python)
            .order_by(Sector.id, Sensor.id)
        ).all()
        estados = []
        for sensor, sector in filas:
            ultima = s.exec(
                select(SensorData)
                .where(SensorData.sensor_id == sensor.id)
                .order_by(col(SensorData.timestamp).desc())
                .limit(1)
            ).first()
            minimo, maximo = limites_sensor(s, sensor, sector)
            valor = ultima.value if ultima else None
            estados.append(
                EstadoSensor(
                    sensor_id=sensor.id,
                    sector_id=sector.id,
                    sector_name=sector.name,
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
        _parcela_visible(s, usuario_id, s.get(Sector, sensor.sector_id).parcel_id)
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
                .join(Sector, Sensor.sector_id == Sector.id)
                .where(col(Sector.parcel_id).in_(ids), Alert.acknowledged == False)  # noqa: E712
                .order_by(col(Alert.timestamp).desc())
            ).all()
        )


def marcar_alerta_leida(usuario_id: int, alerta_id: int) -> None:
    with sesion() as s:
        alerta = s.get(Alert, alerta_id)
        if alerta is None:
            raise ValueError("La alerta no existe.")
        sector = s.get(Sector, s.get(Sensor, alerta.sensor_id).sector_id)
        _parcela_editable(s, usuario_id, sector.parcel_id)
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
