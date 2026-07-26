"""Validate Wave Z trial JSON (nano:z:log-trial)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from z_trial import validate_trial


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    args = ap.parse_args()
    data = json.loads(args.path.read_text(encoding="utf-8"))
    errs = validate_trial(data)
    if errs:
        print(json.dumps({"ok": False, "errors": errs}))
        return 2
    print(json.dumps({"ok": True, "trial_id": data.get("trial_id")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
