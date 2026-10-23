
import reflex as rx


class State(rx.State):
    """Estado de la aplicación."""

    pass


def sensor_card(
    title: str,
    value: str,
    unit: str,
    description: str,
    icon: str,
    color: str,
) -> rx.Component:
    """Tarjeta para mostrar la lectura de un sensor."""

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(
                        tag=icon,
                        size=24,
                        color=color,
                    ),
                    padding="10px",
                    border_radius="12px",
                    background="#CACACA",
                ),
                rx.spacer(),
                rx.badge("Simulado", color_scheme="gray"),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(title, color="#CACACA", size="2"),
                rx.hstack(
                    rx.heading(value, size="7", color=color),
                    rx.text(unit, color="#CACACA", size="2"),
                    align="baseline",
                    spacing="1",
                ),
                rx.text(description, color="#CACACA", size="1"),
                width="100%",
                align="start",
                spacing="2",
            ),
            width="100%",
            spacing="4",
            align="start",
        ),
        width="100%",
        height="100%",
    )


def index() -> rx.Component:
    """Página principal de Agrotech."""

    return rx.box(
        rx.vstack(
            # Cabecera
            rx.hstack(
                rx.hstack(
                    rx.icon(
                        tag="sprout",
                        size=32,
                        color="#16A34A",
                    ),
                    rx.vstack(
                        rx.heading("Agrotech", size="6",color="#CACACA"),
                        rx.text(
                            "Agricultura inteligente",
                            color="#CACACA",
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

            # Introducción
            rx.vstack(
                rx.heading(
                    "Panel de control",
                    size="8",
                    color="#CACACA"
                ),
                rx.text(
                    "Consulta las condiciones ambientales "
                    "de tu parcela.",
                    color="#CACACA",
                    size="3",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),

            # Indicadores
            rx.grid(
                sensor_card(
                    "Temperatura",
                    "24.6",
                    "°C",
                    "Temperatura ambiental",
                    "thermometer",
                    "#EA580C",
                ),
                sensor_card(
                    "Humedad del suelo",
                    "42",
                    "%",
                    "Contenido de humedad",
                    "droplets",
                    "#2563EB",
                ),
                sensor_card(
                    "Humedad ambiental",
                    "61",
                    "%",
                    "Humedad relativa del aire",
                    "cloud",
                    "#0891B2",
                ),
                sensor_card(
                    "Luminosidad",
                    "18500",
                    "lx",
                    "Intensidad luminosa",
                    "sun",
                    "#CA8A04",
                ),
                columns={
                    "initial": "1",
                    "sm": "2",
                    "lg": "4",
                },
                spacing="4",
                width="100%",
            ),

            # Estado de la parcela
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon(
                            tag="map",
                            size=22,
                            color="#16A34A",
                        ),
                        rx.heading(
                            "Estado de la parcela",
                            size="4",
                            color="#CACACA"
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Todavía no hay sensores conectados. "
                        "Los valores mostrados son datos "
                        "ficticios para probar la interfaz.",
                        color="#CACACA",
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
        background="#272727",
    )


app = rx.App()
app.add_page(index, title="Agrotech | Panel de control")
