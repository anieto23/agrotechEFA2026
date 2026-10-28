import math

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

    def orientacion(
        a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]
    ) -> int:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def sobre_segmento(
        a: tuple[int, int], b: tuple[int, int], p: tuple[int, int]
    ) -> bool:
        return (
            min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])
        )

    def se_cruzan(
        a: tuple[int, int],
        b: tuple[int, int],
        c: tuple[int, int],
        d: tuple[int, int],
    ) -> bool:
        o1, o2 = orientacion(a, b, c), orientacion(a, b, d)
        o3, o4 = orientacion(c, d, a), orientacion(c, d, b)
        if o1 * o2 < 0 and o3 * o4 < 0:
            return True
        return (
            (o1 == 0 and sobre_segmento(a, b, c))
            or (o2 == 0 and sobre_segmento(a, b, d))
            or (o3 == 0 and sobre_segmento(c, d, a))
            or (o4 == 0 and sobre_segmento(c, d, b))
        )

    # Solo se cruzan los lados no contiguos; los vecinos comparten un vértice válido.
    for indice, inicio in enumerate(puntos):
        siguiente = (indice + 1) % len(puntos)
        for otro_indice in range(indice + 1, len(puntos)):
            otro_siguiente = (otro_indice + 1) % len(puntos)
            if siguiente == otro_indice or otro_siguiente == indice:
                continue
            if se_cruzan(
                inicio,
                puntos[siguiente],
                puntos[otro_indice],
                puntos[otro_siguiente],
            ):
                raise ValueError("El contorno no puede cruzarse a sí mismo.")

    coordenadas = ", ".join(f"{x}% {y}%" for x, y in puntos)
    return f"polygon({coordenadas})"


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
    }
    lecturas = lecturas or {}
    for tipo, *_ in SENSORES:
        datos[tipo] = lecturas.get(tipo, "")
        datos[f"has_{tipo}"] = "yes" if tipo in lecturas else "no"
    return datos


class DashboardState(rx.State):
    """Estado temporal de la maqueta de parcelas y sectores."""

    parcelas: list[dict[str, str]] = [
        {
            "id": "1",
            "name": "Huerto de prácticas",
            "area_m2": "1200",
            "shape": "rectangulo",
            "shape_label": "Rectángulo",
            "outline": "",
        },
        {
            "id": "2",
            "name": "Invernadero norte",
            "area_m2": "480",
            "shape": "circulo",
            "shape_label": "Círculo",
            "outline": "",
        },
        {
            "id": "3",
            "name": "Parcela de frutales",
            "area_m2": "860",
            "shape": "poligono",
            "shape_label": "Polígono",
            "outline": "",
        },
    ]
    sectores: list[dict[str, str]] = [
        _crear_sector("1", "1", "Sector 1", "Tomate", "0", "0", "50", "50", {
            "temperature": "24.6",
            "soil_moisture": "42",
            "air_humidity": "61",
            "light": "18500",
        }),
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
        }),
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
    parcela_id_seleccionada: str = ""
    sector_id_seleccionado: str = ""
    sector_abierto: bool = False
    parcela_id_pendiente_eliminar: str = ""

    nuevo_nombre: str = ""
    nueva_area: str = ""
    nueva_forma: str = "Rectángulo"
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
    def actualizar_forma(self, valor: str):
        self.nueva_forma = valor
        self.error_formulario = ""
        self.mensaje_formulario = ""

    @rx.event
    def agregar_vertice(self, x: int, y: int):
        if self.nueva_forma != FORMAS["dibujada"]:
            return
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
        self.parcela_id_seleccionada = parcela_id
        sectores = [
            sector for sector in self.sectores if sector["parcel_id"] == parcela_id
        ]
        self.sector_id_seleccionado = sectores[0]["id"] if sectores else ""
        self.sector_abierto = False

    @rx.event
    def volver_al_panel(self):
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
        forma = next(
            (clave for clave, etiqueta in FORMAS.items() if etiqueta == self.nueva_forma),
            None,
        )
        if forma is None:
            self.error_formulario = "Selecciona una forma válida."
            self.mensaje_formulario = ""
            return
        contorno = ""
        if forma == "dibujada":
            if not self.contorno_cerrado:
                self.error_formulario = "Cierra un contorno válido antes de añadir la parcela."
                self.mensaje_formulario = ""
                return
            try:
                contorno = construir_contorno(
                    [
                        {"x": int(punto["x"]), "y": int(punto["y"])}
                        for punto in self.vertices_nueva_parcela
                    ]
                )
            except ValueError as error:
                self.error_formulario = str(error)
                self.mensaje_formulario = ""
                return

        parcela_id = str(max((int(p["id"]) for p in self.parcelas), default=0) + 1)
        etiqueta = FORMAS[forma]
        self.parcelas = [
            *self.parcelas,
            {
                "id": parcela_id,
                "name": nombre,
                "area_m2": f"{area:g}",
                "shape": forma,
                "shape_label": etiqueta,
                "outline": contorno,
            },
        ]
        sector_id = str(max((int(s["id"]) for s in self.sectores), default=0) + 1)
        self.sectores = [
            *self.sectores,
            _crear_sector(
                sector_id,
                parcela_id,
                "Sector 1",
                "Sin cultivo",
                "0",
                "0",
                "100",
                "100",
            ),
        ]
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
