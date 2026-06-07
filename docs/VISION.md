# Rapha — visión y roadmap

Documento estratégico. Para operación diaria (git, tests, compat, rutas), ver [`AGENTS.md`](../AGENTS.md).

## Qué es / qué no es

**Rapha** es un fork independiente de [Odysseus](https://github.com/pewdiepie-archdaemon/odysseus): workspace AI self-hosted orientado a **profesionales de salud** que quieren soberanía digital — local-first, privacidad, IA como asistente.

| Sí | No |
|----|-----|
| Productividad + IA local (chat, docs, email, research, modelos) | EHR corporativo |
| Consultorio digital privado | NOM-004/024, firma FIEL, directorio RNP |
| Especialización en capas delgadas (skills, plantillas, copy) | Merge continuo con upstream Odysseus |

**OpenDoctor** (`/Volumes/DEV/opendoctor`) = capa clínica vertical (MedicalBlock, Electron, Pi harness). Muy alpha. Sin integración técnica con Rapha aún.

## Identidad

**Rapha** (רָפָא — sanar, restaurar):

- Significado bíblico — coherente con medicina y soberanía sobre la vida digital
- Memoria del abuelo Rafael
- Producto donde el profesional firma; la IA propone y agiliza

**Tono visual (pendiente):** sobrio, cálido, consultorio privado. Ni náutico Odysseus ni corporate OpenDoctor. Sin iconografía religiosa explícita en UI.

## Valores (alineados con Odysseus / PewDiePie)

1. **Soberanía de datos** — tu hardware, tus datos, sin Big Tech obligatorio
2. **Anti-suscripción** — self-host, sin rastreo como modelo de negocio
3. **IA como herramienta** — tú escribes; la IA asiste (Documents, notas, triage)
4. **Minimalismo funcional** — un workspace integrado vs. diez apps fragmentadas

## Ecosistema

```
Rapha (Python/FastAPI)     →  modelos, agente, productivity, PWA
OpenDoctor (Bun/TS/Electron) →  MSD, bloques clínicos, NOM

Futuro plausible: sidecar HTTP local (:7000), no fusión de repos a corto plazo.
```

### Reutilización pragmática

| Capa | Reutilizar de Odysseus | Cambiar si conviene |
|------|------------------------|---------------------|
| Cookbook / model serving | Sí | — |
| Agente + MCP + skills | Sí | Pi (OpenDoctor) solo en dominio clínico |
| Email, calendar, docs, research | Sí | Plantillas y copy clínicos |
| UI PWA | Sí (corto plazo) | Electron vía OpenDoctor (largo plazo) |
| Datos clínicos estructurados | No en v1 | OpenDoctor `MedicalBlock` |
| Privacy pre-LLM | Portar concepto | Python primero |

## Roadmap

| Fase | Estado | Contenido |
|------|--------|-----------|
| 0 — Sync upstream | Hecho | Tag `rapha-v0-base` |
| 1 — Rebrand Rapha | Hecho | `dev` @ rebrand commit |
| 2 — Especialización clínica | **Siguiente** | Plantillas, skills, privacy gate, UX consultorio |
| 3 — Puente OpenDoctor | Opcional | Spike Electron → `:7000` |

### Fase 2 — detalle

1. Documents + Notes — SOAP, resumen consulta, consentimiento
2. Skills clínicos en `data/skills/` — formato profesional, sin PHI en logs
3. Research — literatura con citas (ya es fortaleza del core)
4. Privacy gate — inspirado en OpenDoctor `packages/privacy-filter`
5. Copy/UX — lenguaje de consultorio

### Fase 3 — detalle

- OpenDoctor Electron → `POST http://127.0.0.1:7000/api/...`
- Rapha Cookbook sirve modelos; Pi harness consume respuestas
- Contrato API + auth por token local (`rph_*`)

## Decisiones cerradas

| Tema | Decisión |
|------|----------|
| Upstream | Fork **totalmente independiente** — sin PRs a Odysseus |
| Experimentos | Otro fork dedicado, no mezclar en Rapha |
| Repo | `carlosglz1912/rapha` |
| PWA vs Electron | PWA para iterar; Electron vía OpenDoctor cuando esté listo |
| Filosofía | Reutilizar core; cambiar stack si mejora eficiencia o compatibilidad |

## Estrategia ante upstream acelerado

Odysseus es público y `dev` se mueve rápido. Rapha **no compite en seguir cada commit**.

| Capa | Política |
|------|----------|
| Core Python | Congelado; cherry-pick solo seguridad/bugs propios |
| Frontend | Especializar Rapha; no mergear rediseños upstream por defecto |
| Capa clínica Rapha | 100% propia — nunca upstream |
| Dependencias | Revisar ante CVE; no perseguir features nuevas |

Revisión opcional mensual — ver comandos en `AGENTS.md`.

## Tres flujos hero (por definir en producto)

1. **Documentar consulta** — plantilla → asistencia IA → el profesional edita y guarda
2. **Investigar literatura** — Deep Research con fuentes citadas, local
3. **Organizar jornada** — calendar + notes + email triage en un solo workspace