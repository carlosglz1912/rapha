"""Rapha environment helpers with legacy Odysseus fallbacks."""

from __future__ import annotations

import os


def get_env(name: str, *legacy_names: str, default: str = "") -> str:
    """Return the first non-empty value among ``name`` and legacy aliases."""
    for key in (name, *legacy_names):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return default