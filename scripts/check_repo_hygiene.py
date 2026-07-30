#!/usr/bin/env python3
"""Block repository pollution before it reaches git history.

Enforces docs/REPO-HYGIENE.md. Runs on staged files in pre-commit and on the
whole tracked tree in `npm run verify`.

Deleting a file from a later commit does NOT remove it from history -- once a
200 MB checkpoint is pushed, every future clone downloads it forever. This gate
is the only cheap moment to stop that.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MAX_FILE_BYTES = 1_000_000  # 1 MB — hard block
WARN_FILE_BYTES = 200_000  # 200 KB — warn
MAX_TRACKED_FILES = 400  # tree-size ceiling; was 2,539 before the reset
MAX_NPM_SCRIPTS = 40

BINARY_SUFFIXES = {
    ".pt",
    ".pth",
    ".bin",
    ".safetensors",
    ".gguf",
    ".onnx",
    ".ckpt",
    ".pkl",
    ".pickle",
    ".npy",
    ".npz",
    ".h5",
    ".msgpack",
    ".arrow",
    ".parquet",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".mp4",
    ".pdf",
}

SECRET_NAMES = {".env", "credentials.json", "secrets.yaml", "id_rsa"}
SECRET_SUFFIXES = {".pem", ".key"}

FORBIDDEN_DIRS = ("data/", "runs/", "artifacts/", "node_modules/", ".local/")


def run(*args: str) -> list[str]:
    out = subprocess.run(args, capture_output=True, text=True, check=False)
    return [line for line in out.stdout.splitlines() if line.strip()]


def staged_files() -> list[str]:
    return run("git", "diff", "--cached", "--name-only", "--diff-filter=ACM")


def tracked_files() -> list[str]:
    return run("git", "ls-files")


def check_binaries(files: list[str], errors: list[str]) -> None:
    for f in files:
        if Path(f).suffix.lower() in BINARY_SUFFIXES:
            errors.append(
                f"BINARY: {f} — model weights and archives never go in git. "
                f"Publish via HuggingFace Hub; commit the SHA-256 instead."
            )


def check_secrets(files: list[str], errors: list[str]) -> None:
    for f in files:
        name = Path(f).name
        if name in SECRET_NAMES or Path(f).suffix in SECRET_SUFFIXES:
            errors.append(f"SECRET: {f} — never commit credentials.")


def check_forbidden_dirs(files: list[str], errors: list[str]) -> None:
    for f in files:
        if f.startswith(FORBIDDEN_DIRS) and not f.endswith(".gitkeep"):
            errors.append(f"REGENERABLE: {f} — this directory is gitignored output.")


def check_sizes(files: list[str], errors: list[str], warnings: list[str]) -> None:
    for f in files:
        path = Path(f)
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            errors.append(
                f"TOO LARGE: {f} is {size / 1e6:.1f} MB (cap {MAX_FILE_BYTES / 1e6:.0f} MB)."
            )
        elif size > WARN_FILE_BYTES:
            warnings.append(f"large: {f} is {size / 1e3:.0f} KB")


def check_tree_size(errors: list[str], warnings: list[str]) -> None:
    tracked = tracked_files()
    if len(tracked) > MAX_TRACKED_FILES:
        errors.append(
            f"TREE BLOAT: {len(tracked)} tracked files (cap {MAX_TRACKED_FILES}). "
            f"The previous programme reached 2,539 and became unnavigable."
        )
    elif len(tracked) > MAX_TRACKED_FILES * 0.8:
        warnings.append(f"tracked files: {len(tracked)} of {MAX_TRACKED_FILES}")


def check_npm_scripts(errors: list[str]) -> None:
    import json

    pkg = Path("package.json")
    if not pkg.exists():
        return
    count = len(json.loads(pkg.read_text()).get("scripts", {}))
    if count > MAX_NPM_SCRIPTS:
        errors.append(
            f"SCRIPT BLOAT: {count} npm scripts (cap {MAX_NPM_SCRIPTS}). "
            f"Every script must be referenced by a stage in docs/pipeline/."
        )


def main() -> int:
    scope = sys.argv[1] if len(sys.argv) > 1 else "--all"
    files = staged_files() if scope == "--staged" else tracked_files()

    errors: list[str] = []
    warnings: list[str] = []

    check_binaries(files, errors)
    check_secrets(files, errors)
    check_forbidden_dirs(files, errors)
    check_sizes(files, errors, warnings)
    check_tree_size(errors, warnings)
    check_npm_scripts(errors)

    for w in warnings:
        print(f"[hygiene] warn: {w}")

    if errors:
        print("[hygiene] FAILED — refusing to pollute the repository:\n")
        for e in errors:
            print(f"  - {e}")
        print("\nSee docs/REPO-HYGIENE.md. Do not bypass with --no-verify.")
        return 1

    print(f"[hygiene] OK — {len(files)} file(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
