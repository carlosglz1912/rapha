"""Low-level Rapha environment and token compatibility helpers.

This module deliberately lives at repository root so modules such as
``src.constants`` can apply aliases without importing the eager ``core``
package and creating a circular import. ``core.rapha_env`` remains the stable
application-facing import path and re-exports this API.
"""

from __future__ import annotations

import os
from collections.abc import MutableMapping

SUPPORTED_API_TOKEN_PREFIXES = ("rph_", "ody_")


def is_supported_api_token(token: str) -> bool:
    """Return whether a bearer token uses a current or legacy prefix."""
    return bool(token) and token.startswith(SUPPORTED_API_TOKEN_PREFIXES)


def get_env(name: str, *legacy_names: str, default: str = "") -> str:
    """Return the first non-empty value among a public name and aliases."""
    for key in (name, *legacy_names):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return default


def apply_rapha_env_aliases(
    environ: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    """Expose non-empty ``RAPHA_*`` values under upstream names."""
    target = environ if environ is not None else os.environ
    applied: dict[str, str] = {}
    for key, raw_value in list(target.items()):
        if not key.startswith("RAPHA_"):
            continue
        value = str(raw_value).strip()
        if not value:
            continue
        upstream_key = f"ODYSSEUS_{key.removeprefix('RAPHA_')}"
        target[upstream_key] = raw_value
        applied[upstream_key] = key
    return applied
