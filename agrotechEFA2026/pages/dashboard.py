import reflex as rx

from ..components import colors
from ..components.parcel_map import parcela_map
from ..components.sensor_card import sensor_card
from ..state.dashboard_state import (
    CULTIVOS,
    PUNTOS_CUADRICULA,
    SENSORES,
    DashboardState,
)


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
                rx.cond(
                    parcela["demo_alert"] == "warning",
                    rx.badge(
                        rx.icon(tag="triangle-alert", size=16),
                        rx.text("Aviso de ejemplo"),
                        color_scheme="orange",
                    ),
                    rx.cond(
                        parcela["demo_alert"] == "danger",
                        rx.badge(
                            rx.icon(tag="octagon-alert", size=16),
                            rx.text("Peligro de ejemplo"),
                            color_scheme="red",
                        ),
                        rx.fragment(),
                    ),
                ),
                rx.spacer(),
                rx.button(
                    rx.icon(tag="trash-2", size=16, color="var(--red-9)"),
                    on_click=DashboardState.solicitar_eliminacion_parcela(
                        parcela["id"]
                    ),
                    variant="ghost",
                    color_scheme="red",
                    size="2",
                    padding="1",
                    aria_label=f"Eliminar parcela {parcela['name']}",
                ),
                width="100%",
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
                rx.fragment(),
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        width="100%",
        height="100%",
    )


def punto_contorno(punto: dict[str, rx.Var]) -> rx.Component:
    return rx.box(
        position="absolute",
        left=punto["x"] + "%",
        top=punto["y"] + "%",
        transform="translate(-50%, -50%)",
        width="16px",
        height="16px",
        border_radius="50%",
        background="#E7B85C",
        border="3px solid #202020",
        box_shadow="0 0 0 2px #FFFFFF",
        pointer_events="none",
        z_index="2",
    )


def punto_disponible() -> rx.Component:
    return rx.box(
        width="10px",
        height="10px",
        border="2px solid #E7B85C",
        border_radius="50%",
        background="#202020",
        pointer_events="none",
    )


def lineas_cuadricula() -> list[rx.Component]:
    return [
        *[
            rx.box(
                position="absolute",
                top="0",
                bottom="0",
                left=f"{x}%",
                width="1px",
                background="#646464",
                pointer_events="none",
            )
            for x in PUNTOS_CUADRICULA
        ],
        *[
            rx.box(
                position="absolute",
                left="0",
                right="0",
                top=f"{y}%",
                height="1px",
                background="#646464",
                pointer_events="none",
            )
            for y in PUNTOS_CUADRICULA
        ],
    ]


