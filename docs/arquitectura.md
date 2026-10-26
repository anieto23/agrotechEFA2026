# Arquitectura

## Aplicación y panel

- `agrotechEFA2026/agrotechEFA2026.py` crea la aplicación Reflex y registra la página principal.
- `agrotechEFA2026/pages/dashboard.py` compone la cabecera, los indicadores y el estado de la parcela.
- `agrotechEFA2026/components/sensor_card.py` contiene la tarjeta reutilizable de lectura.
- `agrotechEFA2026/components/colors.py` centraliza los colores usados por el panel.

El panel sigue siendo una maqueta: las lecturas son fijas y no hay conexión con la API,
estado dinámico ni gráficos de histórico implementados todavía.
