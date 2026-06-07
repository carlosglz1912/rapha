# AGENTS.md — contexto para agentes

Lee esto primero si retomas trabajo en **Rapha** sin historial de chat.

## Qué es Rapha

- Fork **independiente** de [Odysseus](https://github.com/pewdiepie-archdaemon/odysseus) (MIT).
- Repo: `https://github.com/carlosglz1912/rapha`
- Working copy habitual: `/Volumes/DEV/luke` (nombre de carpeta legacy; el producto es **Rapha**).
- Orientación: workspace AI **clínico-adjacente** — local-first, privacidad, IA como asistente (no reemplazo del profesional).
- **No** es un EHR; cumplimiento NOM / `MedicalBlock` vive en **OpenDoctor** (`/Volumes/DEV/opendoctor`) — otro monorepo alpha, sin integración técnica aún.

### Identidad del nombre

**Rapha** (רָפָא — sanar/restaurar). Elegido por significado bíblico, vínculo con medicina, y memoria del abuelo Rafael. Sustituye un intento abandonado de renombrar a "Luke".

## Estado actual (2026-06-07)

| Fase | Estado |
|------|--------|
| Fase 0 — sync upstream | Hecho. Tag `rapha-v0-base` = última línea común con upstream. |
| Fase 1 — rebrand Odysseus→Rapha | Hecho en `dev` (`44e3a0e`). 2604 tests pasan. |
| Fase 2 — especialización clínica | Pendiente (plantillas, skills, privacy gate, copy UX). |
| Fase 3 — puente OpenDoctor | Pendiente (spike HTTP Electron → `:7000`). |

### Git

```bash
origin   → carlosglz1912/rapha
upstream → pewdiepie-archdaemon/odysseus  # solo lectura / cherry-pick puntual
rama principal → dev
```

**Política upstream:** fork totalmente independiente. **No** hacer merge continuo de `upstream/dev`. Cherry-pick solo fixes de seguridad o bugs que afecten a Rapha. Nuevos experimentos → otro fork dedicado.

Revisión opcional:

```bash
git fetch upstream dev
git log --oneline rapha-v0-base..upstream/dev -- src/ routes/ core/ | head -20
```

## Compatibilidad tras el rebrand

| Antes (Odysseus) | Ahora (Rapha) |
|------------------|---------------|
| `ODYSSEUS_*` env | `RAPHA_*` (fallback `ODYSSEUS_*` en setup/Docker) |
| `odysseus_session` cookie | `rapha_session` — re-login tras rebrand |
| API tokens `ody_*` | Nuevos: `rph_*`; los `ody_*` existentes siguen válidos |
| `localStorage` `odysseus-*` | Migración automática a `rapha-*` en `static/js/storage.js` |
| CLI `odysseus-*` | `scripts/rapha*` |
| Docker service `odysseus` | `rapha` |

## Datos locales

- `data/` está en `.gitignore` — no se toca en merges.
- Backup de precaución: `data.backup-20260607/` (también gitignored).
- Config de modelos/endpoints: `data/settings.json`.

## Arranque rápido

```bash
cd /Volumes/DEV/luke
source venv/bin/activate
python -m uvicorn app:app --host 127.0.0.1 --port 7000
# o: docker compose up -d --build && docker compose logs rapha
```

## Próxima acción recomendada

**Fase 2** — capa delgada de especialización (sin reescribir el core Python):

1. Plantillas en Documents/Notes (SOAP, resumen consulta).
2. Skills clínicos empaquetados en `data/skills/`.
3. Privacy gate pre-LLM (concepto de OpenDoctor `privacy-filter`, port a Python).
4. Copy/UX de consultorio (no náutico Odysseus ni corporate OpenDoctor).

## Filosofía de ingeniería

- Reutilizar al máximo el core de Odysseus.
- Cambiar lenguaje/stack si mejora eficiencia o compatibilidad con OpenDoctor — no dudar.
- Mantener especialización en capas delgadas para facilitar cherry-picks puntuales de upstream.

## Relación con OpenDoctor (futuro)

Rapha = motor local (modelos, agente, productivity). OpenDoctor = capa clínica (Electron, Pi harness, NOM). Puente plausible: sidecar HTTP en `:7000`, no fusión de repos a corto plazo.