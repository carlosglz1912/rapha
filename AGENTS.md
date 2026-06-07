# AGENTS.md

Instrucciones **operativas** para agentes. Visión, roadmap y decisiones estratégicas → [`docs/VISION.md`](docs/VISION.md).

## Lectura rápida

| Pregunta | Dónde |
|----------|-------|
| ¿Por qué existe Rapha? | `docs/VISION.md` |
| ¿Qué commit/tag es baseline? | abajo |
| ¿Cómo corro tests / servidor? | abajo |
| ¿Qué renombró del rebrand? | tabla compat abajo |

## Repo y rutas

```
origin:     https://github.com/carlosglz1912/rapha.git
upstream:   https://github.com/pewdiepie-archdaemon/odysseus.git  # solo lectura
rama:       dev
worktree:   /Volumes/DEV/luke          # carpeta legacy; producto = Rapha
ecosistema: /Volumes/DEV/opendoctor    # sin código compartido aún
```

**Tags:** `rapha-v0-base` = último sync upstream antes del rebrand.

**Política git:** no mergear `upstream/dev` de forma rutinaria. Cherry-pick puntual solo si hay CVE o bug que nos afecte.

```bash
git fetch upstream dev
git log --oneline rapha-v0-base..upstream/dev -- src/ routes/ core/ | head -20
```

## Estado de la sesión (actualizar al cerrar trabajo)

| Item | Valor |
|------|-------|
| Última acción | Fase 3 spike — `/api/bridge/*`, token profile `opendoctor`, cliente `@opendoctor/rapha-bridge` |
| Siguiente tarea | UI OpenDoctor que consuma `window.electronAPI.rapha.*`; flujos hero en producto |
| Tests | `venv/bin/python -m pytest tests/ -q` → 2640 passed (2026-06-07) |
| Bloqueos | ninguno |

## Comandos

```bash
cd /Volumes/DEV/luke
source venv/bin/activate

# servidor
python -m uvicorn app:app --host 127.0.0.1 --port 7000

# tests (subset rápido)
python -m pytest tests/test_app.py tests/test_rapha_dispatcher.py -q

# tests (suite completa ~70s)
python -m pytest tests/ -q

# docker
docker compose up -d --build
docker compose logs rapha --tail=50
```

## Mapa del código (puntos de entrada)

| Área | Ruta |
|------|------|
| App FastAPI | `app.py` |
| Auth / DB | `core/`, `routes/auth_routes.py` |
| Agente / LLM | `src/agent_loop.py`, `src/llm_core.py` |
| Cookbook | `routes/cookbook_routes.py`, `services/hwfit/` |
| Frontend PWA | `static/index.html`, `static/js/` |
| CLI | `scripts/rapha`, `scripts/rapha-*` |
| Integraciones agentes | `integrations/codex/`, `integrations/claude/` |
| Env compat | `core/rapha_env.py` |
| Datos usuario | `data/` (gitignored) |

## Compat Odysseus → Rapha

| Antes | Ahora |
|-------|-------|
| `ODYSSEUS_*` | `RAPHA_*` (+ fallback en setup/Docker) |
| cookie `odysseus_session` | `rapha_session` |
| tokens `ody_*` | nuevos `rph_*`; `ody_*` legacy aún válidos (`app.py`) |
| `localStorage` `odysseus-*` | migración auto en `static/js/storage.js` |
| CLI `odysseus-*` | `scripts/rapha-*` |
| compose service `odysseus` | `rapha` |

## Datos locales

- `data/settings.json` — endpoints y modelos preconfigurados
- `data.backup-*/` — backups manuales (gitignored)
- Merges git **no** tocan `data/`

## Convenciones para agentes

**Hacer**

- Leer `docs/VISION.md` antes de features nuevas
- Mantener especialización clínica en capas delgadas (skills, plantillas, copy) — no refactor masivo del core
- Correr tests tras cambios en `src/`, `routes/`, `static/js/`
- Actualizar la tabla "Estado de la sesión" arriba al terminar

**No hacer**

- Merge completo desde `upstream/dev` sin acuerdo explícito
- Duplicar NOM / `MedicalBlock` de OpenDoctor en Rapha
- Commitear `data/`, `data.backup-*`, `.env`, secrets
- Reintroducir branding Odysseus en UI (upstream se cita solo en ACKNOWLEDGMENTS)

## Plantilla — al cerrar sesión

Reemplazar la tabla "Estado de la sesión":

```markdown
| Última acción | <qué hiciste + evidencia> |
| Siguiente tarea | <un paso concreto> |
| Tests | <comando + resultado> |
| Bloqueos | <si hay> |
```