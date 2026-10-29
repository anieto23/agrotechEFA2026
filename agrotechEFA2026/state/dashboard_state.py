import math
import re

import reflex as rx

from ..components import colors

FORMAS = {
    "rectangulo": "Rectángulo",
    "cuadrado": "Cuadrado",
    "circulo": "Círculo",
    "poligono": "Polígono",
    "dibujada": "Dibujada",
}

PUNTOS_CUADRICULA = (7, 21, 36, 50, 64, 79, 93)
FORMAS_POLIGONO = {
    "poligono": [(18, 0), (83, 8), (100, 42), (76, 100), (15, 92), (0, 35)],
    "cuadrado": [(16, 0), (84, 0), (84, 100), (16, 100)],
    "rectangulo": [(0, 0), (100, 0), (100, 100), (0, 100)],
}

CULTIVOS = {
    "Sin cultivo": "🌱❌",
    "Tomate": "🍅",
    "Aguacate": "🥑",
    "Mango": "🥭",
    "Chirimoya": "🍈",
}

SENSORES = (
    ("temperature", "Temperatura", "°C", "thermometer", colors.SENSOR["temperatura"]),
    ("soil_moisture", "Humedad del suelo", "%", "droplets", colors.SENSOR["humedad_suelo"]),
    ("air_humidity", "Humedad ambiental", "%", "cloud", colors.SENSOR["humedad_ambiental"]),
    ("light", "Luminosidad", "lx", "sun", colors.SENSOR["luminosidad"]),
)


def construir_contorno(vertices: list[dict[str, int]]) -> str:
    """Valida un contorno y lo convierte a un polígono CSS porcentual."""

    if len(vertices) < 3:
        raise ValueError("Añade al menos tres vértices para cerrar el contorno.")

    puntos = [(vertice["x"], vertice["y"]) for vertice in vertices]
    if any(not 0 <= x <= 100 or not 0 <= y <= 100 for x, y in puntos):
        raise ValueError("Los vértices deben estar dentro de la cuadrícula.")
    if len(set(puntos)) != len(puntos):
        raise ValueError("El contorno no puede repetir vértices.")

    area_doble = sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(puntos, puntos[1:] + puntos[:1])
    )
    if area_doble == 0:
        raise ValueError("Los vértices deben formar una superficie.")

    # Solo se cruzan los lados no contiguos; los vecinos comparten un vértice válido.
    for indice, inicio in enumerate(puntos):
        siguiente = (indice + 1) % len(puntos)
        for otro_indice in range(indice + 1, len(puntos)):
            otro_siguiente = (otro_indice + 1) % len(puntos)
            if siguiente == otro_indice or otro_siguiente == indice:
                continue
            if _segmentos_intersectan(
                inicio,
                puntos[siguiente],
                puntos[otro_indice],
                puntos[otro_siguiente],
            ):
                raise ValueError("El contorno no puede cruzarse a sí mismo.")

    coordenadas = ", ".join(f"{x}% {y}%" for x, y in puntos)
    return f"polygon({coordenadas})"


def _orientacion(
    a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]
) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _sobre_segmento(
    a: tuple[float, float],
    b: tuple[float, float],
    punto: tuple[float, float],
) -> bool:
    return (
        min(a[0], b[0]) <= punto[0] <= max(a[0], b[0])
        and min(a[1], b[1]) <= punto[1] <= max(a[1], b[1])
    )


