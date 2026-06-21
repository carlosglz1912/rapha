"""Tests for OpenDoctor bridge routes (/api/bridge/*)."""

import asyncio
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

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

    def test_documents_list_delegates_filters_as_owner(self):
        observed = {}

        async def fake_list(request, search, language, sort, offset, limit, archived):
            observed.update(
                user=request.state.current_user,
                search=search,
                language=language,
                sort=sort,
                offset=offset,
                limit=limit,
                archived=archived,
            )
            return {"documents": [], "total": 0, "languages": {}, "session_count": 0}

        doc_router = MagicMock()
        doc_router.routes = [
            SimpleNamespace(
                path="/api/documents/library",
                methods={"GET"},
                endpoint=fake_list,
            ),
        ]
        router = setup_bridge_routes(document_router=doc_router)
        handler = next(
            route.endpoint
            for route in router.routes
            if getattr(route, "path", "") == "/api/bridge/documents"
        )
        request = _request()
        result = asyncio.run(handler(request, "soap", "markdown", "alpha", 5, 10, False))

        assert result["total"] == 0
        assert observed == {
            "user": "alice",
            "search": "soap",
            "language": "markdown",
            "sort": "alpha",
            "offset": 5,
            "limit": 10,
            "archived": False,
        }
        assert request.state.current_user == "api"
        assert request.state.api_token is True

    def test_documents_list_rejects_missing_read_scope(self):
        doc_router = MagicMock()
        doc_router.routes = [
            SimpleNamespace(
                path="/api/documents/library",
                methods={"GET"},
                endpoint=MagicMock(),
            ),
        ]
        router = setup_bridge_routes(document_router=doc_router)
        handler = next(
            route.endpoint
            for route in router.routes
            if getattr(route, "path", "") == "/api/bridge/documents"
        )
        request = _request(api_token_scopes=["chat"])
        with pytest.raises(HTTPException) as exc:
            asyncio.run(handler(request, None, None, "recent", 0, 20, False))
        assert exc.value.status_code == 403

    def test_documents_list_keeps_two_owners_isolated(self):
        async def fake_list(request, search, language, sort, offset, limit, archived):
            owner = request.state.current_user
            return {
                "documents": [{"id": f"{owner}-doc", "owner": owner}],
                "total": 1,
                "languages": {},
                "session_count": 1,
            }

        doc_router = MagicMock()
        doc_router.routes = [
            SimpleNamespace(
                path="/api/documents/library",
                methods={"GET"},
                endpoint=fake_list,
            ),
        ]
        router = setup_bridge_routes(document_router=doc_router)
        handler = next(
            route.endpoint
            for route in router.routes
            if getattr(route, "path", "") == "/api/bridge/documents"
        )

        alice = _request(api_token_owner="alice")
        bob = _request(api_token_owner="bob")
        alice_result = asyncio.run(handler(alice, None, None, "recent", 0, 20, False))
        bob_result = asyncio.run(handler(bob, None, None, "recent", 0, 20, False))

        assert alice_result["documents"] == [{"id": "alice-doc", "owner": "alice"}]
        assert bob_result["documents"] == [{"id": "bob-doc", "owner": "bob"}]
        assert alice.state.current_user == "api"
        assert bob.state.current_user == "api"


class TestOpenDoctorTokenProfile:
    def test_opendoctor_profile_in_token_profiles(self):
        from routes.api_token_routes import TOKEN_PROFILES

        scopes = TOKEN_PROFILES["opendoctor"]
        assert "documents:write" in scopes
        assert "documents:read" in scopes
        assert "chat" in scopes
