"""Tests for OpenDoctor bridge routes (/api/bridge/*)."""

import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.bridge_routes import (
    BridgeDocumentFromTemplate,
    _find_template,
    _load_templates,
    setup_bridge_routes,
)


def _request(**state):
    defaults = {
        "current_user": "api",
        "api_token": True,
        "api_token_owner": "alice",
        "api_token_scopes": ["documents:read", "documents:write"],
    }
    defaults.update(state)
    return SimpleNamespace(state=SimpleNamespace(**defaults))


class TestBridgeTemplates:
    def test_load_templates_has_documents(self):
        data = _load_templates()
        assert "documents" in data
        assert any(t.get("id") == "soap" for t in data["documents"])

    def test_find_template_soap(self):
        tpl = _find_template("soap")
        assert tpl["label"] == "Nota SOAP"
        assert tpl["_section"] == "documents"

    def test_find_template_unknown_raises(self):
        with pytest.raises(HTTPException) as exc:
            _find_template("no-existe")
        assert exc.value.status_code == 404


class TestBridgeHandlers:
    def test_ping_returns_product_metadata(self):
        router = setup_bridge_routes()
        ping = next(
            r.endpoint for r in router.routes if getattr(r, "path", "") == "/api/bridge/ping"
        )
        out = ping()
        assert out["ok"] is True
        assert out["product"] == "rapha"
        assert out["integration"] == "opendoctor"
        assert out["auth"]["token_prefix"] == "rph_"

    def test_capabilities_scopes_documents(self):
        router = setup_bridge_routes(document_router=MagicMock(routes=[]))
        capabilities = next(
            r.endpoint for r in router.routes if getattr(r, "path", "") == "/api/bridge/capabilities"
        )
        out = capabilities(_request())
        assert out["integration"] == "opendoctor"
        assert out["owner"] == "alice"
        assert out["tools"]["documents"]["read"] is True
        assert out["tools"]["documents"]["write"] is True
        assert "soap" in out["clinical"]["template_ids"]["documents"]

    def test_documents_from_template_delegates_create(self):
        import asyncio

        async def fake_create(request, req):
            return {"id": "doc-1", "title": req.title, "content": req.content}

        doc_router = MagicMock()
        doc_router.routes = [
            SimpleNamespace(path="/api/document", methods={"POST"}, endpoint=fake_create),
        ]
        router = setup_bridge_routes(document_router=doc_router)
        handler = next(
            r.endpoint
            for r in router.routes
            if getattr(r, "path", "") == "/api/bridge/documents/from-template"
        )
        req = _request()
        body = BridgeDocumentFromTemplate(template_id="soap", session_id="sess-1")
        out = asyncio.run(handler(req, body))
        assert out["id"] == "doc-1"
        assert "SOAP" in out["title"]


class TestOpenDoctorTokenProfile:
    def test_opendoctor_profile_in_token_profiles(self):
        from routes.api_token_routes import TOKEN_PROFILES

        scopes = TOKEN_PROFILES["opendoctor"]
        assert "documents:write" in scopes
        assert "documents:read" in scopes
        assert "chat" in scopes