def _segmentos_intersectan(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> bool:
    o1, o2 = _orientacion(a, b, c), _orientacion(a, b, d)
    o3, o4 = _orientacion(c, d, a), _orientacion(c, d, b)
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    return (
        (o1 == 0 and _sobre_segmento(a, b, c))
        or (o2 == 0 and _sobre_segmento(a, b, d))
        or (o3 == 0 and _sobre_segmento(c, d, a))
        or (o4 == 0 and _sobre_segmento(c, d, b))
    )


def _cruzan_en_interior(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> bool:
    return (
        _orientacion(a, b, c) * _orientacion(a, b, d) < 0
        and _orientacion(c, d, a) * _orientacion(c, d, b) < 0
    )


def _parametros_interseccion(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> list[float]:
    direccion = (b[0] - a[0], b[1] - a[1])
    borde = (d[0] - c[0], d[1] - c[1])
    separacion = (c[0] - a[0], c[1] - a[1])
    determinante = direccion[0] * borde[1] - direccion[1] * borde[0]
    tolerancia = 1e-9

    if abs(determinante) > tolerancia:
        t = (
            separacion[0] * borde[1] - separacion[1] * borde[0]
        ) / determinante
        u = (
            separacion[0] * direccion[1] - separacion[1] * direccion[0]
        ) / determinante
        if -tolerancia <= t <= 1 + tolerancia and -tolerancia <= u <= 1 + tolerancia:
            return [min(1.0, max(0.0, t))]
        return []

    if abs(
        separacion[0] * direccion[1] - separacion[1] * direccion[0]
    ) > tolerancia:
        return []

    longitud_cuadrada = direccion[0] ** 2 + direccion[1] ** 2
    parametros = []
    for punto in (c, d):
        t = (
            (punto[0] - a[0]) * direccion[0]
            + (punto[1] - a[1]) * direccion[1]
        ) / longitud_cuadrada
        if -tolerancia <= t <= 1 + tolerancia:
            parametros.append(min(1.0, max(0.0, t)))
    return parametros


def _punto_en_poligono(
    punto: tuple[float, float],
    poligono: list[tuple[float, float]],
    incluir_borde: bool = True,
) -> bool:
    dentro = False
    for inicio, fin in zip(poligono, poligono[1:] + poligono[:1]):
        if (
            _orientacion(inicio, fin, punto) == 0
            and _sobre_segmento(inicio, fin, punto)
        ):
            return incluir_borde
        if (inicio[1] > punto[1]) != (fin[1] > punto[1]):
            corte_x = inicio[0] + (fin[0] - inicio[0]) * (
                (punto[1] - inicio[1]) / (fin[1] - inicio[1])
            )
            if punto[0] < corte_x:
                dentro = not dentro
    return dentro


def _punto_interior_poligono(
    poligono: list[tuple[float, float]],
) -> tuple[float, float]:
    area_doble = sum(
        inicio[0] * fin[1] - fin[0] * inicio[1]
        for inicio, fin in zip(poligono, poligono[1:] + poligono[:1])
    )
    centroide = (
        sum(
            (inicio[0] + fin[0])
            * (inicio[0] * fin[1] - fin[0] * inicio[1])
            for inicio, fin in zip(poligono, poligono[1:] + poligono[:1])
        )
        / (3 * area_doble),
        sum(
            (inicio[1] + fin[1])
            * (inicio[0] * fin[1] - fin[0] * inicio[1])
            for inicio, fin in zip(poligono, poligono[1:] + poligono[:1])
        )
        / (3 * area_doble),
    )
    if _punto_en_poligono(centroide, poligono, incluir_borde=False):
        return centroide

    coordenadas_y = sorted({punto[1] for punto in poligono})
    mejor_punto = None
    mejor_anchura = -1.0
    for y_inferior, y_superior in zip(coordenadas_y, coordenadas_y[1:]):
        y = (y_inferior + y_superior) / 2
        intersecciones = []
        for inicio, fin in zip(poligono, poligono[1:] + poligono[:1]):
            if (inicio[1] > y) != (fin[1] > y):
                intersecciones.append(
                    inicio[0]
                    + (fin[0] - inicio[0])
                    * (y - inicio[1])
                    / (fin[1] - inicio[1])
                )
        intersecciones.sort()
        for izquierda, derecha in zip(intersecciones[::2], intersecciones[1::2]):
            anchura = derecha - izquierda
            if anchura > mejor_anchura:
                mejor_anchura = anchura
                mejor_punto = ((izquierda + derecha) / 2, y)

    if mejor_punto is None:
        raise ValueError("No se pudo encontrar el interior del sector.")
    return mejor_punto


def _ubicar_etiqueta_sector(
    sector: dict[str, str],
    vertices: list[tuple[float, float]],
) -> None:
    x, y = _punto_interior_poligono(vertices)
    sector["label_x"] = f"{x:.2f}"
    sector["label_y"] = f"{y:.2f}"


def _segmento_dentro_poligono(
    inicio: tuple[float, float],
    fin: tuple[float, float],
    poligono: list[tuple[float, float]],
) -> bool:
    parametros = [0.0, 1.0]
    for borde, fin_borde in zip(poligono, poligono[1:] + poligono[:1]):
        parametros.extend(
            _parametros_interseccion(inicio, fin, borde, fin_borde)
        )

    ordenados = sorted(set(parametros))
    for punto in (inicio, fin):
        if not _punto_en_poligono(punto, poligono):
            return False
    for t1, t2 in zip(ordenados, ordenados[1:]):
        muestra = (
            inicio[0] + (fin[0] - inicio[0]) * ((t1 + t2) / 2),
            inicio[1] + (fin[1] - inicio[1]) * ((t1 + t2) / 2),
        )
        if not _punto_en_poligono(muestra, poligono):
            return False
    return True


def _vertices_css(contorno: str) -> list[tuple[float, float]]:
    coincidencia = re.fullmatch(r"polygon\((.*)\)", contorno.strip())
    if coincidencia is None:
        raise ValueError("El contorno de la parcela no es válido.")
    puntos = []
    for coordenada in coincidencia.group(1).split(","):
        valores = coordenada.strip().split()
        if len(valores) != 2:
            raise ValueError("El contorno de la parcela no es válido.")
        puntos.append((float(valores[0].removesuffix("%")), float(valores[1].removesuffix("%"))))
    return puntos


def vertices_parcela(parcela: dict[str, str]) -> list[tuple[float, float]]:
    if parcela.get("shape") == "dibujada":
        return _vertices_css(parcela.get("outline", ""))
    return FORMAS_POLIGONO.get(parcela.get("shape", "rectangulo"), FORMAS_POLIGONO["rectangulo"])


def punto_en_parcela(
    punto: tuple[float, float], parcela: dict[str, str], incluir_borde: bool = True
) -> bool:
    if parcela.get("shape") == "circulo":
        distancia = ((punto[0] - 50) / 49) ** 2 + ((punto[1] - 50) / 48) ** 2
        return distancia <= 1 if incluir_borde else distancia < 1
    return _punto_en_poligono(punto, vertices_parcela(parcela), incluir_borde)


def _vertices_sector(sector: dict[str, str]) -> list[tuple[float, float]]:
    if sector.get("outline"):
        return _vertices_css(sector["outline"])
    left, top = float(sector["left"]), float(sector["top"])
    right = left + float(sector["width"])
    bottom = top + float(sector["height"])
    return [(left, top), (right, top), (right, bottom), (left, bottom)]


def validar_sector_dibujado(
    parcela: dict[str, str],
    vertices: list[dict[str, int]],
    sectores_existentes: list[dict[str, str]],
) -> str:
    """Rechaza sectores fuera de la parcela o que se solapen con otros sectores."""

    contorno = construir_contorno(vertices)
    puntos = [(vertice["x"], vertice["y"]) for vertice in vertices]
    for punto, siguiente in zip(puntos, puntos[1:] + puntos[:1]):
        if parcela.get("shape") == "circulo":
            dentro = punto_en_parcela(punto, parcela) and punto_en_parcela(
                siguiente, parcela
            )
        else:
            dentro = _segmento_dentro_poligono(
                punto,
                siguiente,
                vertices_parcela(parcela),
            )
        if not dentro:
            if not punto_en_parcela(punto, parcela) or not punto_en_parcela(
                siguiente, parcela
            ):
                raise ValueError("Todos los vértices deben quedar dentro de la parcela.")
            raise ValueError("Los lados del sector deben quedar dentro de la parcela.")

    for existente in sectores_existentes:
        otros_puntos = _vertices_sector(existente)
        if set(puntos) == set(otros_puntos):
            raise ValueError("Los sectores no pueden solaparse.")
        for inicio, fin in zip(puntos, puntos[1:] + puntos[:1]):
            for otro_inicio, otro_fin in zip(
                otros_puntos, otros_puntos[1:] + otros_puntos[:1]
            ):
                if _cruzan_en_interior(inicio, fin, otro_inicio, otro_fin):
                    raise ValueError("Los sectores no pueden solaparse.")
        if any(_punto_en_poligono(punto, otros_puntos, False) for punto in puntos):
            raise ValueError("Los sectores no pueden solaparse.")
        if any(_punto_en_poligono(punto, puntos, False) for punto in otros_puntos):
            raise ValueError("Los sectores no pueden solaparse.")

    return contorno


def calcular_medias(sectores: list[dict[str, str]]) -> list[dict[str, str]]:
    """Calcula una media por magnitud usando solo sectores con lectura disponible."""

    medias = []
    for tipo, nombre, unidad, icono, color in SENSORES:
        valores = []
        for sector in sectores:
            valor = sector.get(tipo, "")
            if not valor:
                # Un sector sin lectura no equivale a cero y no debe bajar la media.
                continue
            try:
                numero = float(valor)
            except ValueError as error:
                raise ValueError(f"Lectura no válida para {nombre.lower()}.") from error
            if not math.isfinite(numero):
                raise ValueError(f"Lectura no válida para {nombre.lower()}.")
            valores.append(numero)

        medias.append(
            {
                "type": tipo,
                "name": nombre,
                "value": f"{sum(valores) / len(valores):.1f}" if valores else "",
                "unit": unidad,
                "icon": icono,
                "color": color,
                "sector_count": str(len(valores)),
            }
        )
    return medias


def dividir_sector(
    sector: dict[str, str], orientacion: str
) -> tuple[dict[str, str], dict[str, str]]:
    """Divide un sector por la mitad en coordenadas porcentuales del plano."""

    if orientacion not in ("vertical", "horizontal"):
        raise ValueError("La división debe ser vertical u horizontal.")

    existente = sector.copy()
    nuevo = sector.copy()
    for tipo, *_ in SENSORES:
        nuevo[tipo] = ""
        nuevo[f"has_{tipo}"] = "no"

    if orientacion == "vertical":
        mitad = float(sector["width"]) / 2
        existente["width"] = f"{mitad:.2f}"
        nuevo["left"] = f"{float(sector['left']) + mitad:.2f}"
        nuevo["width"] = f"{mitad:.2f}"
    else:
        mitad = float(sector["height"]) / 2
        existente["height"] = f"{mitad:.2f}"
        nuevo["top"] = f"{float(sector['top']) + mitad:.2f}"
        nuevo["height"] = f"{mitad:.2f}"

    return existente, nuevo


def eliminar_parcela_de_datos(
    parcelas: list[dict[str, str]],
    sectores: list[dict[str, str]],
    parcela_id: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Elimina una parcela de la maqueta y los sectores que contiene."""

    if not any(parcela["id"] == parcela_id for parcela in parcelas):
        raise ValueError("La parcela seleccionada ya no existe.")

    return (
        [parcela for parcela in parcelas if parcela["id"] != parcela_id],
        [sector for sector in sectores if sector["parcel_id"] != parcela_id],
    )


def _crear_sector(
    sector_id: str,
    parcela_id: str,
    nombre: str,
    cultivo: str,
    left: str,
    top: str,
    width: str,
    height: str,
    lecturas: dict[str, str] | None = None,
    alerta_demo: str = "",
) -> dict[str, str]:
    datos = {
        "id": sector_id,
        "parcel_id": parcela_id,
        "name": nombre,
        "crop": cultivo,
        "crop_icon": CULTIVOS[cultivo],
        "left": left,
        "top": top,
        "width": width,
        "height": height,
        "outline": "",
        "stroke_points": "0,0 100,0 100,100 0,100",
        "label_x": "50",
        "label_y": "50",
        "demo_alert": alerta_demo,
    }
    lecturas = lecturas or {}
    for tipo, *_ in SENSORES:
        datos[tipo] = lecturas.get(tipo, "")
        datos[f"has_{tipo}"] = "yes" if tipo in lecturas else "no"
    return datos


def _crear_sectores_demo() -> list[dict[str, str]]:
    return [
        _crear_sector("1", "1", "Sector 1", "Tomate", "0", "0", "50", "50", {
            "temperature": "24.6",
            "soil_moisture": "42",
            "air_humidity": "61",
            "light": "18500",
        }, "warning"),
        _crear_sector("2", "1", "Sector 2", "Tomate", "50", "0", "50", "50", {
            "temperature": "23.8",
            "soil_moisture": "45",
            "air_humidity": "58",
            "light": "17700",
        }),
        _crear_sector("3", "1", "Sector 3", "Aguacate", "0", "50", "50", "50", {
            "temperature": "25.1",
            "soil_moisture": "49",
            "air_humidity": "63",
            "light": "19100",
        }),
        _crear_sector("4", "1", "Sector 4", "Aguacate", "50", "50", "50", "50", {
            "temperature": "24.2",
            "soil_moisture": "47",
            "air_humidity": "60",
            "light": "18200",
        }),
        _crear_sector("5", "2", "Sector 1", "Tomate", "0", "0", "50", "100", {
            "temperature": "26.0",
            "soil_moisture": "40",
            "air_humidity": "57",
            "light": "16900",
        }, "danger"),
        _crear_sector("6", "2", "Sector 2", "Tomate", "50", "0", "50", "100", {
            "temperature": "25.4",
            "soil_moisture": "44",
            "air_humidity": "59",
            "light": "17300",
        }),
        _crear_sector("7", "3", "Sector 1", "Mango", "0", "0", "50", "100", {
            "temperature": "27.1",
            "soil_moisture": "46",
            "air_humidity": "54",
            "light": "19800",
        }),
        _crear_sector("8", "3", "Sector 2", "Chirimoya", "50", "0", "50", "100", {
            "temperature": "26.3",
            "soil_moisture": "51",
            "air_humidity": "56",
            "light": "18700",
        }),
    ]


def _crear_parcela_dibujada(
    parcela_id: str,
    nombre: str,
    area: float,
    vertices: list[dict[str, int]],
    alerta_demo: str = "",
) -> dict[str, str]:
    return {
        "id": parcela_id,
        "name": nombre,
        "area_m2": f"{area:g}",
        "shape": "dibujada",
        "shape_label": FORMAS["dibujada"],
        "outline": construir_contorno(vertices),
        "stroke_points": " ".join(
            f'{vertice["x"]},{vertice["y"]}' for vertice in vertices
        ),
        "demo_alert": alerta_demo,
    }


def _crear_parcelas_demo() -> list[dict[str, str]]:
    parcelas = (
        (
            "1",
            "Huerto de prácticas",
            1200,
            [(7, 7), (93, 7), (93, 93), (7, 93)],
            "warning",
        ),
        (
            "2",
            "Invernadero norte",
            480,
            [
                (21, 7),
                (79, 7),
                (93, 21),
                (93, 79),
                (79, 93),
                (21, 93),
                (7, 79),
                (7, 21),
            ],
            "danger",
        ),
        (
            "3",
            "Parcela de frutales",
            860,
            [(21, 7), (79, 7), (93, 50), (79, 93), (21, 93), (7, 50)],
            "",
        ),
    )
    return [
        _crear_parcela_dibujada(
            parcela_id,
            nombre,
            area,
            [{"x": x, "y": y} for x, y in vertices],
            alerta_demo,
        )
        for parcela_id, nombre, area, vertices, alerta_demo in parcelas
    ]


class DashboardState(rx.State):
    """Estado temporal de la maqueta de parcelas y sectores."""

    parcelas: list[dict[str, str]] = _crear_parcelas_demo()
    sectores: list[dict[str, str]] = _crear_sectores_demo()
    parcela_id_seleccionada: str = ""
    sector_id_seleccionado: str = ""
    sector_abierto: bool = False
    parcela_id_pendiente_eliminar: str = ""
    confirmar_redibujo_sectores_pendiente: bool = False
    modo_dibujo_sectores: bool = False
    contorno_sector_cerrado: bool = False
    vertices_sector_en_edicion: list[dict[str, str]] = []
    sectores_dibujados_temporales: list[dict[str, str]] = []
    error_dibujo_sector: str = ""
    mensaje_dibujo_sector: str = ""

    nuevo_nombre: str = ""
    nueva_area: str = ""
    vertices_nueva_parcela: list[dict[str, str]] = []
    contorno_cerrado: bool = False
    error_formulario: str = ""
    mensaje_formulario: str = ""

    tipo_sensor_nuevo: str = "Temperatura"
    mensaje_sensor: str = ""

    @rx.var
    def parcela_seleccionada(self) -> dict[str, str]:
        return next(
            (
                parcela
                for parcela in self.parcelas
                if parcela["id"] == self.parcela_id_seleccionada
            ),
            {},
        )

    @rx.var
    def sectores_parcela(self) -> list[dict[str, str]]:
        return [
            sector
            for sector in self.sectores
            if sector["parcel_id"] == self.parcela_id_seleccionada
        ]

    @rx.var
    def sector_seleccionado(self) -> dict[str, str]:
        return next(
            (
                sector
                for sector in self.sectores
                if sector["id"] == self.sector_id_seleccionado
            ),
            {},
        )

    @rx.var
    def medias_parcela(self) -> list[dict[str, str]]:
        return calcular_medias(self.sectores_parcela)

    @rx.var
    def contorno_previsualizacion(self) -> str:
        if len(self.vertices_nueva_parcela) < 3:
            return "none"
        coordenadas = ", ".join(
            f'{punto["x"]}% {punto["y"]}%'
            for punto in self.vertices_nueva_parcela
        )
        return f"polygon({coordenadas})"

    @rx.var
    def contorno_parcela_css(self) -> str:
        parcela = self.parcela_seleccionada
        if parcela.get("shape") == "dibujada":
            return parcela.get("outline", "inset(0)")
        if parcela.get("shape") == "circulo":
            return "ellipse(49% 48% at 50% 50%)"
        forma = parcela.get("shape", "rectangulo")
        puntos = FORMAS_POLIGONO.get(forma, FORMAS_POLIGONO["rectangulo"])
        coordenadas = ", ".join(f"{x}% {y}%" for x, y in puntos)
        return f"polygon({coordenadas})"

    @rx.var
    def contorno_sector_previsualizacion(self) -> str:
        if len(self.vertices_sector_en_edicion) < 3:
            return "none"
        coordenadas = ", ".join(
            f'{punto["x"]}% {punto["y"]}%'
            for punto in self.vertices_sector_en_edicion
        )
        return f"polygon({coordenadas})"

    @rx.var
    def lecturas_sector(self) -> list[dict[str, str]]:
        sector = self.sector_seleccionado
        return [
            {
                "type": tipo,
                "name": nombre,
                "value": sector.get(tipo, ""),
                "unit": unidad,
                "icon": icono,
                "color": color,
            }
            for tipo, nombre, unidad, icono, color in SENSORES
            if sector.get(f"has_{tipo}") == "yes"
        ]

    @rx.event
    def actualizar_nombre(self, valor: str):
        self.nuevo_nombre = valor

    @rx.event
    def actualizar_area(self, valor: str):
        self.nueva_area = valor

    @rx.event
    def agregar_vertice(self, x: int, y: int):
        if self.contorno_cerrado:
            self.error_formulario = "Vuelve a editar el contorno antes de añadir vértices."
            return
        if x not in PUNTOS_CUADRICULA or y not in PUNTOS_CUADRICULA:
            self.error_formulario = "El vértice seleccionado no está en la cuadrícula."
            return
        if any(
            punto["x"] == str(x) and punto["y"] == str(y)
            for punto in self.vertices_nueva_parcela
        ):
            self.error_formulario = "Ese vértice ya está marcado."
            return
        self.vertices_nueva_parcela = [
            *self.vertices_nueva_parcela,
            {"x": str(x), "y": str(y)},
        ]
        self.error_formulario = ""
        self.mensaje_formulario = ""

    @rx.event
    def deshacer_vertice(self):
        if self.contorno_cerrado:
            self.error_formulario = "Vuelve a editar el contorno antes de deshacer."
            return
        if self.vertices_nueva_parcela:
            self.vertices_nueva_parcela = self.vertices_nueva_parcela[:-1]
            self.error_formulario = ""
            self.mensaje_formulario = ""

    @rx.event
    def limpiar_contorno(self):
        self.vertices_nueva_parcela = []
        self.contorno_cerrado = False
        self.error_formulario = ""
        self.mensaje_formulario = ""

    @rx.event
    def cerrar_contorno(self):
        try:
            construir_contorno(
                [
                    {"x": int(punto["x"]), "y": int(punto["y"])}
                    for punto in self.vertices_nueva_parcela
                ]
            )
        except ValueError as error:
            self.error_formulario = str(error)
            self.mensaje_formulario = ""
            return
        self.contorno_cerrado = True
        self.error_formulario = ""
        self.mensaje_formulario = "Contorno cerrado. Ya puedes añadir la parcela."

    @rx.event
    def reabrir_contorno(self):
        self.contorno_cerrado = False
        self.error_formulario = ""
        self.mensaje_formulario = ""

    @rx.event
    def solicitar_redibujar_sectores(self):
        if not self.parcela_seleccionada:
            self.mensaje_dibujo_sector = "Abre una parcela antes de dibujar sectores."
            return
        self.confirmar_redibujo_sectores_pendiente = True
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = ""

    @rx.event
    def cancelar_solicitud_redibujar_sectores(self):
        self.confirmar_redibujo_sectores_pendiente = False

    @rx.event
    def confirmar_redibujar_sectores(self):
        if (
            not self.confirmar_redibujo_sectores_pendiente
            or not self.parcela_seleccionada
        ):
            return
        self.confirmar_redibujo_sectores_pendiente = False
        self.modo_dibujo_sectores = True
        self.vertices_sector_en_edicion = []
        self.contorno_sector_cerrado = False
        self.sectores_dibujados_temporales = []
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = ""

    @rx.event
    def agregar_vertice_sector(self, x: int, y: int):
        if not self.modo_dibujo_sectores:
            return
        if x not in PUNTOS_CUADRICULA or y not in PUNTOS_CUADRICULA:
            self.error_dibujo_sector = "El punto seleccionado no está en la cuadrícula."
            return
        punto = (x, y)
        if not punto_en_parcela(punto, self.parcela_seleccionada):
            self.error_dibujo_sector = "El vértice debe quedar dentro de la parcela."
            return
        if any(
            vertice["x"] == str(x) and vertice["y"] == str(y)
            for vertice in self.vertices_sector_en_edicion
        ):
            self.error_dibujo_sector = "Ese vértice ya está marcado."
            return
        self.vertices_sector_en_edicion = [
            *self.vertices_sector_en_edicion,
            {"x": str(x), "y": str(y)},
        ]
        self.contorno_sector_cerrado = False
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = ""

    @rx.event
    def deshacer_vertice_sector(self):
        if self.vertices_sector_en_edicion:
            self.vertices_sector_en_edicion = self.vertices_sector_en_edicion[:-1]
            self.contorno_sector_cerrado = False
            self.error_dibujo_sector = ""
            self.mensaje_dibujo_sector = ""

    @rx.event
    def limpiar_contorno_sector(self):
        self.vertices_sector_en_edicion = []
        self.contorno_sector_cerrado = False
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = ""

    @rx.event
    def cerrar_contorno_sector(self):
        try:
            validar_sector_dibujado(
                self.parcela_seleccionada,
                [
                    {"x": int(punto["x"]), "y": int(punto["y"])}
                    for punto in self.vertices_sector_en_edicion
                ],
                self.sectores_dibujados_temporales,
            )
        except ValueError as error:
            self.error_dibujo_sector = str(error)
            self.mensaje_dibujo_sector = ""
            return
        self.contorno_sector_cerrado = True
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = "Sector válido. Puedes añadirlo al plano."

    @rx.event
    def crear_sector_dibujado(self):
        if not self.contorno_sector_cerrado:
            self.error_dibujo_sector = "Cierra un sector válido antes de añadirlo."
            return
        vertices = [
            {"x": int(punto["x"]), "y": int(punto["y"])}
            for punto in self.vertices_sector_en_edicion
        ]
        try:
            contorno = validar_sector_dibujado(
                self.parcela_seleccionada,
                vertices,
                self.sectores_dibujados_temporales,
            )
        except ValueError as error:
            self.error_dibujo_sector = str(error)
            self.mensaje_dibujo_sector = ""
            return

        sector_id = str(
            max(
                (int(sector["id"]) for sector in self.sectores),
                default=0,
            )
            + len(self.sectores_dibujados_temporales)
            + 1
        )
        nuevo = _crear_sector(
            sector_id,
            self.parcela_id_seleccionada,
            f"Sector {len(self.sectores_dibujados_temporales) + 1}",
            "Sin cultivo",
            "0",
            "0",
            "100",
            "100",
        )
        nuevo["outline"] = contorno
        nuevo["stroke_points"] = " ".join(
            f"{vertice['x']},{vertice['y']}" for vertice in vertices
        )
        _ubicar_etiqueta_sector(
            nuevo,
            [(vertice["x"], vertice["y"]) for vertice in vertices],
        )
        self.sectores_dibujados_temporales = [
            *self.sectores_dibujados_temporales,
            nuevo,
        ]
        self.vertices_sector_en_edicion = []
        self.contorno_sector_cerrado = False
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = f"{nuevo['name']} añadido al plano."

    @rx.event
    def terminar_dibujo_sectores(self):
        if not self.modo_dibujo_sectores:
            return
        if self.vertices_sector_en_edicion:
            self.error_dibujo_sector = (
                "Añade o borra el sector en edición antes de terminar."
            )
            return
        if not self.sectores_dibujados_temporales:
            self.error_dibujo_sector = "Dibuja al menos un sector antes de terminar."
            return
        parcela_id = self.parcela_id_seleccionada
        if any(
            sector["parcel_id"] != parcela_id
            for sector in self.sectores_dibujados_temporales
        ):
            self.error_dibujo_sector = "Los sectores dibujados no pertenecen a esta parcela."
            return
        self.sectores = [
            sector
            for sector in self.sectores
            if sector["parcel_id"] != parcela_id
        ] + self.sectores_dibujados_temporales
        self.sector_id_seleccionado = self.sectores_dibujados_temporales[0]["id"]
        self.sector_abierto = False
        self.modo_dibujo_sectores = False
        self.vertices_sector_en_edicion = []
        self.contorno_sector_cerrado = False
        self.sectores_dibujados_temporales = []
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = ""

    @rx.event
    def cancelar_dibujo_sectores(self):
        self.modo_dibujo_sectores = False
        self.vertices_sector_en_edicion = []
        self.contorno_sector_cerrado = False
        self.sectores_dibujados_temporales = []
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = ""

    @rx.event
    def actualizar_tipo_sensor(self, valor: str):
        self.tipo_sensor_nuevo = valor

    @rx.event
    def solicitar_eliminacion_parcela(self, parcela_id: str):
        if not any(parcela["id"] == parcela_id for parcela in self.parcelas):
            self.error_formulario = "La parcela seleccionada ya no existe."
            return
        self.parcela_id_pendiente_eliminar = parcela_id
        self.error_formulario = ""
        self.mensaje_formulario = ""

    @rx.event
    def cancelar_eliminacion_parcela(self):
        self.parcela_id_pendiente_eliminar = ""

    @rx.event
    def confirmar_eliminacion_parcela(self):
        try:
            self.parcelas, self.sectores = eliminar_parcela_de_datos(
                self.parcelas,
                self.sectores,
                self.parcela_id_pendiente_eliminar,
            )
        except ValueError as error:
            self.error_formulario = str(error)
            self.parcela_id_pendiente_eliminar = ""
            return

        if self.parcela_id_seleccionada == self.parcela_id_pendiente_eliminar:
            self.parcela_id_seleccionada = ""
            self.sector_id_seleccionado = ""
            self.sector_abierto = False
        self.parcela_id_pendiente_eliminar = ""
        self.mensaje_formulario = "Parcela eliminada de esta maqueta."

    @rx.event
    def abrir_parcela(self, parcela_id: str):
        if not any(parcela["id"] == parcela_id for parcela in self.parcelas):
            self.mensaje_formulario = "La parcela seleccionada ya no existe."
            return
        self.confirmar_redibujo_sectores_pendiente = False
        self.modo_dibujo_sectores = False
        self.contorno_sector_cerrado = False
        self.vertices_sector_en_edicion = []
        self.sectores_dibujados_temporales = []
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = ""
        self.parcela_id_seleccionada = parcela_id
        sectores = [
            sector for sector in self.sectores if sector["parcel_id"] == parcela_id
        ]
        self.sector_id_seleccionado = sectores[0]["id"] if sectores else ""
        self.sector_abierto = False

    @rx.event
    def volver_al_panel(self):
        self.confirmar_redibujo_sectores_pendiente = False
        self.modo_dibujo_sectores = False
        self.contorno_sector_cerrado = False
        self.vertices_sector_en_edicion = []
        self.sectores_dibujados_temporales = []
        self.error_dibujo_sector = ""
        self.mensaje_dibujo_sector = ""
        self.parcela_id_seleccionada = ""
        self.sector_id_seleccionado = ""
        self.sector_abierto = False

    @rx.event
    def abrir_sector(self, sector_id: str):
        if not any(
            sector["id"] == sector_id
            and sector["parcel_id"] == self.parcela_id_seleccionada
            for sector in self.sectores
        ):
            self.mensaje_sensor = "El sector seleccionado ya no existe."
            return
        self.sector_id_seleccionado = sector_id
        self.sector_abierto = True
        self.mensaje_sensor = ""

    @rx.event
    def volver_a_parcela(self):
        self.sector_abierto = False

    @rx.event
    def crear_parcela(self):
        nombre = self.nuevo_nombre.strip()
        try:
            area = float(self.nueva_area)
        except ValueError:
            self.error_formulario = "Escribe una superficie válida en m²."
            self.mensaje_formulario = ""
            return

        if not nombre:
            self.error_formulario = "Escribe un nombre para la parcela."
            self.mensaje_formulario = ""
            return
        if len(nombre) > 80:
            self.error_formulario = "El nombre no puede superar 80 caracteres."
            self.mensaje_formulario = ""
            return
        if not math.isfinite(area) or area <= 0:
            self.error_formulario = "La superficie debe ser mayor que 0 m²."
            self.mensaje_formulario = ""
            return
        if not self.contorno_cerrado:
            self.error_formulario = "Cierra un contorno válido antes de añadir la parcela."
            self.mensaje_formulario = ""
            return

        vertices = [
            {"x": int(punto["x"]), "y": int(punto["y"])}
            for punto in self.vertices_nueva_parcela
        ]

        parcela_id = str(max((int(p["id"]) for p in self.parcelas), default=0) + 1)
        try:
            parcela = _crear_parcela_dibujada(
                parcela_id,
                nombre,
                area,
                vertices,
            )
        except ValueError as error:
            self.error_formulario = str(error)
            self.mensaje_formulario = ""
            return
        self.parcelas = [*self.parcelas, parcela]
        sector_id = str(max((int(s["id"]) for s in self.sectores), default=0) + 1)
        nuevo_sector = _crear_sector(
            sector_id,
            parcela_id,
            "Sector 1",
            "Sin cultivo",
            "0",
            "0",
            "100",
            "100",
        )
        _ubicar_etiqueta_sector(
            nuevo_sector,
            [(punto["x"], punto["y"]) for punto in vertices],
        )
        self.sectores = [*self.sectores, nuevo_sector]
        self.nuevo_nombre = ""
        self.nueva_area = ""
        self.error_formulario = ""
        self.mensaje_formulario = f"Parcela «{nombre}» añadida a esta maqueta."
        self.vertices_nueva_parcela = []
        self.contorno_cerrado = False

    @rx.event
    def dividir_sector(self, orientacion: str):
        if orientacion not in ("vertical", "horizontal"):
            self.mensaje_sensor = "Elige una división vertical u horizontal."
            return
        sector = self.sector_seleccionado
        if not sector:
            self.mensaje_sensor = "Selecciona un sector antes de dividirlo."
            return

        sector_id = str(max((int(s["id"]) for s in self.sectores), default=0) + 1)
        existente, nuevo = dividir_sector(sector, orientacion)
        nuevo["id"] = sector_id
        nuevo["name"] = f"Sector {len(self.sectores_parcela) + 1}"

        # La división conserva el cultivo, pero el sector nuevo necesita sus propios sensores.
        self.sectores = [
            existente if item["id"] == sector["id"] else item
            for item in self.sectores
        ]
        self.sectores = [*self.sectores, nuevo]
        self.sector_id_seleccionado = sector_id
        self.sector_abierto = True
        self.mensaje_sensor = "Sector creado; añade sus sensores para ver lecturas."

    @rx.event
    def cambiar_cultivo(self, cultivo: str):
        if cultivo not in CULTIVOS:
            self.mensaje_sensor = "Selecciona un cultivo válido."
            return
        self.sectores = [
            {
                **sector,
                "crop": cultivo,
                "crop_icon": CULTIVOS[cultivo],
            }
            if sector["id"] == self.sector_id_seleccionado
            else sector
            for sector in self.sectores
        ]

    @rx.event
    def agregar_sensor(self, tipo: str):
        tipo = next(
            (clave for clave, nombre, *_ in SENSORES if nombre == tipo),
            tipo,
        )
        if tipo not in {sensor[0] for sensor in SENSORES}:
            self.mensaje_sensor = "Selecciona un tipo de sensor válido."
            return
        if not self.sector_seleccionado:
            self.mensaje_sensor = "Selecciona un sector antes de añadir sensores."
            return
        if self.sector_seleccionado.get(f"has_{tipo}") == "yes":
            self.mensaje_sensor = "Ese sector ya tiene este tipo de sensor."
            return

        self.sectores = [
            {
                **sector,
                f"has_{tipo}": "yes",
                tipo: "",
            }
            if sector["id"] == self.sector_id_seleccionado
            else sector
            for sector in self.sectores
        ]
        self.mensaje_sensor = "Sensor añadido a la maqueta; todavía no tiene lecturas."
