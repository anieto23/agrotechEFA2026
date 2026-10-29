import reflex as rx

from . import colors
from ..state.dashboard_state import DashboardState


def sector_cell(sector: dict[str, rx.Var]) -> rx.Component:
    """Sector rectangular o poligonal, ubicado en porcentajes del plano."""

    return rx.box(
        rx.button(
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            padding="2",
            border="1px solid #CACACA",
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
        rx.vstack(
            rx.text(sector["name"], size="2", weight="bold"),
            rx.text(sector["crop_icon"], size="5"),
            rx.text(sector["crop"], size="1"),
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
        rx.foreach(DashboardState.sectores_parcela, sector_cell),
        position="relative",
        width="100%",
        max_width=rx.cond(forma == "circulo", "480px", "760px"),
        aspect_ratio=rx.cond(
            (forma == "circulo") | (forma == "dibujada"),
            "1 / 1",
            "3 / 2",
        ),
        overflow="hidden",
        clip_path=recorte,
        background="#202020",
        border="2px solid #747474",
        border_radius="12px",
        role="group",
        aria_label="Plano de parcela dividido en sectores",
    )
