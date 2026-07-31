"""P01 ground-truth contracts — fail if the reset is undone.

These assert repository invariants, not document contents.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _train_modules() -> list[Path]:
    train_dir = ROOT / "n32" / "train"
    return sorted(
        p
        for p in train_dir.glob("*.py")
        if p.name != "__init__.py" and not p.name.startswith("test_")
    )


def test_npm_script_count_at_most_40() -> None:
    scripts = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
    assert len(scripts) <= 40, f"npm scripts={len(scripts)} exceeds cap 40"


def test_exactly_one_training_entrypoint_module() -> None:
    modules = _train_modules()
    names = [p.name for p in modules]
    assert names == ["loop.py"], f"expected only loop.py, got {names}"


def test_train_script_invokes_loop_module() -> None:
    scripts = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
    assert scripts["train"] == "python3 -m n32.train.loop"


def test_legacy_wave_tag_exists() -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/tags/legacy/waves-w-bh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, "git tag legacy/waves-w-bh must exist"


def test_no_legacy_code_in_working_tree() -> None:
    forbidden = [
        ROOT / "nano_lm",
        ROOT / "docs" / "results" / "nano-lm",
        ROOT / "agent-rules",
        ROOT / "agent-harness",
        ROOT / "legacy",
    ]
    present = [str(p.relative_to(ROOT)) for p in forbidden if p.exists()]
    assert present == [], f"legacy paths present: {present}"


def test_active_python_file_count_at_most_80() -> None:
    files = list((ROOT / "n32").rglob("*.py")) + list((ROOT / "bench").rglob("*.py"))
    files = [p for p in files if "__pycache__" not in p.parts]
    assert len(files) <= 80, f"active Python files={len(files)} exceeds cap 80"


def test_loop_module_is_importable() -> None:
    import n32.train.loop as loop

    assert callable(loop.main)
    assert loop.main([]) == 2
