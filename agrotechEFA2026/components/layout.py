"""Marco común de la app: menú, cabecera y tema de colores.

Todas las páginas se envuelven con `pagina(contenido, titulo)`:

    def parcelas() -> rx.Component:
        return pagina(rx.text("Hola"), "Parcelas")

En ordenador el menú va en una barra lateral; en el móvil, en una barra
inferior. La entrada del menú cuyo nombre coincide con `titulo` sale resaltada.
"""

import reflex as rx

from . import colors

# --- Tema -----------------------------------------------------------------
# Colores del menú y la cabecera según el modo claro u oscuro. Los del modo
# oscuro salen de colors.py (el tema del panel) para que todo combine.
COLORES = {
    "fondo": rx.color_mode_cond(light="#F4F6F4", dark=colors.DASHBOARD_BACKGROUND),
    "superficie": rx.color_mode_cond(light="#FFFFFF", dark="#1F1F1F"),
    "linea": rx.color_mode_cond(light="1px solid #DDE3DD", dark="1px solid #3A3A3A"),
    "texto": rx.color_mode_cond(light="#1F2A1F", dark="#EDEDED"),
    "texto_suave": rx.color_mode_cond(light="#5B6B5B", dark=colors.TEXT),
    "acento": colors.PARCEL_STATUS,
    "acento_suave": rx.color_mode_cond(light="#DCFCE7", dark="#14532D"),
}

ANCHO_MENU = "220px"
ALTO_BARRA_INFERIOR = "64px"

# Por debajo de "sm" (768 px) se considera móvil.
SOLO_ORDENADOR = rx.breakpoints(initial="none", sm="flex")
SOLO_MOVIL = rx.breakpoints(initial="flex", sm="none")

# --- Menú -----------------------------------------------------------------
# (nombre, ruta, icono de Lucide). El nombre es también el título de la página.
MENU = [
    ("Panel", "/", "layout_dashboard"),
    ("Histórico", "/historico", "chart_line"),
    ("Parcelas", "/parcelas", "map"),
    ("Sensores", "/sensores", "radio_tower"),
    ("Alertas", "/alertas", "bell"),
]

# Datos de ejemplo hasta que exista el login (tarea C2).
USUARIO_EJEMPLO = "Ana López"
ROL_EJEMPLO = "agricultor"
ALERTAS_SIN_LEER_EJEMPLO = 3


def _logo(tamano: str = "40px") -> rx.Component:
    return rx.image(
        src="/logo.png",
        alt="Logo de Agrotech",
        width=tamano,
        height=tamano,
        object_fit="contain",
    )


def _enlace_lateral(nombre: str, ruta: str, icono: str, activa: bool) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icono, size=20),
            rx.text(nombre, size="3", weight="medium" if activa else "regular"),
            spacing="3",
            align="center",
            width="100%",
            padding="10px 12px",
            border_radius="8px",
            background=COLORES["acento_suave"] if activa else "transparent",
            color=COLORES["texto"] if activa else COLORES["texto_suave"],
            _hover={"background": COLORES["acento_suave"]},
        ),
        href=ruta,
        underline="none",
        width="100%",
        # Los lectores de pantalla anuncian cuál es la página actual.
        aria_current="page" if activa else None,
    )


def _barra_lateral(titulo: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            _logo(),
            rx.vstack(
                rx.heading("Agrotech", size="5", color=COLORES["texto"]),
                rx.text("Agricultura inteligente", size="1", color=COLORES["texto_suave"]),
                spacing="0",
            ),
            align="center",
            spacing="2",
            padding_bottom="16px",
        ),
        *[
            _enlace_lateral(nombre, ruta, icono, nombre == titulo)
            for nombre, ruta, icono in MENU
        ],
        display=SOLO_ORDENADOR,
        position="fixed",
        top="0",
        left="0",
        height="100vh",
        width=ANCHO_MENU,
        padding="20px 12px",
        spacing="1",
        background=COLORES["superficie"],
        border_right=COLORES["linea"],
    )


