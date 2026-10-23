# Plan de equipo – Agrotech (6 personas + Claude)

Objetivo: **ganar** el II Reto Agrotech 2026. Entrega 8-dic · final 16-dic. Claude escribe código, ideas y automatiza; las personas revisan y confirman (pull request = vuestro "sí").

## Cómo ganamos (baremo 2025 como guía)
Funcionalidad 40 · código 15 · UI/UX 15 · docs 10 · git 10 · extras 10. Hacer **todo lo mínimo perfecto** y añadir 3 diferenciales que los demás no tendrán:
1. **Sensor real**: un ESP32 (o simulado idéntico) que envía al mismo endpoint. Demo "mira, es real".
2. **Recomendación inteligente de riego** (reglas + opcional IA) en el panel: "regar hoy 20 min en parcela 2".
3. **Alertas** (aviso visual + Telegram) y **exportar CSV/PDF** del histórico.
Extras baratos: modo claro/oscuro, PWA instalable en móvil, despliegue público, vídeo demo.

## Reparto: cada persona es dueña de CARPETAS distintas (así no se pisan)
Estructura del código (`agrotechEFA2026/`):

| Persona | Rol | Es dueña de (solo ella edita) |
|---|---|---|
| **A** | Backend y datos | `db/` (modelos, sesión, seed), `api/` (REST, login/roles, WebSocket), `migrations/` |
| **B** | Panel y gráficos | `pages/dashboard.py`, `pages/historico.py`, `components/charts.py`, `components/sensor_card.py`, `state/dashboard_state.py` |
| **C** | Gestión, alertas y UX | `pages/parcelas.py`, `pages/sensores.py`, `pages/alertas.py`, `pages/login.py`, `components/layout.py` (menú/tema/responsive), `state/gestion_state.py`, `services/alertas.py` (umbrales y aviso visual) |
| **D** | Sensores (diferencial 1) | `scripts/` (simulador + ESP32), `firmware/`, `docs/hardware.md` |
| **E** | Inteligencia y avisos (diferenciales 2 y 3) | `services/riego.py` (recomendación de riego), `services/telegram.py` (avisos), `services/export.py` (CSV/PDF) |
| **F** | Calidad, despliegue y entrega | `.github/` (CI, `CODEOWNERS`), `Dockerfile`/despliegue público, `README.md` (une las secciones), `docs/arquitectura.md`, `docs/presentacion/` (diapositivas y vídeo) |

**Compartido por los 6 (nadie es "el de comprobar"):** cada uno hace los **tests de su carpeta**, escribe **su sección del README** y del documento de arquitectura, y **aprueba los PR de otro** (rotando). CI, protección de `main` y presentación/vídeo: Claude lo prepara y presenta cada uno su parte en la final.

**Archivos compartidos** (`agrotechEFA2026.py`, `rxconfig.py`, `pyproject.toml`): solo se tocan con PR pequeño y avisando en el grupo; los gestiona A.

## Contrato semana 1 (lo primero, para trabajar en paralelo sin esperar)
Claude lo redacta en `docs/contrato.md` y todos lo aprueban antes de programar:
- Esquema BBDD: `users, parcels, sensors, sensor_data, alerts` (campos y tipos).
- JSON de la API (`sensor_id, timestamp ISO, type, value, unit`) y lista de endpoints.
- Qué datos expone cada `State` a la interfaz.
Con el contrato fijo, B y C trabajan con **datos de ejemplo** mientras A termina la BBDD.

## Reglas de git (puntúa en el baremo)
- `main` protegida: nadie sube directo. Ramas `feat/<persona>-<tema>`, PR con descripción, **otra persona lo aprueba**. Paso a paso en `docs/GIT-SEGURO.md`.
- `.github/CODEOWNERS`: si un PR toca tu carpeta, GitHub exige que lo apruebes tú o tu compañero de revisión.
- Commits pequeños, mensaje descriptivo en español ("Añade gráfico de humedad del suelo").
- Antes de empezar cada día: `git pull`. Cada uno trabaja solo en sus carpetas.
- Claude: cada persona lo usa en su propio clon; el repo llevará un `CLAUDE.md` con estas reglas y el reparto, para que respete las carpetas de cada una.

## Calendario (hoy 23 oct)
Tabla hecha para 4; con 6, la columna D se reparte: D lleva simulador y ESP32, E la recomendación de riego, Telegram y exportar, y F el despliegue, el CI y el vídeo.


| Semana | A Backend | B Panel | C Gestión/alertas | D Calidad/entrega |
|---|---|---|---|---|
| **1** (→30 oct) | Contrato + modelos + BBDD | Maqueta panel con datos ejemplo | Maqueta menú, login y tema | Simulador v1 (datos realistas por hora/día) |
| **2** (→6 nov) | `POST …/data` + lecturas | Tarjetas en tiempo real | CRUD parcelas | Simulador enviando a la API; comprar/elegir ESP32 y sensores |
| **3** (→13 nov) | Login con roles + dashboard API | Histórico con rango de fechas | CRUD sensores, umbrales | ESP32 midiendo y enviando datos reales |
| **4** (→20 nov) | WebSocket / refresco | Gráficos pulidos | Alertas visuales | Recomendación de riego + avisos por Telegram |
| **5** (→27 nov) | Rendimiento y datos reales | Responsive y PWA | Pulido de gestión | Exportar CSV/PDF, despliegue público |
| **6** (→4 dic) | Congelar API | Congelar UI | Congelar funciones | Congelar sensores; vídeo demo (Claude hace guion) |
| **→8 dic** | Revisión cruzada y entrega | | | **Entrega** |
| **9–16 dic** | Ensayo de la demo (todos), preguntas del jurado |

Regla: **congelar funciones el 4 dic**; después solo arreglar errores.

## Qué hace Claude y qué hacéis vosotros
- **Claude:** código de todas las carpetas, tests, CI, documentación, simulador, ideas, diapositivas, guion de la demo, revisión de PRs.
- **Vosotros:** probar, aprobar los PR, tomar decisiones (qué diferenciales entran), instalar el sensor físico y presentar ante el jurado.
- Cada persona arranca con: "Soy la persona X, lee `docs/PLAN-EQUIPO.md` y `docs/equipo/<tu carpeta>/GUION.md`".

## Antes de empezar (necesito vuestro OK)
1. Quién es A, B, C, D, E y F (según gustos: A más backend, B más diseño, C más lógica, D hardware, E lógica/IA, F más orden/documentación).
2. Activar la protección de `main` en GitHub y dar acceso a los 6 (pasos en `docs/GIT-SEGURO.md`).
3. Elegir qué diferenciales entran (propongo los 3).
4. Si hay ESP32 o sensores en clase, o si lo dejamos solo simulado.
