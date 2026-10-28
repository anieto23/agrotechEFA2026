import pytest

from agrotechEFA2026.state.dashboard_state import (
    calcular_medias,
    dividir_sector,
    eliminar_parcela_de_datos,
)


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
