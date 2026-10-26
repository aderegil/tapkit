# TapKit App Shell v1.2

Shared layout and rules for every TapKit page. A skill that produces an HTML page copies this shell and fills its own views.

## Two levels: the TapKit frame and the skill card

```
  Frame color (#CBE3E0) ─────────────────────────────────────────────────
   mark  TapKit ............................................ chevron mark    ← TapKit band, no functions
  ┌──────────────────────────────────────────────────────────────────────┐
  │ skill-id (large monospace)                                           │  ← skill header, 3px Deep teal line under it
  │ one-line tagline                                                     │
  ├────────┬─────────────────────────────────────────────────────────────┤
  │ Nav    │  Workspace (light gray)                                     │
  │ Use    │  ┌ ▾ DATA ──────┐  ┌ RESULT title ....... [Edit] [Primary]┐ │
  │ How To │  │ inputs       │  │ (edit toolbar while editing)          │ │
  │ About  │  └──────────────┘  │                                       │ │
  │        │  ┌ ▸ CONFIG ────┐  │ the result                            │ │
  │ ────── │  └──────────────┘  │                                       │ │
  │ Save   │                    └───────────────────────────────────────┘ │
  │ [Down] │                                                             │
  │ [Rcpe] │                                                             │
  └────────┴─────────────────────────────────────────────────────────────┘  ← skill card: white, 1px border, 4px corners
  Footer (Deep teal, compact, English): collection, skill + version, repo link
```

- **TapKit frame:** the band (mark + "TapKit" + chevron watermark) and the footer, on the frame color. It only says which collection the skill comes from. It holds no functions.
- **Skill card:** everything that belongs to the skill. The skill header (skill id + tagline, nothing else) spans the card. Below it, the nav rail sits inside the card, left of the views.
- **Workspace (Use view):** three panels on a light gray ground. Left, stacked: DATA and CONFIG. Right: the RESULT panel.

## Rules

- **Identity:** the skill header shows the skill id in large monospace with a one-line tagline. It stays the same on the three tabs. The result (message, document…) keeps its own title inside the result panel.
- **Three views, always:** Use the skill, How To, About. The tab names follow the page language. Views have no header of their own; the skill header is shared.
- **Panels:** each panel is a white box with a 1px border, 4px corners and its own title. DATA and CONFIG are collapsible (a chevron before the title; the whole title row toggles). DATA starts open when there is something to fill and closed when there is nothing; CONFIG starts closed. The page remembers the state per viewer (localStorage, in try/catch). The DATA title row keeps its counter visible when closed ("2 left").
- **CONFIG and DATA never share a panel.** DATA holds the values the user must provide (placeholders, inputs). CONFIG holds settings that change how the result looks (switches, choices).
- **Result panel:** its title row says what it shows ("Preview") and holds the controls that act on the result: Edit and the primary action (Copy for Teams). Tools that appear while editing go right under that row, inside the panel.
- **Save actions:** Download and Save recipe live at the bottom of the nav rail under a small "Save" label, separated from the tabs by a line. They show only on the Use tab. At 1180px and below they become icon buttons; on phones they sit at the end of the tab row.
- **Buttons:** keep them simple. Same height and style everywhere: an icon plus a short text, as wide as the text needs, and a tooltip (`title`) that explains in one sentence what it does, in the page language. Only the primary action is filled with Deep teal; the others are outlined. Stacked buttons in the rail share the rail width.
- **After the primary action:** a large centered notice in solid Deep teal confirms it in two short lines ("Copied!" / "Now paste it in Teams."), with a square white check icon. No button: it closes by itself after 2.5 s, on a click or on Esc. Small notices (warnings, saved files) stay as toasts.
- **No page scroll on desktop.** The page fits the window at 1366×768 and larger. If content is longer, only a panel scrolls inside itself. Never horizontal scroll.
- **Responsive:** at 1180px and below, the nav shows icons only and the left panels get narrower. At 820px and below, the card loses its side margins, everything stacks in one column (DATA, CONFIG, result), the nav becomes a row of tabs, and only then the page scrolls vertically.
- **Light theme only.** No dark mode for the page and no light/dark switch. (A skill whose result has its own themes, like Teams, must still pick result colors that work in both of the result's themes.)

## Tokens

| Token | Value | Use |
|---|---|---|
| `--brand` | #0E7C7B | mark, header line, footer |
| `--act` | #0E7C7B | primary button, switches, focus |
| `--frame` | #CBE3E0 | TapKit frame behind the card |
| `--rail` | #EEF7F6 | nav rail inside the card |
| `--card-line` | #B7D2CF | card border |
| `--ws` | #EDF1F1 | workspace ground behind the panels |
| `--panel-line` | #D6DEDE | panel borders |
| `--r` | 4px | corner radius for the card, panels and every control |

- The frame is darker than the rail, so the two levels read apart. Never give them the same color.
- **One brand moment:** the mark in the band. Solid colors only: no gradients.
- **Corners:** 4px everywhere. Nothing round: no pills, circles or bubbles, switches included (3px). The only exception is what imitates the result itself, like the Teams avatar in the preview.
- **Language:** the whole UI in the user's language (en or es, fallback en). The footer stays in English.
- **Footer:** left, two lines: "**TapKit** AI skills that give you results on tap." and "**<skill-id>** v<version> <what it does>." Right, vertically centered, no underline (underline on hover): the link github.com/aderegil/tapkit with the GitHub mark at the far right (from assets/github-mark.svg; a code icon until that file exists). No TapKit mark in the footer. Authorship lives in the About view.
- **Avoid template look:** no decorative gradients, no soft drop shadows on cards or panels, no large rounded corners, no all-caps labels, no arrows appended to buttons.
