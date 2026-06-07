"""OpenDoctor bridge — /api/bridge/*.

Thin HTTP surface for the OpenDoctor Electron desktop (Fase 3). Reuses Codex
scope checks and document routes; adds clinical discovery metadata.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel, Field

from routes.codex_routes import DOCS_READ_SCOPES, DOCS_WRITE_SCOPES, _as_owner, _scope_owner

_TEMPLATES_PATH = (
    Path(__file__).resolve().parent.parent / "static" / "clinical" / "templates.json"
)


def _load_templates() -> dict[str, Any]:
    if not _TEMPLATES_PATH.is_file():
        raise HTTPException(503, "Clinical templates are not available")
    try:
        return json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(503, f"Clinical templates could not be loaded: {exc}") from exc


def _find_template(template_id: str) -> dict[str, Any]:
    data = _load_templates()
    for section in ("documents", "notes"):
        for item in data.get(section) or []:
            if item.get("id") == template_id:
                return {**item, "_section": section}
    raise HTTPException(404, f"Unknown clinical template: {template_id}")


class BridgeDocumentFromTemplate(BaseModel):
    template_id: str = Field(..., min_length=1, max_length=80)
    session_id: str | None = None
    title: str | None = Field(None, max_length=200)


def setup_bridge_routes(document_router: APIRouter | None = None) -> APIRouter:
    from routes.codex_routes import _find_endpoint

    router = APIRouter(prefix="/api/bridge", tags=["bridge"])
    documents_create_endpoint = _find_endpoint(document_router, "POST", "/api/document")
    documents_library_endpoint = _find_endpoint(document_router, "GET", "/api/documents/library")

    @router.get("/ping")
    def ping():
        """Public liveness + clinical feature flags for OpenDoctor discovery."""
        from core.constants import APP_VERSION
        from src.privacy_filter import privacy_filter_enabled

        return {
            "ok": True,
            "product": "rapha",
            "version": APP_VERSION,
            "integration": "opendoctor",
            "clinical": {
                "templates": _TEMPLATES_PATH.is_file(),
                "privacy_filter": privacy_filter_enabled(),
            },
            "endpoints": {
                "templates": "/api/bridge/templates",
                "capabilities": "/api/bridge/capabilities",
                "companion_ping": "/api/companion/ping",
                "codex_capabilities": "/api/codex/capabilities",
            },
            "auth": {"token_prefix": "rph_"},
        }

    @router.get("/templates")
    def templates():
        """Public catalog of bundled clinical document/note templates."""
        return _load_templates()

    @router.get("/capabilities")
    def capabilities(request: Request):
        """Auth-required integration contract for OpenDoctor clients."""
        token_scopes = set(getattr(request.state, "api_token_scopes", []) or [])
        has_token = bool(getattr(request.state, "api_token", False))

        def scoped(allowed: set[str]) -> bool:
            return bool(token_scopes.intersection(allowed)) if has_token else True

        owner = None
        if has_token:
            owner = getattr(request.state, "api_token_owner", None)
        elif getattr(request.state, "current_user", None) not in (None, "api"):
            owner = request.state.current_user

        try:
            catalog = _load_templates()
        except HTTPException:
            catalog = {}

        return {
            "integration": "opendoctor",
            "owner": owner,
            "token_scopes": sorted(token_scopes),
            "clinical": {
                "templates": _TEMPLATES_PATH.is_file(),
                "template_ids": {
                    "documents": [t.get("id") for t in (catalog.get("documents") or [])],
                    "notes": [t.get("id") for t in (catalog.get("notes") or [])],
                },
            },
            "tools": {
                "documents": {
                    "read": scoped(DOCS_READ_SCOPES),
                    "write": scoped(DOCS_WRITE_SCOPES),
                    "actions": ["library", "from_template", "create"],
                    "available": documents_library_endpoint is not None,
                },
                "companion": {
                    "ping": "/api/companion/ping",
                    "models": "/api/companion/models",
                },
            },
        }

    @router.post("/documents/from-template")
    async def documents_from_template(
        request: Request,
        body: BridgeDocumentFromTemplate = Body(...),
    ):
        owner = _scope_owner(request, DOCS_WRITE_SCOPES)
        if documents_create_endpoint is None:
            raise HTTPException(503, "Documents integration is not available")

        tpl = _find_template(body.template_id)
        if tpl.get("_section") != "documents":
            raise HTTPException(400, "Template is not a document template")

        from routes.document_helpers import DocumentCreate

        payload = DocumentCreate(
            session_id=body.session_id,
            title=body.title or tpl.get("title") or tpl.get("label") or "Untitled",
            language=tpl.get("language"),
            content=tpl.get("content") or "",
        )
        return await _as_owner(request, owner, documents_create_endpoint, request, payload)

    return router