def formulario_dibujo() -> rx.Component:
    celdas = [
        rx.button(
            punto_disponible(),
            on_click=DashboardState.agregar_vertice(x, y),
            aria_label=f"Añadir vértice en {x}%, {y}%",
            position="absolute",
            left=f"{x}%",
            top=f"{y}%",
            transform="translate(-50%, -50%)",
            width="28px",
            height="28px",
            padding="0",
            border="0",
            border_radius="50%",
            background="transparent",
            z_index="1",
            _hover={"background": "#3D5A43"},
        )
        for y in PUNTOS_CUADRICULA
        for x in PUNTOS_CUADRICULA
    ]

    return rx.vstack(
        rx.text(
            "Toca un punto vacío para elegirlo; los puntos dorados grandes ya están "
            "seleccionados.",
            color=colors.TEXT,
            size="2",
        ),
        rx.box(
            *lineas_cuadricula(),
            *celdas,
            rx.cond(
                DashboardState.vertices_nueva_parcela.length() >= 3,
                rx.box(
                    position="absolute",
                    top="0",
                    right="0",
                    bottom="0",
                    left="0",
                    background="#3D5A43",
                    opacity="0.6",
                    clip_path=DashboardState.contorno_previsualizacion,
                    pointer_events="none",
                ),
                rx.fragment(),
            ),
            rx.foreach(DashboardState.vertices_nueva_parcela, punto_contorno),
            position="relative",
            width="100%",
            max_width="480px",
            aspect_ratio="1 / 1",
            overflow="hidden",
            border="1px solid #747474",
            border_radius="8px",
            role="group",
            aria_label="Cuadrícula para dibujar el contorno de la parcela",
        ),
        rx.text(
            "Vértices marcados: ",
            DashboardState.vertices_nueva_parcela.length(),
            color=colors.TEXT,
            size="2",
        ),
        rx.cond(
            DashboardState.contorno_cerrado,
            rx.badge("Contorno cerrado", color_scheme="green"),
            rx.badge("Contorno en edición", color_scheme="gray"),
        ),
        rx.hstack(
            rx.cond(
                DashboardState.contorno_cerrado,
                rx.button(
                    "Volver a editar",
                    on_click=DashboardState.reabrir_contorno,
                    variant="soft",
                ),
                rx.button(
                    "Cerrar contorno",
                    on_click=DashboardState.cerrar_contorno,
                    color_scheme="green",
                    variant="soft",
                    disabled=DashboardState.vertices_nueva_parcela.length() < 3,
                ),
            ),
            rx.button(
                "Deshacer último",
                on_click=DashboardState.deshacer_vertice,
                variant="soft",
                disabled=DashboardState.vertices_nueva_parcela.length() == 0,
            ),
            rx.button(
                "Borrar puntos",
                on_click=DashboardState.limpiar_contorno,
                variant="soft",
                disabled=DashboardState.vertices_nueva_parcela.length() == 0,
            ),
            width="100%",
            wrap="wrap",
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def formulario_parcela() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Añadir parcela", size="4", color=colors.TEXT),
            rx.text(
                "Indica su superficie y dibuja el contorno en la cuadrícula. "
                "Los cambios se guardan "
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
            formulario_dibujo(),
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
                disabled=DashboardState.contorno_cerrado != True,
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        width="100%",
    )


def tarjeta_media(media: dict[str, rx.Var]) -> rx.Component:
    return sensor_card(
        media["name"],
        rx.cond(media["value"] != "", media["value"], "—"),
        media["unit"],
        rx.cond(
            media["sector_count"] != "0",
            "Media de " + media["sector_count"] + " sectores con lectura",
            "Sin lecturas disponibles",
        ),
        media["icon"],
        media["color"],
        badge="Media",
    )


def sector_dibujado(sector: dict[str, rx.Var]) -> rx.Component:
    return rx.box(
        rx.text(
            sector["name"],
            position="absolute",
            top=sector["label_y"] + "%",
            left=sector["label_x"] + "%",
            transform="translate(-50%, -50%)",
            text_align="center",
            font_size="12px",
            font_weight="bold",
            color=colors.TEXT,
        ),
        position="absolute",
        top="0",
        right="0",
        bottom="0",
        left="0",
        background="#3D5A43",
        opacity="0.85",
        clip_path=sector["outline"],
        pointer_events="none",
    )


def formulario_dibujo_sectores() -> rx.Component:
    botones = [
        rx.button(
            punto_disponible(),
            on_click=DashboardState.agregar_vertice_sector(x, y),
            aria_label=f"Añadir vértice de sector en {x}%, {y}%",
            position="absolute",
            left=f"{x}%",
            top=f"{y}%",
            transform="translate(-50%, -50%)",
            width="28px",
            height="28px",
            padding="0",
            border="0",
            border_radius="50%",
            background="transparent",
            z_index="1",
            _hover={"background": "#3D5A43"},
        )
        for y in PUNTOS_CUADRICULA
        for x in PUNTOS_CUADRICULA
    ]

    return rx.vstack(
        rx.text(
            "Toca un punto vacío para elegirlo; los puntos dorados grandes ya están "
            "seleccionados. Puedes dejar zonas sin sector.",
            color=colors.TEXT,
            size="2",
        ),
        rx.box(
            rx.box(
                position="absolute",
                top="0",
                right="0",
                bottom="0",
                left="0",
                clip_path=DashboardState.contorno_parcela_css,
                background="#202020",
                pointer_events="none",
            ),
            *lineas_cuadricula(),
            *botones,
            rx.foreach(
                DashboardState.sectores_dibujados_temporales,
                sector_dibujado,
            ),
            rx.cond(
                DashboardState.vertices_sector_en_edicion.length() >= 3,
                rx.box(
                    position="absolute",
                    top="0",
                    right="0",
                    bottom="0",
                    left="0",
                    background="#E7B85C",
                    opacity="0.55",
                    clip_path=DashboardState.contorno_sector_previsualizacion,
                    pointer_events="none",
                ),
                rx.fragment(),
            ),
            rx.foreach(DashboardState.vertices_sector_en_edicion, punto_contorno),
            position="relative",
            width="100%",
            max_width="480px",
            aspect_ratio="1 / 1",
            overflow="hidden",
            border="1px solid #747474",
            border_radius="8px",
            background="#181818",
            role="group",
            aria_label="Cuadrícula para dibujar sectores dentro de la parcela",
        ),
        rx.text(
            "Vértices del sector actual: ",
            DashboardState.vertices_sector_en_edicion.length(),
            " · Sectores dibujados: ",
            DashboardState.sectores_dibujados_temporales.length(),
            color=colors.TEXT,
            size="2",
        ),
        rx.cond(
            DashboardState.error_dibujo_sector != "",
            rx.callout(
                DashboardState.error_dibujo_sector,
                icon="triangle_alert",
                color_scheme="red",
                width="100%",
            ),
            rx.fragment(),
        ),
        rx.cond(
            DashboardState.mensaje_dibujo_sector != "",
            rx.callout(
                DashboardState.mensaje_dibujo_sector,
                icon="circle_check",
                color_scheme="green",
                width="100%",
            ),
            rx.fragment(),
        ),
        rx.hstack(
            rx.cond(
                DashboardState.contorno_sector_cerrado,
                rx.button(
                    "Añadir sector",
                    on_click=DashboardState.crear_sector_dibujado,
                    color_scheme="green",
                ),
                rx.button(
                    "Cerrar sector",
                    on_click=DashboardState.cerrar_contorno_sector,
                    color_scheme="green",
                    variant="soft",
                    disabled=DashboardState.vertices_sector_en_edicion.length() < 3,
                ),
            ),
            rx.button(
                "Deshacer último",
                on_click=DashboardState.deshacer_vertice_sector,
                variant="soft",
                disabled=DashboardState.vertices_sector_en_edicion.length() == 0,
            ),
            rx.button(
                "Borrar puntos",
                on_click=DashboardState.limpiar_contorno_sector,
                variant="soft",
                disabled=DashboardState.vertices_sector_en_edicion.length() == 0,
            ),
            width="100%",
            wrap="wrap",
        ),
        rx.hstack(
            rx.button(
                "Terminar distribución",
                on_click=DashboardState.terminar_dibujo_sectores,
                color_scheme="green",
                disabled=DashboardState.sectores_dibujados_temporales.length() == 0,
            ),
            rx.button(
                "Cancelar",
                on_click=DashboardState.cancelar_dibujo_sectores,
                variant="soft",
            ),
            width="100%",
            wrap="wrap",
        ),
        spacing="3",
        align="start",
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
            align="center",
            width="100%",
            wrap="wrap",
        ),
        rx.card(
            rx.hstack(
                rx.icon(tag="map", size=28, color=colors.PARCEL_STATUS),
                rx.vstack(
                    rx.heading(
                        DashboardState.parcela_seleccionada["name"],
                        size="7",
                        color=colors.TEXT,
                    ),
                    rx.text(
                        DashboardState.parcela_seleccionada["area_m2"],
                        " m²",
                        color=colors.TEXT,
                        size="2",
                    ),
                    spacing="1",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
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
            rx.cond(
                DashboardState.modo_dibujo_sectores,
                formulario_dibujo_sectores(),
                rx.vstack(
                    rx.button(
                        "Dibujar sectores",
                        on_click=DashboardState.solicitar_redibujar_sectores,
                        color_scheme="green",
                        variant="soft",
                    ),
                    rx.cond(
                        DashboardState.confirmar_redibujo_sectores_pendiente,
                        rx.callout(
                            rx.vstack(
                                rx.text(
                                    "Al guardar, se sustituirán los sectores actuales "
                                    "y se perderán sus sensores y lecturas de ejemplo. "
                                    "Si cancelas el dibujo, se conservarán.",
                                    color=colors.TEXT,
                                    size="2",
                                ),
                                rx.hstack(
                                    rx.button(
                                        "Empezar a dibujar",
                                        on_click=DashboardState.confirmar_redibujar_sectores,
                                        color_scheme="red",
                                    ),
                                    rx.button(
                                        "Cancelar",
                                        on_click=DashboardState.cancelar_solicitud_redibujar_sectores,
                                        variant="soft",
                                    ),
                                    wrap="wrap",
                                ),
                                spacing="2",
                                align="start",
                            ),
                            icon="triangle_alert",
                            color_scheme="orange",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    parcela_map(),
                    rx.text(
                        "Los sectores se dibujan dentro del contorno de la parcela. "
                        "Se permiten huecos, pero no solapamientos.",
                        color=colors.TEXT,
                        size="2",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
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
                    formulario_parcela(),
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
            align="start",
        ),
        min_height="100vh",
        width="100%",
        style={"padding": "16px"},
        background=colors.DASHBOARD_BACKGROUND,
    )
