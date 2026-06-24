# AGENTS.md

Instrucciones operativas para agentes. Visión y límites de producto: [`docs/VISION.md`](docs/VISION.md). Proceso de actualización: [`docs/UPSTREAM_SYNC.md`](docs/UPSTREAM_SYNC.md).

## Repositorio

```text
origin:     https://github.com/carlosglz1912/rapha.git
upstream:   https://github.com/pewdiepie-archdaemon/odysseus.git  # solo lectura
rama:       dev
worktree:   /Volumes/DEV/luke          # nombre histórico; producto = Rapha
ecosistema: /Volumes/DEV/opendoctor    # proceso y repositorio separados vía HTTP
```

Baseline de esta versión: `upstream/dev@1602674`. La versión de distribución es `1.0.0-rapha.1` y el tag de release es `rapha-v1.0.0-rapha.1`. `rapha-v0-mit-final` conserva el último árbol de Rapha bajo MIT antes de adoptar AGPL-3.0-or-later.

No hacer merges rutinarios directamente sobre `dev`. Cada actualización mensual se construye desde upstream en una rama/worktree de staging, se valida completa y se promueve sin force-push.

## Estado de la sesión

| Item | Valor |
|------|-------|
| Última acción | Rapha 1.0 reconstruido sobre `upstream/dev@1602674`; overlay clínico, compatibilidad pública, bridge y smoke con dos owners |
| Siguiente tarea | Implementar la UI Electron que consuma `window.electronAPI.rapha.listDocuments()` |
| Tests | `venv/bin/python -m pytest tests/ -q` → 3887 passed, 2 skipped (2026-06-20) |
| Bloqueos | ninguno |

## Comandos

```bash
cd /Volumes/DEV/luke
source venv/bin/activate

python -m uvicorn app:app --host 127.0.0.1 --port 7000
python -m pytest tests/test_bridge_routes.py tests/test_privacy_filter.py tests/test_rapha_compat.py -q
python -m pytest tests/ -q

docker compose up -d --build
docker compose logs rapha --tail=50
```

## Puntos de entrada

| Área | Ruta |
|------|------|
| FastAPI | `app.py` |
| Auth / DB | `core/`, `routes/auth_routes.py` |
| Agente / LLM | `src/agent_loop.py`, `src/llm_core.py` |
| Privacy gate | `src/privacy_filter.py` |
| Bridge HTTP | `routes/bridge_routes.py`, `routes/integration_helpers.py` |
| Frontend PWA | `static/index.html`, `static/js/` |
| Plantillas clínicas | `static/clinical/templates.json`, `seeds/skills/clinical/` |
| CLI público | `scripts/rapha`, `scripts/rapha-*` |
| Compatibilidad env | `core/rapha_env.py` |
| Datos locales | `data/` (gitignored) |

## Compatibilidad pública

| Contrato anterior | Contrato Rapha |
|-------------------|----------------|
| `ODYSSEUS_*` | `RAPHA_*` tiene precedencia; `ODYSSEUS_*` permanece como fallback |
| cookie `odysseus_session` | se emite `rapha_session`; se acepta la cookie legacy |
| tokens `ody_*` | se emiten `rph_*`; ambos prefijos se aceptan |
| header `X-Odysseus-Internal-Token` | se prefiere `X-Rapha-Internal-Token`; ambos se aceptan |
| claves `rapha-*` de localStorage | se copian una vez a las claves internas upstream, sin borrar respaldo |
| comandos `odysseus-*` | siguen disponibles; `rapha-*` es la interfaz pública |

## Convenciones

- Leer `docs/VISION.md` antes de añadir features.
- Mantener lo clínico en capas delgadas: skills, plantillas, privacy gate y bridge.
- No duplicar NOM, `MedicalBlock` ni datos clínicos estructurados de OpenDoctor.
- El privacy gate solo redacta tráfico hacia endpoints externos; localhost/Ollama conserva el contenido.
- Los logs de privacidad incluyen únicamente cantidad y tipo de redacción, nunca PHI.
- Ejecutar las pruebas relevantes después de cambios en `src/`, `routes/` o `static/js/`.
- No commitear `data/`, `data.backup-*`, `.env`, secretos ni `.agents/`.
- Actualizar la tabla “Estado de la sesión” al cerrar trabajo.
