"""Public Rapha CLI remains a thin alias over upstream commands."""

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def test_dispatcher_reports_release_version():
    result = subprocess.run(
        [str(SCRIPTS / "rapha"), "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "rapha 1.0.0-rapha.1"


def test_every_public_wrapper_has_an_executable_legacy_target():
    wrappers = {
        path.name.removeprefix("rapha-")
        for path in SCRIPTS.glob("rapha-*")
        if path.name != "rapha-bootstrap-opendoctor"
    }
    legacy = {
        path.name.removeprefix("odysseus-")
        for path in SCRIPTS.glob("odysseus-*")
        if path.is_file() and os.access(path, os.X_OK) and "." not in path.name
    }
    assert wrappers == legacy
    assert all(os.access(SCRIPTS / f"rapha-{name}", os.X_OK) for name in wrappers)
