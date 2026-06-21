# Sincronización mensual con Odysseus

La sincronización de Rapha es una reconstrucción validada, no un merge periódico sobre `dev`.

## 1. Preparación

```bash
git fetch origin --tags
git fetch upstream dev
git tag -a rapha-pre-sync-YYYY-MM -m "Rapha before upstream sync YYYY-MM" origin/dev
git branch codex/backup-dev-YYYY-MM dev
git worktree add /Volumes/DEV/rapha-upstream-YYYY-MM \
  -b codex/upstream-refresh-YYYY-MM upstream/dev
```

Registrar el SHA upstream exacto. No incluir `.agents/`, datos, backups, `.env` ni secretos.

## 2. Aplicar el overlay

Usar upstream como implementación base. Portar únicamente:

- branding y contratos públicos Rapha;
- adaptador central `RAPHA_*` → `ODYSSEUS_*`;
- compatibilidad de cookies, tokens, headers, CLI y localStorage;
- templates, skills, selector clínico y privacy gate;
- bridge HTTP y profile `opendoctor`;
- documentación y pruebas del overlay.

Conservar la implementación upstream en rutas, agente, cookbook, email, frontend y tests salvo que el overlay requiera un cambio explícito. Resolver manualmente `setup.py` y el selector clínico si vuelven a divergir.

## 3. Validar

```bash
git diff --check
rg -n '^(<<<<<<<|=======|>>>>>>>)' . --glob '!data/**'
python -m pytest tests/ -q
docker compose config --quiet
```

Además:

- auditar branding visible, no identificadores internos;
- probar `RAPHA_*` con precedencia y fallback `ODYSSEUS_*`;
- probar cookies, ambos headers y tokens `rph_*`/`ody_*`;
- verificar privacy gate en sync, async y streaming, local y externo;
- verificar scopes, owners, paginación y errores del bridge;
- ejecutar el smoke HTTP real con dos owners;
- ejecutar tests, tipos y Ultracite en `@opendoctor/rapha-bridge` y Electron.

## 4. Reconciliar sin cambiar el árbol

```bash
before=$(git rev-parse HEAD^{tree})
git merge -s ours origin/dev -m "chore: reconcile Rapha history for YYYY-MM"
test "$before" = "$(git rev-parse HEAD^{tree})"
```

Este merge hace que el release contenga la historia anterior de Rapha sin reemplazar el árbol ya validado. Después, abrir el PR de release y promover únicamente mediante fast-forward:

```bash
git push -u origin codex/upstream-refresh-YYYY-MM
git push origin codex/upstream-refresh-YYYY-MM:dev
git tag -a rapha-vX.Y.Z-rapha.N -m "Rapha X.Y.Z-rapha.N"
git push origin rapha-vX.Y.Z-rapha.N
```

Nunca usar force-push. Si el árbol cambia durante la reconciliación o `dev` dejó de ser ancestro, detener la promoción y reconstruir desde el estado remoto actual.
