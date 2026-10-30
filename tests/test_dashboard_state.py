import pytest

from agrotechEFA2026.state.dashboard_state import (
    _crear_parcela_dibujada,
    _crear_parcelas_demo,
    _crear_sectores_demo,
    _punto_en_poligono,
    _punto_interior_poligono,
    _ubicar_etiqueta_sector,
    PUNTOS_CUADRICULA,
    calcular_medias,
    construir_contorno,
    dividir_sector,
    eliminar_parcela_de_datos,
    eliminar_sector_de_datos,
    validar_sector_dibujado,
)


def test_cuadricula_duplica_puntos_y_conserva_las_posiciones_anteriores():
    posiciones_anteriores = {7, 21, 36, 50, 64, 79, 93}

    assert len(PUNTOS_CUADRICULA) == 13
    assert tuple(sorted(PUNTOS_CUADRICULA)) == PUNTOS_CUADRICULA
    assert posiciones_anteriores.issubset(PUNTOS_CUADRICULA)


def test_parcelas_de_ejemplo_tienen_todas_un_contorno_dibujado():
    parcelas = _crear_parcelas_demo()

    assert [parcela["name"] for parcela in parcelas] == [
        "Huerto de prácticas",
        "Invernadero norte",
        "Parcela de frutales",
    ]
    assert all(parcela["shape"] == "dibujada" for parcela in parcelas)
    assert all(parcela["shape_label"] == "Dibujada" for parcela in parcelas)
    assert all(parcela["outline"].startswith("polygon(") for parcela in parcelas)
    assert [parcela["demo_alert"] for parcela in parcelas] == [
        "warning",
        "danger",
        "",
    ]


def test_nueva_parcela_se_crea_siempre_con_forma_dibujada_y_contorno():
    parcela = _crear_parcela_dibujada(
        "10",
        "Bancal",
        250,
        [
            {"x": 7, "y": 7},
            {"x": 50, "y": 7},
            {"x": 50, "y": 50},
            {"x": 7, "y": 50},
        ],
    )

    assert parcela["shape"] == "dibujada"
    assert parcela["shape_label"] == "Dibujada"
    assert parcela["demo_alert"] == ""
    assert parcela["outline"] == (
        "polygon(7% 7%, 50% 7%, 50% 50%, 7% 50%)"
    )
    assert parcela["stroke_points"] == "7,7 50,7 50,50 7,50"


def test_sectores_afectados_muestran_los_estados_de_aviso_de_ejemplo():
    sectores = _crear_sectores_demo()

    assert {
        sector["id"]: sector["demo_alert"]
        for sector in sectores
        if sector["demo_alert"]
    } == {"1": "warning", "5": "danger"}


def test_etiqueta_sector_queda_dentro_de_parcela_dibujada_a_media_cuadricula():
    sector = {"label_x": "50", "label_y": "50"}
    parcela = [(7, 7), (50, 7), (50, 93), (7, 93)]

    _ubicar_etiqueta_sector(sector, parcela)

    assert sector["label_x"] == "28.50"
    assert sector["label_y"] == "50.00"


def test_etiqueta_elige_un_punto_centrado_con_margen_en_parcela_concava():
    sector = {"label_x": "50", "label_y": "50"}
    parcela = [
        (7, 7),
        (36, 7),
        (36, 21),
        (93, 21),
        (93, 36),
        (36, 36),
        (36, 93),
        (7, 93),
    ]

    _ubicar_etiqueta_sector(sector, parcela)

    punto = (float(sector["label_x"]), float(sector["label_y"]))
    assert _punto_en_poligono(punto, parcela, incluir_borde=False)
    assert punto == pytest.approx((22.03, 30.44), abs=0.1)


def test_punto_etiqueta_de_sector_concavo_queda_dentro_del_contorno():
    poligono = [
        (10, 10),
        (30, 10),
        (30, 70),
        (70, 70),
        (70, 10),
        (90, 10),
        (90, 90),
        (10, 90),
    ]

    centro = _punto_interior_poligono(poligono)

    assert _punto_en_poligono(centro, poligono, incluir_borde=False)


