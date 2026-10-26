# Teams formatting: what exists and what survives a paste

Two different questions:

1. **What can Teams show?** Whatever its own compose box can produce.
2. **What survives a paste?** Teams converts the clipboard's `text/html` into its own editor model. Anything its editor cannot represent is dropped. So the paste-safe set is, at most, the compose-box set.

Status legend: **Compose** = in the Teams Format menu, so Teams can render it. **Expected** = standard rich paste, very likely kept. **Unverified** = depends on the Teams build or tenant. **No** = not supported. The **Verified** column records results from the Format Lab (`assets/format-lab.html`) in the user's own tenant: fill it with ✅ / ❌ and the date.

## Capability matrix

| Lab | Feature | HTML to write | Status | Verified | Notes |
|---|---|---|---|---|---|
| ① ② | Headings 1–3 | `<h1>`–`<h3>` | Compose | | Teams has no H4–H6. |
| ③ | Bold, italic, underline, strike | `<strong> <em> <u> <s>` | Compose | | |
| ③ | Inline code | `<code>` | Compose | | |
| ③ | Link | `<a href="https://…">` | Compose | | Absolute URLs only. |
| ④ | Text color | `<span style="color:#hex">` | Compose | | Teams' own picker has a fixed palette; arbitrary hex values may be kept or snapped. Check in the lab. |
| ⑤ | Highlight | `<span style="background-color:#hex;color:#1A1A1A">` | Compose | | |
| ⑥ | Highlight without text color | `<span style="background-color:#hex">` | Unverified | | In dark mode the default text turns white, which is unreadable on yellow. Always set a dark text color. |
| ⑦ | Status chip (solid background + white text) | `<span style="background-color:#107C10;color:#FFFFFF;font-weight:600">` | Unverified | | Padding and rounded corners are always dropped; `&nbsp;` gives the label room. |
| ⑧ | Font size | `<span style="font-size:12px">` | Compose (Small / Medium / Large) | | Pixel values may be mapped to the three sizes or dropped. |
| ⑨ | Centered text | `<p style="text-align:center">` | Unverified | | Not in the Format menu. Do not depend on it. |
| ⑩ | Custom font | `font-family` | No | | Teams always uses its own font. |
| ⑪ | Bulleted, numbered, nested lists | `<ul> <ol> <li>` | Compose | | |
| ⑫ | Emoji | Unicode emoji | Expected | | Teams may swap them for its own Fluent emoji art. |
| ⑬ | Quote | `<blockquote>` | Compose | | |
| ⑭ | Code block | `<pre><code>` | Compose | | Teams' own code blocks add a language picker; a pasted block may land as plain monospaced text. |
| ⑮ | Table | `<table>` with `<thead>` | Compose | | Cell background colors are uncertain; colored text inside cells is more reliable. |
| ⑯ | Horizontal rule | `<hr>` | Compose | | |
| ⑰ | Superscript / subscript | `<sup> <sub>` | No | | Microsoft Q&A: pasted super/subscript shows as italic. Use Unicode ² ³ ₂. |
| ⑱ | @mention | (text) | No | | Mentions are entities, not HTML. Retype them in Teams. |
| ⑲ | Inline image | `<img src="data:image/png;base64,…">` | Unverified | | Teams post limits exclude base64 images, which hints that inline images are stored; paste behavior is not documented. |

## Teams-only features (cannot come from the clipboard)

Channel subject line, announcement banner and background, Important / Urgent flag, GIFs and stickers, Loop components, file attachments, live @mentions, scheduled send. Add them in Teams after pasting.

## Known paste quirks

- **Ctrl+V vs Ctrl+Shift+V.** Ctrl+V pastes the HTML flavor. Ctrl+Shift+V pastes plain text, so all formatting is lost.
- **Right-click Paste** has been unreliable in recent Teams desktop builds; use Ctrl+V.
- **Leading spaces and indentation** are stripped. Use lists for hierarchy and code blocks for code.
- **Dark mode** does not recolor custom text colors. Pick colors that read on both themes (palette in SKILL.md).

## Size limit

A Teams chat message or channel post holds about **100 KB**, including @mentions and reactions; Microsoft advises staying under **80 KB**. Base64 images do not count toward that limit. The page shows a size meter and the lint warns above 80 KB.

## Sources

- Microsoft Support, "Format a message in Microsoft Teams": Format menu with bold, italic, underline, strikethrough, highlight, font color, font size (Large / Medium / Small), lists, clear formatting.
- Microsoft Learn, "Format agent messages" (Teams platform): Teams renders a basic HTML subset (b/strong, i/em, u, s, br, hr, a, img).
- Microsoft Learn, Graph "Send chatMessage": the Teams client has specific HTML restrictions; `<div>` and inline styles may not work as intended.
- Microsoft Q&A: Teams chat supports bold, italic, underline, font size, font color, highlight and lists; pasted superscript/subscript shows as italic.
- Microsoft Learn, "Limits and specifications for Microsoft Teams": about 100 KB per chat message or channel post; keep under 80 KB; base64 images excluded.
- Microsoft Tech Community and Q&A threads: Teams strips leading indentation on paste; Ctrl+Shift+V pastes plain text; right-click Paste issue in recent desktop builds.

## Verification log

| Date | Teams client (desktop / web / mobile) | Result |
|---|---|---|
| | | |
