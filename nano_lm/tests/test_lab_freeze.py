"""Contract: lab freeze NO-REOPEN (§8 #6)."""

from __future__ import annotations

from lab_freeze_ops import (
    KILL_ARCHIVES,
    LAB_FREEZE_ID,
    WAVE_COMPLETE_DOCS,
    banned_scripts,
    decide_lab_freeze,
    load_npm_script_names,
    missing_archives,
    recipes_use_promotes_kill,
    wave_status_ok,
)


def test_given_all_archives_when_missing_then_empty() -> None:
    ok = {p: True for p in KILL_ARCHIVES.values()}
    assert missing_archives(ok) == []


def test_given_miss_stream_when_missing_then_label() -> None:
    ok = {p: True for p in KILL_ARCHIVES.values()}
    ok[KILL_ARCHIVES["STREAM"]] = False
    assert missing_archives(ok) == ["STREAM"]


def test_given_gpfb4_when_banned_scripts_then_ok() -> None:
    assert banned_scripts(["nano:gpfb4", "nano:formal:hgpfb4"]) == []


def test_given_stream_runner_when_banned_then_hit() -> None:
    assert "nano:stream" in banned_scripts(["nano:stream", "nano:z:ask"])


def test_given_gpfb_k2_runner_when_banned_then_hit() -> None:
    assert "nano:gpfb" in banned_scripts(["nano:gpfb"])
    assert banned_scripts(["nano:gpfb:smoke"]) == ["nano:gpfb:smoke"]


def test_given_complete_waves_when_status_then_ok() -> None:
    texts = {p: "Status: COMPLETE\n" for p in WAVE_COMPLETE_DOCS}
    assert wave_status_ok(texts) is True


def test_given_recipes_use_stream_when_scan_then_hit() -> None:
    md = (
        "| Goal | L | Use | Never |\n"
        "|------|---|-----|-------|\n"
        "| **Bad** | @128 | **H-STREAM** only | — |\n"
    )
    assert "STREAM" in recipes_use_promotes_kill(md) or "H-STREAM" in (
        recipes_use_promotes_kill(md)
    )


def test_given_good_freeze_when_decide_then_promote() -> None:
    archives = {p: True for p in KILL_ARCHIVES.values()}
    texts = {p: "COMPLETE" for p in WAVE_COMPLETE_DOCS}
    recipes = (
        "| Goal | L | Use | Never |\n"
        "| **Code** | @128 | **H-ABS-QPFB2** | STREAM |\n"
    )
    out = decide_lab_freeze(
        archive_exists=archives,
        script_names=["nano:z:ask", "nano:gpfb4"],
        wave_texts=texts,
        recipes_md=recipes,
    )
    assert out.startswith("PROMOTE")
    assert LAB_FREEZE_ID in out


def test_given_package_json_when_load_then_scripts() -> None:
    names = load_npm_script_names('{"scripts":{"nano:z:z6":"x","a":"b"}}')
    assert "nano:z:z6" in names
