# Rapha — visión y límites

Rapha es una distribución de [Odysseus](https://github.com/pewdiepie-archdaemon/odysseus) orientada a profesionales de salud que necesitan un workspace de IA self-hosted, local-first y con control sobre sus datos. Rapha 1.0 se reconstruye sobre Odysseus 1.0 y se distribuye bajo AGPL-3.0-or-later.

## Responsabilidades

| Rapha sí es | Rapha no es |
|-------------|-------------|
| Workspace de productividad e IA local | Expediente clínico electrónico completo |
| Chat, documentos, notas, investigación, correo y calendario | Implementación de NOM-004/024 o firma FIEL |
| Plantillas y skills clínicas delgadas | Fuente canónica de datos clínicos estructurados |
| Privacy gate antes de proveedores LLM externos | Sustituto del criterio del profesional |
| Sidecar HTTP local para OpenDoctor | Librería embebida dentro de OpenDoctor |

OpenDoctor mantiene `MedicalBlock`, sus reglas clínicas y su aplicación Electron. Ambos proyectos conservan repositorio, proceso y licencia separados; se integran únicamente mediante el bridge HTTP local autenticado.

## Principios

1. Soberanía de datos: ejecución self-hosted y proveedores locales como primera opción.
2. IA como herramienta: el profesional revisa y firma; la IA propone y acelera.
3. Privacidad por destino: no alterar prompts hacia localhost/Ollama; redactar PHI antes de proveedores externos.
4. Especialización delgada: evitar forks profundos del core upstream.
5. Compatibilidad pública: UI, CLI, tokens y configuración exponen Rapha sin romper instalaciones legacy.

## Arquitectura

```text
OpenDoctor Electron
        |
        | HTTP local + token rph_ (ody_ legacy)
        v
Rapha /api/bridge/*
        |
        +-- documentos y sesiones de Odysseus, aislados por owner
        +-- plantillas y skills clínicas
        +-- agente/LLM con privacy gate por endpoint
```

La API estable del bridge incluye ping, capabilities, templates, listado de documentos y creación desde plantilla. Los helpers compartidos de autorización, delegación por owner y resolución de endpoints son públicos dentro de `routes/integration_helpers.py`; las integraciones no deben importar helpers privados de otras rutas.

## Estrategia upstream

Rapha sigue upstream mediante una revisión mensual manual. La rama de release siempre nace desde un commit upstream explícito y luego recibe el overlay Rapha. No se hace auto-merge directo a `dev`, no se force-pushea historia y no se porta el rebrand histórico masivo.

Cada promoción requiere:

1. worktree de staging desde `upstream/dev`;
2. inventario de cambios de seguridad, datos y contratos;
3. aplicación del overlay público y clínico;
4. suite completa, smoke HTTP y pruebas del cliente OpenDoctor;
5. merge de reconciliación que preserve el árbol validado;
6. fast-forward de `dev` y tag de release.

El procedimiento reproducible está en [`UPSTREAM_SYNC.md`](UPSTREAM_SYNC.md).

## Próximo alcance

- UI Electron para consultar la biblioteca Rapha mediante `listDocuments()`.
- Flujos hero: documentar consulta, investigar literatura y organizar jornada.
- Revisión legal antes de distribución comercial conjunta con OpenDoctor.

Quedan fuera de esta etapa una biblioteca UI nueva en Rapha, la duplicación de `MedicalBlock`, la implementación de NOM y cualquier sincronización automática de upstream.
