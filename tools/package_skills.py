#!/usr/bin/env python3
"""Zip each skill in skills/ into dist/<skill>.zip, ready to upload to Claude or attach to a GitHub release.

Usage: python3 tools/package_skills.py [skill-name ...]
Each zip holds the skill folder itself (tap-teams-message/SKILL.md, ...), the layout Claude expects.
"""
import sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS, DIST = ROOT / "skills", ROOT / "dist"
SKIP_DIRS = {"__pycache__", ".git", "node_modules"}
SKIP_FILES = {".DS_Store"}

def package(skill: Path) -> Path:
    if not (skill / "SKILL.md").is_file():
        raise SystemExit(f"{skill.name}: SKILL.md not found")
    DIST.mkdir(exist_ok=True)
    out = DIST / f"{skill.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(skill.rglob("*")):
            rel = f.relative_to(skill)
            if f.is_dir() or f.name in SKIP_FILES or SKIP_DIRS & set(rel.parts) or f.suffix == ".pyc":
                continue
            z.write(f, Path(skill.name) / rel)
    return out

names = sys.argv[1:] or sorted(p.name for p in SKILLS.iterdir() if p.is_dir())
for name in names:
    out = package(SKILLS / name)
    print(f"{out.relative_to(ROOT)}  ({out.stat().st_size // 1024} KB)")