def test_construir_contorno_convierte_vertices_a_poligono_css():
    vertices = [
        {"x": 10, "y": 10},
        {"x": 80, "y": 10},
        {"x": 60, "y": 80},
        {"x": 20, "y": 60},
    ]

    assert construir_contorno(vertices) == (
        "polygon(10% 10%, 80% 10%, 60% 80%, 20% 60%)"
    )


@pytest.mark.parametrize(
    ("vertices", "error"),
    [
        ([{"x": 10, "y": 10}, {"x": 80, "y": 10}], "al menos tres"),
        (
            [{"x": 10, "y": 10}, {"x": 80, "y": 10}, {"x": 10, "y": 10}],
            "repetir vértices",
        ),
        (
            [{"x": 10, "y": 10}, {"x": 80, "y": 10}, {"x": 110, "y": 80}],
            "dentro de la cuadrícula",
        ),
        (
            [{"x": 10, "y": 10}, {"x": 50, "y": 50}, {"x": 90, "y": 90}],
            "formar una superficie",
        ),
    ],
)
def test_construir_contorno_rechaza_formas_invalidas(vertices, error):
    with pytest.raises(ValueError, match=error):
        construir_contorno(vertices)


def test_construir_contorno_rechaza_lados_que_se_cruzan():
    vertices = [
        {"x": 10, "y": 10},
        {"x": 80, "y": 80},
        {"x": 10, "y": 80},
        {"x": 80, "y": 20},
        {"x": 90, "y": 90},
    ]

    with pytest.raises(ValueError, match="cruzarse"):
        construir_contorno(vertices)


def test_sector_dibujado_admite_huecos_y_bordes_compartidos():
    parcela = {"shape": "rectangulo"}
    sector_existente = {
        "left": "0",
        "top": "0",
        "width": "50",
        "height": "100",
        "outline": "",
    }
    vertices = [
        {"x": 50, "y": 0},
        {"x": 100, "y": 0},
        {"x": 100, "y": 100},
        {"x": 50, "y": 100},
    ]

    contorno = validar_sector_dibujado(parcela, vertices, [sector_existente])

    assert contorno == "polygon(50% 0%, 100% 0%, 100% 100%, 50% 100%)"


@pytest.mark.parametrize(
    ("parcela", "vertices", "error"),
    [
        (
            {"shape": "circulo"},
            [
                {"x": 7, "y": 7},
                {"x": 93, "y": 7},
                {"x": 93, "y": 93},
                {"x": 7, "y": 93},
            ],
            "dentro de la parcela",
        ),
        (
            {
                "shape": "dibujada",
                "outline": (
                    "polygon(0% 0%, 100% 0%, 100% 100%, 60% 100%, "
                    "60% 40%, 40% 40%, 40% 100%, 0% 100%)"
                ),
            },
            [
                {"x": 20, "y": 80},
                {"x": 80, "y": 80},
                {"x": 80, "y": 90},
                {"x": 20, "y": 90},
            ],
            "lados del sector",
        ),
    ],
)
def test_sector_dibujado_rechaza_geometria_fuera_de_la_parcela(
    parcela, vertices, error
):
    with pytest.raises(ValueError, match=error):
        validar_sector_dibujado(parcela, vertices, [])


def test_sector_dibujado_rechaza_solapamiento_parcial():
    sector_existente = {
        "left": "40",
        "top": "20",
        "width": "40",
        "height": "50",
        "outline": "",
    }
    vertices = [
        {"x": 20, "y": 30},
        {"x": 60, "y": 30},
        {"x": 60, "y": 60},
        {"x": 20, "y": 60},
    ]

    with pytest.raises(ValueError, match="no pueden solaparse"):
        validar_sector_dibujado({"shape": "rectangulo"}, vertices, [sector_existente])


def test_sector_dibujado_rechaza_sector_contenido_en_otro():
    sector_existente = {
        "left": "10",
        "top": "10",
        "width": "80",
        "height": "80",
        "outline": "",
    }
    vertices = [
        {"x": 30, "y": 30},
        {"x": 70, "y": 30},
        {"x": 70, "y": 70},
        {"x": 30, "y": 70},
    ]

    with pytest.raises(ValueError, match="no pueden solaparse"):
        validar_sector_dibujado({"shape": "rectangulo"}, vertices, [sector_existente])


