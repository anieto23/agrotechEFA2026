import reflex as rx

from . import colors


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
                        size=32,
                        color=color,
                    ),
                    padding="5px",
                    border_radius="12px",
                    background=colors.ICON_BACKGROUND,
                ),
                rx.spacer(),
                rx.badge("Simulado", color_scheme="gray"),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(title, color=colors.TEXT, size="2"),
                rx.hstack(
                    rx.heading(value, size="7", color=color),
                    rx.text(unit, color=colors.TEXT, size="2"),
                    align="baseline",
                    spacing="1",
                ),
                rx.text(description, color=colors.TEXT, size="1"),
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
