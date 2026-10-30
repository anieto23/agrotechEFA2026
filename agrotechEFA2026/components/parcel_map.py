import reflex as rx

from . import colors
from ..state.dashboard_state import DashboardState


def sector_cell(sector: dict[str, rx.Var]) -> rx.Component:
    """Sector rectangular o poligonal, ubicado en porcentajes del plano."""

    return rx.box(
        rx.box(
            rx.button(
                position="absolute",
                top="0",
                left="0",
                width="100%",
                height="100%",
                padding="2",
                border="0",
                border_radius="0",
                background="#343434",
                clip_path=rx.cond(
                    sector["outline"] != "",
                    sector["outline"],
                    "inset(0)",
                ),
                pointer_events="auto",
                _hover={"background": "#3D5A43"},
                on_click=DashboardState.abrir_sector(sector["id"]),
                aria_label=f"Abrir {sector['name']}, cultivo {sector['crop']}",
            ),
            rx.el.svg(
                rx.el.polygon(
                    points=sector["stroke_points"],
                    fill="none",
                    stroke=colors.TEXT,
                    stroke_width="2",
                    vector_effect="non-scaling-stroke",
                ),
                position="absolute",
                top="0",
                left="0",
                width="100%",
                height="100%",
                view_box="0 0 100 100",
                preserve_aspect_ratio="none",
                pointer_events="none",
            ),
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
        ),
        rx.vstack(
            rx.text(sector["name"], size="2", weight="bold"),
            rx.text(sector["crop_icon"], size="5"),
            rx.text(sector["crop"], size="1"),
            rx.cond(
                sector["demo_alert"] == "warning",
                rx.badge(
                    rx.icon(tag="triangle-alert", size=14),
                    rx.text("Aviso de ejemplo", size="1"),
                    color_scheme="orange",
                ),
                rx.cond(
                    sector["demo_alert"] == "danger",
                    rx.badge(
                        rx.icon(tag="octagon-alert", size=14),
                        rx.text("Peligro de ejemplo", size="1"),
                        color_scheme="red",
                    ),
                    rx.fragment(),
                ),
            ),
            spacing="1",
            align="center",
            justify="center",
            position="absolute",
            top=sector["label_y"] + "%",
            left=sector["label_x"] + "%",
            transform="translate(-50%, -50%)",
            max_width="90%",
            pointer_events="none",
            z_index="1",
        ),
        position="absolute",
        left=rx.cond(sector["outline"] != "", "0%", sector["left"] + "%"),
        top=rx.cond(sector["outline"] != "", "0%", sector["top"] + "%"),
        width=rx.cond(sector["outline"] != "", "100%", sector["width"] + "%"),
        height=rx.cond(sector["outline"] != "", "100%", sector["height"] + "%"),
        color=colors.TEXT,
        white_space="normal",
        pointer_events="none",
    )


def contorno_parcela_svg() -> rx.Component:
    """Dibuja el borde de la parcela seleccionada."""
    forma = DashboardState.parcela_seleccionada["shape"]
    puntos_contorno = rx.cond(
        forma == "dibujada",
        DashboardState.parcela_seleccionada["stroke_points"],
        rx.cond(
            forma == "cuadrado",
            "16,0 84,0 84,100 16,100",
            rx.cond(
                forma == "poligono",
                "18,0 83,8 100,42 76,100 15,92 0,35",
                "0,0 100,0 100,100 0,100",
            ),
        ),
    )

    return rx.el.svg(
        rx.cond(
            forma == "circulo",
            rx.el.ellipse(
                cx="50",
                cy="50",
                rx="49",
                ry="48",
                fill="none",
                stroke=colors.TEXT,
                stroke_width="2",
                vector_effect="non-scaling-stroke",
            ),
            rx.el.polygon(
                points=puntos_contorno,
                fill="none",
                stroke=colors.TEXT,
                stroke_width="2",
                vector_effect="non-scaling-stroke",
            ),
        ),
        position="absolute",
        top="0",
        left="0",
        width="100%",
        height="100%",
        view_box="0 0 100 100",
        preserve_aspect_ratio="none",
        pointer_events="none",
    )


def parcela_map() -> rx.Component:
    """Vista esquemática de la forma y los sectores de una parcela."""

    forma = DashboardState.parcela_seleccionada["shape"]
    recorte = rx.cond(
        forma == "dibujada",
        DashboardState.parcela_seleccionada["outline"],
        rx.cond(
            forma == "circulo",
            "ellipse(49% 48% at 50% 50%)",
            rx.cond(
                forma == "cuadrado",
                "inset(0 16%)",
                rx.cond(
                    forma == "poligono",
                    "polygon(18% 0, 83% 8%, 100% 42%, 76% 100%, 15% 92%, 0 35%)",
                    "inset(0)",
                ),
            ),
        ),
    )

    return rx.box(
        rx.box(
            rx.foreach(DashboardState.sectores_parcela, sector_cell),
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            overflow="hidden",
            clip_path=recorte,
            background="#202020",
        ),
        contorno_parcela_svg(),
        position="relative",
        width="100%",
        max_width=rx.cond(forma == "circulo", "480px", "760px"),
        aspect_ratio=rx.cond(
            (forma == "circulo") | (forma == "dibujada"),
            "1 / 1",
            "3 / 2",
        ),
        overflow="visible",
        border_radius="12px",
        role="group",
        aria_label="Plano de parcela dividido en sectores",
    )