def _enlace_inferior(nombre: str, ruta: str, icono: str, activa: bool) -> rx.Component:
    color = COLORES["acento"] if activa else COLORES["texto_suave"]
    return rx.link(
        rx.vstack(
            rx.icon(icono, size=22),
            rx.text(nombre, size="1", weight="bold" if activa else "regular"),
            spacing="1",
            align="center",
            color=color,
        ),
        href=ruta,
        underline="none",
        flex="1",
        aria_current="page" if activa else None,
    )


def _barra_inferior(titulo: str) -> rx.Component:
    return rx.hstack(
        *[
            _enlace_inferior(nombre, ruta, icono, nombre == titulo)
            for nombre, ruta, icono in MENU
        ],
        display=SOLO_MOVIL,
        position="fixed",
        bottom="0",
        left="0",
        width="100%",
        height=ALTO_BARRA_INFERIOR,
        align="center",
        justify="between",
        padding_x="4px",
        background=COLORES["superficie"],
        border_top=COLORES["linea"],
        z_index="10",
    )


def _cabecera(titulo: str) -> rx.Component:
    return rx.hstack(
        # En el móvil no hay barra lateral, así que el logo va aquí.
        rx.box(_logo("32px"), display=SOLO_MOVIL),
        rx.heading(titulo, size="7", color=COLORES["texto"]),
        rx.spacer(),
        rx.link(
            rx.box(
                rx.icon("bell", size=22, color=COLORES["texto_suave"]),
                rx.badge(
                    ALERTAS_SIN_LEER_EJEMPLO,
                    color_scheme="red",
                    variant="solid",
                    radius="full",
                    position="absolute",
                    top="-8px",
                    right="-10px",
                ),
                position="relative",
            ),
            href="/alertas",
            aria_label=f"{ALERTAS_SIN_LEER_EJEMPLO} alertas sin leer",
        ),
        rx.hstack(
            rx.icon("circle_user", size=28, color=COLORES["texto_suave"]),
            rx.vstack(
                rx.text(USUARIO_EJEMPLO, size="2", weight="medium", color=COLORES["texto"]),
                rx.badge(ROL_EJEMPLO, color_scheme="green", size="1"),
                spacing="0",
                align="start",
            ),
            align="center",
            spacing="2",
            # En el móvil solo cabe el icono.
            display=SOLO_ORDENADOR,
        ),
        rx.color_mode.button(aria_label="Cambiar modo claro u oscuro"),
        width="100%",
        align="center",
        spacing="4",
        padding_bottom="12px",
        border_bottom=COLORES["linea"],
    )


def pagina(contenido: rx.Component, titulo: str) -> rx.Component:
    """Envuelve el contenido de una página con el menú y la cabecera.

    `titulo` debe ser uno de los nombres de MENU para que se resalte.
    """
    return rx.box(
        _barra_lateral(titulo),
        rx.vstack(
            _cabecera(titulo),
            contenido,
            spacing="5",
            width="100%",
            max_width="1200px",
            padding="20px",
            # Hueco para que la barra inferior no tape el final de la página.
            padding_bottom=rx.breakpoints(initial="88px", sm="20px"),
        ),
        _barra_inferior(titulo),
        padding_left=rx.breakpoints(initial="0", sm=ANCHO_MENU),
        min_height="100vh",
        width="100%",
        background=COLORES["fondo"],
    )


def en_construccion(texto: str) -> rx.Component:
    """Contenido provisional para las páginas que aún están vacías."""
    return rx.card(
        rx.vstack(
            rx.icon("construction", size=32, color=COLORES["acento"]),
            rx.text(texto, color=COLORES["texto_suave"]),
            align="center",
            spacing="3",
            padding="24px",
        ),
        width="100%",
    )
