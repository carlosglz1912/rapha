"""OpenDoctor bridge under ``/api/bridge``.

The bridge is intentionally thin: document persistence and owner filtering
remain in the upstream document routes, while this module provides a stable,
scope-gated contract for the Electron client.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, Request
from pydantic import BaseModel, Field

from routes.codex_routes import DOCS_READ_SCOPES, DOCS_WRITE_SCOPES
from routes.integration_helpers import call_as_owner, find_endpoint, scope_owner

logger = logging.getLogger(__name__)

_TEMPLATES_PATH = (
    Path(__file__).resolve().parent.parent / "static" / "clinical" / "templates.json"
)


def _load_templates() -> dict[str, Any]:
    if not _TEMPLATES_PATH.is_file():
        raise HTTPException(503, "Clinical templates are not available")
    try:
        payload = json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("Clinical template catalog could not be loaded")
        raise HTTPException(503, "Clinical templates could not be loaded") from None
    if not isinstance(payload, dict):
        raise HTTPException(503, "Clinical template catalog is invalid")
    return payload


def _find_template(template_id: str) -> dict[str, Any]:
    catalog = _load_templates()
    for section in ("documents", "notes"):
        for item in catalog.get(section) or []:
            if isinstance(item, dict) and item.get("id") == template_id:
                return {**item, "_section": section}
    raise HTTPException(404, f"Unknown clinical template: {template_id}")


class BridgeDocumentFromTemplate(BaseModel):
    template_id: str = Field(..., min_length=1, max_length=80)
    session_id: str | None = Field(None, max_length=100)
    title: str | None = Field(None, max_length=200)


def setup_bridge_routes(document_router: APIRouter | None = None) -> APIRouter:
    router = APIRouter(prefix="/api/bridge", tags=["bridge"])
    create_document = find_endpoint(document_router, "POST", "/api/document")
    list_documents = find_endpoint(document_router, "GET", "/api/documents/library")

    @router.get("/ping")
    def ping():
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
                "documents": "/api/bridge/documents",
                "documents_from_template": "/api/bridge/documents/from-template",
            },
            "auth": {"token_prefix": "rph_", "legacy_token_prefix": "ody_"},
        }

    @router.get("/templates")
    def templates():
        return _load_templates()

    @router.get("/capabilities")
    def capabilities(request: Request):
        token_scopes = set(getattr(request.state, "api_token_scopes", []) or [])
        has_token = bool(getattr(request.state, "api_token", False))

        def scoped(allowed: set[str]) -> bool:
            return bool(token_scopes.intersection(allowed)) if has_token else True

        owner = (
            getattr(request.state, "api_token_owner", None)
            if has_token
            else getattr(request.state, "current_user", None)
        )
        try:
            catalog = _load_templates()
        except HTTPException:
            catalog = {}
        return {
            "integration": "opendoctor",
            "owner": owner if owner not in (None, "api") else None,
            "token_scopes": sorted(token_scopes),
            "clinical": {
                "templates": _TEMPLATES_PATH.is_file(),
                "template_ids": {
                    "documents": [item.get("id") for item in catalog.get("documents", [])],
                    "notes": [item.get("id") for item in catalog.get("notes", [])],
                },
            },
            "tools": {
                "documents": {
                    "read": scoped(DOCS_READ_SCOPES),
                    "write": scoped(DOCS_WRITE_SCOPES),
                    "actions": ["list", "from_template", "create"],
                    "available": list_documents is not None and create_document is not None,
                },
                "companion": {
                    "ping": "/api/companion/ping",
                    "models": "/api/companion/models",
                },
            },
        }

    @router.get("/documents")
    async def documents(
        request: Request,
        search: str | None = Query(None, max_length=200),
        language: str | None = Query(None, max_length=40),
        sort: str = Query("recent", pattern="^(recent|oldest|edits|alpha)$"),
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=50),
        archived: bool = Query(False),
    ):
        owner = scope_owner(request, DOCS_READ_SCOPES)
        if list_documents is None:
            raise HTTPException(503, "Documents integration is not available")
        return await call_as_owner(
            request,
            owner,
            list_documents,
            request,
            search,
            language,
            sort,
            offset,
            limit,
            archived,
        )

    @router.post("/documents/from-template")
    async def documents_from_template(
        request: Request,
        body: BridgeDocumentFromTemplate = Body(...),
    ):
        owner = scope_owner(request, DOCS_WRITE_SCOPES)
        if create_document is None:
            raise HTTPException(503, "Documents integration is not available")
        template = _find_template(body.template_id)
        if template.get("_section") != "documents":
            raise HTTPException(400, "Template is not a document template")

        from routes.document_helpers import DocumentCreate

        payload = DocumentCreate(
            session_id=body.session_id,
            title=body.title or template.get("title") or template.get("label") or "Untitled",
            language=template.get("language"),
            content=template.get("content") or "",
        )
        return await call_as_owner(
            request,
            owner,
            create_document,
            request,
            payload,
        )

    return router
