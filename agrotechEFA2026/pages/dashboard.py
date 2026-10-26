import reflex as rx

from ..components import colors
from ..components.sensor_card import sensor_card


def dashboard() -> rx.Component:
    """Página principal de Agrotech."""

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.image(
                        src="/logo.png",
                        alt="Logo de Agrotech",
                        width="64px",
                        height="64px",
                        object_fit="contain",
                    ),
                    rx.vstack(
                        rx.heading("Agrotech", size="6", color=colors.TEXT),
                        rx.text(
                            "Agricultura inteligente",
                            color=colors.TEXT,
                            size="2",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.spacer(),
                rx.badge(
                    "Proyecto de demostración",
                    color_scheme="green",
                ),
                width="100%",
                align="center",
                wrap="wrap",
            ),
            rx.divider(),
            rx.vstack(
                rx.heading(
                    "Panel de control",
                    size="8",
                    color=colors.TEXT,
                ),
                rx.text(
                    "Consulta las condiciones ambientales "
                    "de tu parcela.",
                    color=colors.TEXT,
                    size="3",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            rx.grid(
                sensor_card(
                    "Temperatura",
                    "24.6",
                    "°C",
                    "Temperatura ambiental",
                    "thermometer",
                    colors.SENSOR["temperatura"],
                ),
                sensor_card(
                    "Humedad del suelo",
                    "42",
                    "%",
                    "Contenido de humedad",
                    "droplets",
                    colors.SENSOR["humedad_suelo"],
                ),
                sensor_card(
                    "Humedad ambiental",
                    "61",
                    "%",
                    "Humedad relativa del aire",
                    "cloud",
                    colors.SENSOR["humedad_ambiental"],
                ),
                sensor_card(
                    "Luminosidad",
                    "18500",
                    "lx",
                    "Intensidad luminosa",
                    "sun",
                    colors.SENSOR["luminosidad"],
                ),
                columns={
                    "initial": "1",
                    "sm": "2",
                    "lg": "4",
                },
                spacing="4",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon(
                            tag="map",
                            size=22,
                            color=colors.PARCEL_STATUS,
                        ),
                        rx.heading(
                            "Estado de la parcela",
                            size="4",
                            color=colors.TEXT,
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Todavía no hay sensores conectados. "
                        "Los valores mostrados son datos "
                        "ficticios para probar la interfaz.",
                        color=colors.TEXT,
                        size="2",
                    ),
                    rx.badge(
                        "Modo de prueba",
                        color_scheme="green",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                width="100%",
            ),
            spacing="6",
            width="100%",
            max_width="1200px",
            padding="24px",
            align="start",
        ),
        min_height="100vh",
        width="100%",
        background=colors.DASHBOARD_BACKGROUND,
    )
