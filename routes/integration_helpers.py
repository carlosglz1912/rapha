"""Stable helpers shared by scoped external-integration routes."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from src.auth_helpers import require_user


async def call_as_owner(
    request: Request,
    owner: str,
    handler: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Call an existing route with the scope-gated owner identity."""
    original_user = getattr(request.state, "current_user", None)
    original_api_token = getattr(request.state, "api_token", None)
    request.state.current_user = owner
    request.state.api_token = False
    try:
        result = handler(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return result
    finally:
        request.state.current_user = original_user
        if original_api_token is None:
            try:
                delattr(request.state, "api_token")
            except AttributeError:
                pass
        else:
            request.state.api_token = original_api_token


def scope_owner(request: Request, allowed: set[str]) -> str:
    """Return the owner when a caller has at least one allowed scope."""
    if getattr(request.state, "api_token", False):
        scopes = set(getattr(request.state, "api_token_scopes", []) or [])
        if not scopes.intersection(allowed):
            required = " or ".join(sorted(allowed))
            raise HTTPException(403, f"API token missing required scope: {required}")
        owner = getattr(request.state, "api_token_owner", None)
        if not owner:
            raise HTTPException(403, "API token has no owner")
        return owner
    return require_user(request)


def scope_owner_all(request: Request, required: set[str]) -> str:
    """Return the owner when a caller has every required scope."""
    if getattr(request.state, "api_token", False):
        scopes = set(getattr(request.state, "api_token_scopes", []) or [])
        missing = required - scopes
        if missing:
            raise HTTPException(
                403,
                f"API token missing required scope: {' and '.join(sorted(missing))}",
            )
        owner = getattr(request.state, "api_token_owner", None)
        if not owner:
            raise HTTPException(403, "API token has no owner")
        return owner
    return require_user(request)


def find_endpoint(router: APIRouter | None, method: str, path: str):
    """Return a mounted route handler by exact method and path."""
    if router is None:
        return None
    for route in getattr(router, "routes", []):
        if getattr(route, "path", "") == path and method in getattr(route, "methods", set()):
            return route.endpoint
    return None