def test_sector_dibujado_rechaza_solapamiento_de_igual_forma():
    sector_existente = {
        "left": "10",
        "top": "10",
        "width": "30",
        "height": "30",
        "outline": "",
    }
    vertices = [
        {"x": 10, "y": 10},
        {"x": 40, "y": 10},
        {"x": 40, "y": 40},
        {"x": 10, "y": 40},
    ]

    with pytest.raises(ValueError, match="no pueden solaparse"):
        validar_sector_dibujado({"shape": "rectangulo"}, vertices, [sector_existente])


def test_calcula_media_de_sectores_con_lectura_y_omite_los_sin_datos():
    sectores = [
        {"temperature": "20", "soil_moisture": "40"},
        {"temperature": "24", "soil_moisture": ""},
        {"temperature": "", "soil_moisture": "60"},
    ]

    medias = {media["type"]: media for media in calcular_medias(sectores)}

    assert medias["temperature"]["value"] == "22.0"
    assert medias["temperature"]["sector_count"] == "2"
    assert medias["soil_moisture"]["value"] == "50.0"
    assert medias["soil_moisture"]["sector_count"] == "2"
    assert medias["light"]["value"] == ""


@pytest.mark.parametrize(
    ("orientacion", "expected"),
    [
        ("vertical", ("0", "50.00", "50.00", "50.00")),
        ("horizontal", ("0", "50.00", "50.00", "50.00")),
    ],
)
def test_dividir_sector_conserva_el_area_y_los_limites(orientacion, expected):
    sector = {
        "left": "0",
        "top": "0",
        "width": "100",
        "height": "100",
        "temperature": "23",
        "has_temperature": "yes",
    }

    existente, nuevo = dividir_sector(sector, orientacion)

    if orientacion == "vertical":
        limites = (
            existente["left"],
            nuevo["left"],
            existente["width"],
            nuevo["width"],
        )
    else:
        limites = (
            existente["top"],
            nuevo["top"],
            existente["height"],
            nuevo["height"],
        )
    assert limites == expected
    assert existente["temperature"] == "23"
    assert nuevo["temperature"] == ""
    assert existente["has_temperature"] == "yes"
    assert nuevo["has_temperature"] == "no"


def test_division_rechaza_orientacion_desconocida():
    with pytest.raises(ValueError, match="vertical u horizontal"):
        dividir_sector({"left": "0", "top": "0", "width": "100", "height": "100"}, "diagonal")


def test_media_rechaza_lecturas_no_numericas():
    with pytest.raises(ValueError, match="temperatura"):
        calcular_medias([{"temperature": "caliente"}])


def test_eliminar_parcela_tambien_elimina_sus_sectores_sin_afectar_otras():
    parcelas = [{"id": "1"}, {"id": "2"}]
    sectores = [
        {"id": "10", "parcel_id": "1"},
        {"id": "11", "parcel_id": "1"},
        {"id": "20", "parcel_id": "2"},
    ]

    parcelas_restantes, sectores_restantes = eliminar_parcela_de_datos(
        parcelas, sectores, "1"
    )

    assert parcelas_restantes == [{"id": "2"}]
    assert sectores_restantes == [{"id": "20", "parcel_id": "2"}]


def test_eliminar_parcela_inexistente_devuelve_error_claro():
    with pytest.raises(ValueError, match="ya no existe"):
        eliminar_parcela_de_datos([{"id": "1"}], [], "no-existe")


def test_eliminar_sector_quita_solo_el_sector_seleccionado():
    sectores = [
        {"id": "10", "parcel_id": "1"},
        {"id": "11", "parcel_id": "1"},
        {"id": "20", "parcel_id": "2"},
    ]

    assert eliminar_sector_de_datos(sectores, "1", "10") == [
        {"id": "11", "parcel_id": "1"},
        {"id": "20", "parcel_id": "2"},
    ]


@pytest.mark.parametrize(
    ("parcela_id", "sector_id"),
    [("1", "no-existe"), ("2", "10")],
)
def test_eliminar_sector_rechaza_sector_ausente_o_de_otra_parcela(
    parcela_id, sector_id
):
    with pytest.raises(ValueError, match="ya no existe en esta parcela"):
        eliminar_sector_de_datos(
            [{"id": "10", "parcel_id": "1"}],
            parcela_id,
            sector_id,
        )
