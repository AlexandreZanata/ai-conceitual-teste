"""Lab freeze NO-REOPEN (§8 #6): KILL archives stay archived; no revive scripts."""

from __future__ import annotations

import json
import re
from typing import Mapping, Sequence

__all__ = [
    "LAB_FREEZE_ID",
    "KILL_ARCHIVES",
    "BANNED_NPM_PREFIXES",
    "WAVE_COMPLETE_DOCS",
    "decide_lab_freeze",
    "banned_scripts",
    "missing_archives",
    "wave_status_ok",
]

LAB_FREEZE_ID = "LAB-FREEZE"

# pesquisa §8 #6 + Wave Y KILLs that must remain archived.
KILL_ARCHIVES: dict[str, str] = {
    "STREAM": "docs/results/nano-lm/archive/hstream-stream.md",
    "KVCACHE-Q": "docs/results/nano-lm/archive/hkvcache-kvcache.md",
    "GENCACHE": "docs/results/nano-lm/archive/hgencache-gencache.md",
    "MIXD": "docs/results/nano-lm/archive/hmixd-mix.md",
    "GPFB_K2": "docs/results/nano-lm/archive/hgpfb-gpfb.md",
    "naive_CTX": "docs/results/nano-lm/archive/hctx-long-window.md",
}

# npm script name prefixes that would reopen KILLs (gpfb4 is allowed).
BANNED_NPM_PREFIXES: tuple[str, ...] = (
    "nano:stream",
    "nano:gencache",
    "nano:kvcache",
    "nano:mixd",
    "nano:rag",
    "nano:ctx",
    "nano:gpfb",
)

WAVE_COMPLETE_DOCS: tuple[str, ...] = (
    "docs/results/nano-lm/wave-y-summary.md",
    "docs/results/nano-lm/wave-z-summary.md",
    "docs/results/nano-lm/wave-z-hitl.md",
)


def missing_archives(exists: Mapping[str, bool]) -> list[str]:
    """
    GIVEN path→exists for KILL archives
    WHEN checking freeze
    THEN return missing archive labels.
    """
    miss: list[str] = []
    for label, path in KILL_ARCHIVES.items():
        if not bool(exists.get(path)):
            miss.append(label)
    return miss


def banned_scripts(script_names: Sequence[str]) -> list[str]:
    """
    GIVEN package.json script keys
    WHEN scanning for reopened KILL runners
    THEN return offending script names (gpfb4 allowed).
    """
    bad: list[str] = []
    for name in script_names:
        n = str(name)
        if n == "nano:gpfb" or n.startswith("nano:gpfb:") and not n.startswith(
            "nano:gpfb4"
        ):
            bad.append(n)
            continue
        if n.startswith("nano:gpfb4"):
            continue
        for pref in (
            "nano:stream",
            "nano:gencache",
            "nano:kvcache",
            "nano:mixd",
            "nano:rag",
            "nano:ctx",
        ):
            if n == pref or n.startswith(pref + ":") or n.startswith(pref + "-"):
                bad.append(n)
                break
    return bad


def wave_status_ok(texts: Mapping[str, str]) -> bool:
    """
    GIVEN wave doc bodies
    WHEN checking close-out
    THEN True iff each required doc contains COMPLETE.
    """
    for path in WAVE_COMPLETE_DOCS:
        body = str(texts.get(path, ""))
        if "COMPLETE" not in body:
            return False
    return True


def recipes_use_promotes_kill(recipes_md: str) -> list[str]:
    """
    GIVEN RECIPES.md body
    WHEN scanning Use cells for banned promote tokens
    THEN return tokens found in Use column (not Do-not-claim).
    """
    hits: list[str] = []
    # Table rows: | **Goal** | scope | **Use** | Do not |
    row_re = re.compile(
        r"^\|\s*\*\*[^*]+\*\*\s*\|\s*[^|]+\|\s*([^|]+)\|\s*([^|]+)\|",
        re.MULTILINE,
    )
    bans = ("STREAM", "GENCACHE", "KVCACHE-Q", "MIXD", "naive CTX", "H-STREAM")
    for m in row_re.finditer(str(recipes_md)):
        use = m.group(1)
        for ban in bans:
            if ban in use:
                hits.append(ban)
    # GPFB K=2 must not appear as Use (K=4 / GPFB4-LONG ok).
    for m in row_re.finditer(str(recipes_md)):
        use = m.group(1)
        if re.search(r"GPFB\s*K\s*=\s*2", use) or "GPFB K=2" in use:
            hits.append("GPFB_K2")
    return sorted(set(hits))


def decide_lab_freeze(
    *,
    archive_exists: Mapping[str, bool],
    script_names: Sequence[str],
    wave_texts: Mapping[str, str],
    recipes_md: str,
) -> str:
    """
    GIVEN archives + scripts + wave docs + RECIPES
    WHEN applying §8 #6 NO-REOPEN
    THEN PROMOTE iff all checks pass; else KILL with reason.
    """
    miss = missing_archives(archive_exists)
    if miss:
        return f"KILL (missing archive: {miss[0]})"
    bad = banned_scripts(script_names)
    if bad:
        return f"KILL (reopened runner: {bad[0]})"
    if not wave_status_ok(wave_texts):
        return "KILL (wave docs missing COMPLETE)"
    promo = recipes_use_promotes_kill(recipes_md)
    if promo:
        return f"KILL (RECIPES Use promotes {promo[0]})"
    return f"PROMOTE ({LAB_FREEZE_ID}: NO-REOPEN; archives intact)"


def load_npm_script_names(package_json: str) -> list[str]:
    """Parse script keys from package.json text."""
    data = json.loads(package_json)
    scripts = data.get("scripts") or {}
    return [str(k) for k in scripts.keys()]
