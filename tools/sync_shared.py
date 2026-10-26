#!/usr/bin/env python3
"""Copy the files in shared/ into every skill that uses them.

Each skill must stay complete on its own, so shared files are copied, not linked.
Usage: python3 tools/sync_shared.py          copy
       python3 tools/sync_shared.py --check  only report skills that are out of date (exit 1)
"""
import sys, shutil, filecmp
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"
TARGETS = {"tapkit-ui.md": "references/tapkit-ui.md", "github-mark.svg": "assets/github-mark.svg"}

check = "--check" in sys.argv
stale = []
for skill in sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()):
    for name, rel in TARGETS.items():
        src, dst = SHARED / name, skill / rel
        if not dst.exists():          # the skill does not use this file
            continue
        if filecmp.cmp(src, dst, shallow=False):
            continue
        stale.append(f"{skill.name}/{rel}")
        if not check:
            shutil.copyfile(src, dst)
for s in stale:
    print(("out of date: " if check else "updated: ") + s)
if not stale:
    print("All skills match shared/.")
sys.exit(1 if check and stale else 0)
