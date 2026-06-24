"""Clinical skill seeds are idempotent and never overwrite user edits."""

from pathlib import Path

import setup


def test_seed_clinical_skills_is_idempotent(monkeypatch, tmp_path):
    destination = tmp_path / "skills" / "clinical"
    monkeypatch.setattr(setup, "CLINICAL_SKILLS_DEST", str(destination))

    first_seeded, first_skipped = setup.seed_clinical_skills()
    assert first_seeded == 3
    assert first_skipped == 0

    soap = destination / "nota-soap" / "SKILL.md"
    soap.write_text("customized by user", encoding="utf-8")
    second_seeded, second_skipped = setup.seed_clinical_skills()

    assert second_seeded == 0
    assert second_skipped == 3
    assert soap.read_text(encoding="utf-8") == "customized by user"
    assert sorted(path.parent.name for path in Path(destination).glob("*/SKILL.md")) == [
        "literatura",
        "nota-soap",
        "privacidad",
    ]
