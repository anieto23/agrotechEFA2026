import reflex as rx

from ..components import colors
from ..components.parcel_map import parcela_map
from ..components.sensor_card import sensor_card
from ..state.dashboard_state import CULTIVOS, SENSORES, DashboardState


def cabecera() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.image(
                src="/logo.png",
                alt="Logo de Agrotech",
                width="56px",
                height="56px",
                object_fit="contain",
            ),
            rx.vstack(
                rx.heading("Agrotech", size="6", color=colors.TEXT),
                rx.text("Agricultura inteligente", color=colors.TEXT, size="2"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        rx.spacer(),
        rx.badge("Maqueta interactiva", color_scheme="green"),
        width="100%",
        align="center",
        wrap="wrap",
    )


def tarjeta_parcela(parcela: dict[str, rx.Var]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="map", size=22, color=colors.PARCEL_STATUS),
                rx.badge(parcela["shape_label"], color_scheme="gray"),
                width="100%",
                justify="between",
                align="center",
            ),
            rx.heading(parcela["name"], size="4", color=colors.TEXT),
            rx.text(parcela["area_m2"], " m²", color=colors.TEXT, size="3"),
            rx.text(
                "Abre la parcela para consultar sus sectores y mediciones.",
                color=colors.TEXT,
                size="2",
            ),
            rx.button(
                "Abrir parcela",
                on_click=DashboardState.abrir_parcela(parcela["id"]),
                width="100%",
                color_scheme="green",
            ),
            rx.cond(
                DashboardState.parcela_id_pendiente_eliminar == parcela["id"],
                rx.vstack(
                    rx.text(
                        "¿Eliminar esta parcela y todos sus sectores?",
                        color=colors.TEXT,
                        size="2",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            on_click=DashboardState.cancelar_eliminacion_parcela,
                            variant="soft",
                            width="100%",
                        ),
                        rx.button(
                            "Confirmar eliminación",
                            on_click=DashboardState.confirmar_eliminacion_parcela,
                            color_scheme="red",
                            width="100%",
                        ),
                        width="100%",
                        wrap="wrap",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.button(
                    "Eliminar parcela",
                    on_click=DashboardState.solicitar_eliminacion_parcela(
                        parcela["id"]
                    ),
                    variant="soft",
                    color_scheme="red",
                    width="100%",
                ),
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        width="100%",
        height="100%",
    )


def formulario_parcela() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Añadir parcela", size="4", color=colors.TEXT),
            rx.text(
                "Indica su superficie y elige una forma. Los cambios se guardan "
                "solo durante esta sesión de demostración.",
                color=colors.TEXT,
                size="2",
            ),
            rx.input(
                placeholder="Nombre de la parcela",
                value=DashboardState.nuevo_nombre,
                on_change=DashboardState.actualizar_nombre,
                max_length=80,
                width="100%",
                aria_label="Nombre de la parcela",
            ),
            rx.input(
                placeholder="Superficie en m²",
                type="number",
                min="0.01",
                step="any",
                value=DashboardState.nueva_area,
                on_change=DashboardState.actualizar_area,
                width="100%",
                aria_label="Superficie de la parcela en metros cuadrados",
            ),
            rx.select(
                ["Rectángulo", "Cuadrado", "Círculo", "Polígono"],
                value=DashboardState.nueva_forma,
                on_change=DashboardState.actualizar_forma,
                width="100%",
                aria_label="Forma de la parcela",
            ),
            rx.cond(
                DashboardState.error_formulario != "",
                rx.callout(
                    DashboardState.error_formulario,
                    icon="triangle_alert",
                    color_scheme="red",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(
                DashboardState.mensaje_formulario != "",
                rx.callout(
                    DashboardState.mensaje_formulario,
                    icon="circle_check",
                    color_scheme="green",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.button(
                "Añadir parcela",
                on_click=DashboardState.crear_parcela,
                width="100%",
                color_scheme="green",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        width="100%",
    )


def tarjeta_media(media: dict[str, rx.Var]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(tag=media["icon"], size=20, color=media["color"]),
                rx.text(media["name"], color=colors.TEXT, size="2"),
                align="center",
                spacing="2",
            ),
            rx.hstack(
                rx.heading(
                    rx.cond(media["value"] != "", media["value"], "—"),
                    size="6",
                    color=media["color"],
                ),
                rx.text(media["unit"], color=colors.TEXT, size="2"),
                align="baseline",
                spacing="1",
            ),
            rx.text(
                rx.cond(
                    media["sector_count"] != "0",
                    "Media de " + media["sector_count"] + " sectores con lectura",
                    "Sin lecturas disponibles",
                ),
                color=colors.TEXT,
                size="1",
            ),
            spacing="2",
            align="start",
        ),
        width="100%",
    )


def detalle_parcela() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.button(
                "← Parcelas",
                on_click=DashboardState.volver_al_panel,
                variant="soft",
            ),
            rx.spacer(),
            rx.badge(DashboardState.parcela_seleccionada["shape_label"]),
            align="center",
            width="100%",
            wrap="wrap",
        ),
        rx.vstack(
            rx.heading(
                DashboardState.parcela_seleccionada["name"],
                size="8",
                color=colors.TEXT,
            ),
            rx.text(
                DashboardState.parcela_seleccionada["area_m2"],
                " m² · ",
                DashboardState.parcela_seleccionada["shape_label"],
                color=colors.TEXT,
                size="3",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.vstack(
            rx.heading("Media de la parcela", size="5", color=colors.TEXT),
            rx.text(
                "Media aritmética de los sectores que tienen una lectura "
                "para cada magnitud.",
                color=colors.TEXT,
                size="2",
            ),
            rx.grid(
                rx.foreach(DashboardState.medias_parcela, tarjeta_media),
                columns={"initial": "1", "sm": "2", "lg": "4"},
                spacing="3",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        rx.vstack(
            rx.hstack(
                rx.heading("Sectores", size="5", color=colors.TEXT),
                rx.spacer(),
                rx.text(
                    "Pulsa un sector para abrir sus mediciones.",
                    color=colors.TEXT,
                    size="2",
                ),
                width="100%",
                align="center",
                wrap="wrap",
            ),
            parcela_map(),
            rx.text(
                "Cada división crea un sector nuevo; puedes seguir subdividiendo "
                "cualquiera de ellos.",
                color=colors.TEXT,
                size="2",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        spacing="6",
        width="100%",
    )


def tarjeta_lectura(lectura: dict[str, rx.Var]) -> rx.Component:
    return sensor_card(
        lectura["name"],
        rx.cond(lectura["value"] != "", lectura["value"], "Sin lectura"),
        lectura["unit"],
        "Lectura del sector seleccionado",
        lectura["icon"],
        lectura["color"],
    )


def detalle_sector() -> rx.Component:
    return rx.vstack(
        rx.button(
            "← Volver a la parcela",
            on_click=DashboardState.volver_a_parcela,
            variant="soft",
            align_self="start",
        ),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text(
                        DashboardState.sector_seleccionado["crop_icon"],
                        size="8",
                    ),
                    rx.vstack(
                        rx.heading(
                            DashboardState.sector_seleccionado["name"],
                            size="7",
                            color=colors.TEXT,
                        ),
                        rx.text(
                            DashboardState.parcela_seleccionada["name"],
                            color=colors.TEXT,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.text("Cultivo del sector", color=colors.TEXT, size="2"),
                rx.select(
                    list(CULTIVOS),
                    value=DashboardState.sector_seleccionado["crop"],
                    on_change=DashboardState.cambiar_cultivo,
                    width="100%",
                    aria_label="Cultivo del sector",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            width="100%",
        ),
        rx.vstack(
            rx.heading("Mediciones del sector", size="5", color=colors.TEXT),
            rx.cond(
                DashboardState.lecturas_sector.length() > 0,
                rx.grid(
                    rx.foreach(DashboardState.lecturas_sector, tarjeta_lectura),
                    columns={"initial": "1", "sm": "2", "lg": "4"},
                    spacing="4",
                    width="100%",
                ),
                rx.callout(
                    "Este sector todavía no tiene sensores.",
                    icon="info",
                    color_scheme="gray",
                    width="100%",
                ),
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.heading("Añadir sensor", size="4", color=colors.TEXT),
                rx.hstack(
                    rx.select(
                        [sensor[1] for sensor in SENSORES],
                        value=DashboardState.tipo_sensor_nuevo,
                        on_change=DashboardState.actualizar_tipo_sensor,
                        width="100%",
                    ),
                    rx.button(
                        "Añadir",
                        on_click=DashboardState.agregar_sensor(
                            DashboardState.tipo_sensor_nuevo
                        ),
                        color_scheme="green",
                    ),
                    width="100%",
                    wrap="wrap",
                ),
                rx.cond(
                    DashboardState.mensaje_sensor != "",
                    rx.text(
                        DashboardState.mensaje_sensor,
                        color=colors.TEXT,
                        size="2",
                    ),
                    rx.fragment(),
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.heading("Dividir este sector", size="4", color=colors.TEXT),
                rx.text(
                    "El sector actual conserva sus sensores; el nuevo empieza "
                    "vacío para que le añadas los suyos.",
                    color=colors.TEXT,
                    size="2",
                ),
                rx.hstack(
                    rx.button(
                        "Dividir en vertical",
                        on_click=DashboardState.dividir_sector("vertical"),
                        color_scheme="green",
                        variant="soft",
                    ),
                    rx.button(
                        "Dividir en horizontal",
                        on_click=DashboardState.dividir_sector("horizontal"),
                        color_scheme="green",
                        variant="soft",
                    ),
                    width="100%",
                    wrap="wrap",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            width="100%",
        ),
        spacing="5",
        width="100%",
    )


def dashboard() -> rx.Component:
    """Página de parcelas, sectores y mediciones de demostración."""

    return rx.box(
        rx.vstack(
            cabecera(),
            rx.divider(),
            rx.cond(
                DashboardState.parcela_id_seleccionada == "",
                rx.vstack(
                    rx.vstack(
                        rx.heading("Panel de control", size="8", color=colors.TEXT),
                        rx.text(
                            "Gestiona tus parcelas, sus sectores y los sensores de cada cultivo.",
                            color=colors.TEXT,
                            size="3",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    formulario_parcela(),
                    rx.heading("Mis parcelas", size="5", color=colors.TEXT),
                    rx.cond(
                        DashboardState.parcelas.length() > 0,
                        rx.grid(
                            rx.foreach(DashboardState.parcelas, tarjeta_parcela),
                            columns={"initial": "1", "sm": "2", "lg": "3"},
                            spacing="4",
                            width="100%",
                        ),
                        rx.callout(
                            "Todavía no hay parcelas. Añade una para empezar.",
                            icon="info",
                            color_scheme="gray",
                            width="100%",
                        ),
                    ),
                    spacing="4",
                    align="start",
                    width="100%",
                ),
                rx.cond(
                    DashboardState.sector_abierto,
                    detalle_sector(),
                    detalle_parcela(),
                ),
            ),
            spacing="6",
            width="100%",
            max_width="1200px",
            padding={"initial": "16px", "md": "24px"},
            align="start",
        ),
        min_height="100vh",
        width="100%",
        background=colors.DASHBOARD_BACKGROUND,
    )
