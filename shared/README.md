# shared

Files that every TapKit skill uses. Edit them here, never inside a skill.

| File | Copied into each skill as |
|---|---|
| `tapkit-ui.md` | `references/tapkit-ui.md` (TapKit App Shell rules) |
| `github-mark.svg` | `assets/github-mark.svg` (footer repo link) |

Run `python3 tools/sync_shared.py` after a change. It copies these files into every skill that already has them, so each skill folder stays complete on its own (Claude needs every file inside the skill folder). `tools/sync_shared.py --check` fails if a skill is out of date.
