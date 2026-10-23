# II Reto Agrotech Startup 2026 – bases (recogidas de agrotechstartup.com el 23-oct-2026)

Organiza Asociación Granada + · financia Junta de Andalucía (Consejería de Universidad, Investigación e Innovación) · patrocina Puerto de Motril. Participa alumnado de FP (familias tecnológicas y agrarias), en equipo, con apoyo de centro y profesorado.

## Fechas
- Entrega prevista: **8-dic-2026** (plataforma colaborativa; instrucciones por email a tutores y equipos).
- Gran Final prevista: **16-dic-2026**, 9:00–14:00, Costa Tropical de Granada (programa provisional: 10:00 bienvenida, 10:30 presentaciones ante el jurado, 12:00 deliberación + ponencia IA, 13:00 premios, 14:00 clausura).
- Plazo de inscripción: no publicado. Formularios en /inscripcion.html (equipos y público).

## Fases
Presentación → Equipos → Bases técnicas → Desarrollo (documentar evolución) → Entrega → Presentación final → Ganadores (3 primeros).
Premios orientativos: 1.º 1000 € · 2.º 750 € · 3.º 500 €.

## El desafío
Web app **responsiva** para que un agricultor o técnico monitorice **en tiempo real** sensores de una parcela (temperatura, humedad del suelo, luminosidad, humedad ambiental…).

## Tecnologías obligadas
Python + **Reflex**, una base de datos (SQLite, MySQL, PostgreSQL o MariaDB), git + GitHub, software libre, licencia **GPL v3 o posterior**.

## Requisitos mínimos 2026
- Interfaz responsiva (ordenador, tableta, móvil).
- Almacenar los datos.
- Demo en directo con datos reales o simulados.
- Código ordenado y comentado donde la lógica no sea evidente.
- GitHub desde el día 1; se valora historial: commits frecuentes y descriptivos, ramas por funcionalidad, pull requests.
- README (propósito, instalación, ejecución local) + documento breve de arquitectura y decisiones + registro de evolución del trabajo.

## Criterios (sin pesos publicados)
Funcionalidad y utilidad agro · calidad técnica del código · diseño y facilidad de uso · documentación y uso de git · innovación · presentación ante el jurado.

## Ayuda técnica sugerida (no obligatoria)
API REST (Reflex o FastAPI): `POST /api/auth/login`, `GET /api/parcels`, `GET /api/parcels/{id}/sensors`, `POST /api/sensors/{sensor_id}/data`, `GET /api/sensors/{sensor_id}/data?from=&to=&limit=`, `GET /api/dashboard`, `WS /ws/parcels/{id}` (opcional).
Dato ejemplo: `sensor_id, timestamp ISO, type, value, unit`.
Tablas: `users, parcels, sensors, sensor_data, alerts`.

## Edición 2025 (referencia; probable que se repita, NO confirmado)
- Mínimos: 2 roles (agricultor, técnico/visor), panel tiempo real por parcela, CRUD parcelas y sensores, gráficos históricos por rango de fechas, umbrales con aviso visual, SQLite, API REST documentada, tests (pytest), CONTRIBUTING.md, LICENSE.
- Entregables: código, BBDD ejemplo o script generador, README con endpoints/payloads/capturas, doc de arquitectura (máx. 2 págs).
- Baremo: funcionalidad 40 · código 15 · UI/UX 15 · documentación/repo 10 · git 10 · extras (despliegue, vídeo demo) 10.
- Simulador obligatorio si no hay sensores: `scripts/gen_sample_data.py` (p. ej. 5–40 ºC según hora/día).
- Presentación: 3–5 diapositivas (idea, arquitectura, enlace demo) + demo en vivo.
