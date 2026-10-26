---
name: tap-teams-message
description: Writes richly formatted Microsoft Teams messages (emoji, bold, colors, highlights, lists, tables, quotes, copy-friendly snippets) for chats, group chats, meeting chats and channels, then delivers a polished self-contained HTML page with a Teams preview, fill-in fields, on/off switches and a "Copy for Teams" button that puts paste-ready rich text on the clipboard. Use it whenever the user wants to write, format, polish or make look good any Teams message, post, recap, follow-up, reminder, update, invitation, announcement, maintenance notice or kudos, even if they never mention HTML, a page or a button ("send this to the team in Teams", "recap of today's call for the chat", "format this for Teams", "mensaje para el chat de Teams", "resumen de la reunión para el chat"). Also use it when the user gives a tap-teams-message recipe file. Not for Slack, email, Adaptive Cards, Teams bots or Graph API automation.
---

# tap-teams-message (TapKit)

The work happens in two phases:

- **Phase A, in your head:** settle the settings and design the message with the right Teams formats. Do not show a draft in the chat: users who see a draft think that is all the skill does. The interactive page is the product.
- **Phase B, the page:** build one HTML page right away. It previews the message the way Teams renders it, offers fields for `[placeholders]`, switches for emoji and optional parts, edit in place, save options, and **Copy for Teams**. Teams reads the clipboard's HTML flavor on Ctrl+V; the page also writes a plain-text flavor.

Most messages go to **chats**: one-to-one, group chats, and the chat of a meeting or call. Channel posts are the less common case.

## Phase A: settings and design

### 1. Settings

Settle these before writing. Take what the user said or what the request implies, use the defaults for the rest, and ask only what you cannot infer and that changes the message (for example who the audience is, when it is unclear). If there is a question tool, ask everything in one round of short multiple-choice questions.

| Setting | Values | Default |
|---|---|---|
| `channel` | `chat` (1:1), `group_chat`, `meeting_chat`, `channel` | `group_chat` |
| `tone` | `formal`, `friendly`, `festive`, `urgent` | `friendly` |
| `emoji` | `none`, `few` (one per line or heading, at most), `many` | `few` |
| `header` | `none`, `bold_line`, `heading` | `bold_line` in chats, `heading` in channels |
| `cta` | `none`, `reply`, `link`, `decide`, `attend` | what the content needs, or `none` |
| `signoff` | `none`, `name`, `team` | `none` in chats unless asked, `name` in channels |
| `length` | `short` (3 to 5 lines), `standard`, `detailed` | `short` in chats, `standard` in channels |
| `language` | the language of the message | the user's language |
| `pattern` | a name from `references/message-patterns.md`, or `custom` | the closest pattern |

What the channel changes:

- **Chats** (`chat`, `group_chat`, `meeting_chat`): conversational, short, no subject line, at most one or two small headings. Lead with the point.
- **Meeting chat** usually means a recap or a follow-up: decisions, action items with owners and dates, next meeting.
- **Channel**: more structure, headings allowed, and remind the user to add a subject line in Teams (it cannot be pasted).

### 2. Design with the formatting playbook

Before writing, scan the content and choose formats on purpose. Use every format the content calls for; do not add formats the content does not need.

| When the content has… | Use | HTML |
|---|---|---|
| One main point | A bold first line, or a heading in channels, naming the point and the date | `<p><strong>…</strong></p>` or `<h2>` / `<h3>` |
| Facts in two dimensions (date × event, owner × task × due date, option × pros) | A **table**. Teams renders tables very well. Keep header words short ("Owner", "Due") so they do not wrap. | `<table><thead><tr><th>…` |
| Steps in order | A numbered list | `<ol>` |
| Several separate points | A bulleted list, one emoji per line when `emoji` allows | `<ul>` |
| Text people will copy (a command, a prompt, an address, an ID, a template, a code) | A **snippet**. One triple-click selects all of it. Put only the final text inside: snippets do not get fill-in fields. | `<pre><code>…</code></pre>` |
| A decision, a warning or a quote | A quote block | `<blockquote><p>…</p></blockquote>` |
| A status | A colored chip | see the palette below |
| Something to do | A call-to-action line with 👉 and a real link when one exists | `<p data-part="cta">👉 …</p>` |
| Text the reader should not miss but cannot act on (a help line, "reply if I missed something") | A plain line after the call to action, outside the `cta` part | `<p>❓ …</p>` |
| A word that must not be missed | Bold, a palette color or a highlight, sparingly | see below |
| A small aside | Small print | `<span style="font-size:12px">` |
| A break between two different parts (the news and the logistics, the summary and the details) | A divider. In chats, one at most; never two in a row or right after a heading. | `<hr>` |

### 3. Build the page, then revise from the conversation

Go straight to the page. Never post the message text in the chat before the page exists, and never ask "should I build the page?". Ask a question first only when the purpose or the audience is unclear; otherwise use the defaults and say which ones you used in your delivery note.

After the page is delivered, rewriting still happens in the conversation: when the user asks for another tone, a shorter version, a sign-off or a channel version, change the fragment or the settings and rebuild the page to the same path. Small fixes (a word, a date, emoji on or off) the user can make on the page.

If the user explicitly asks to see a draft first, show it, start it with "Draft (the interactive page comes next)", and build the page as soon as they accept it.

Facts:

- **Missing facts:** never invent them. Use `[square brackets]` with a clear label (`[start date]`, not `[X]`). Each label becomes a field the user fills in the page, and the same label always means the same value. A link without a known URL uses `href="[registration link]"`.
- **Field types:** the page gives each blank the right input. Add the type after a colon when the label does not make it obvious:
  - `[start date:date]` date picker; the value appears as "Friday, November 6" (or "viernes, 6 de noviembre") in the message language,
  - `[start:time]` time picker, `[kickoff:datetime]` date and time,
  - `[attendees:number]`, `[support:email]`, `[form:url]`,
  - `[status:choice=On track|At risk|Blocked]` a list of options,
  - `[team photo:image]` an image slot: the user pastes, drops or chooses an image in the Data panel. Put an image slot in its own paragraph (`<p>[team photo:image]</p>`). Use it when the user mentions a photo, screenshot, chart or banner they will add.
  Without a type, the wording decides: "date/fecha/day/due" gives a date picker, "time/hora" a time picker, "email/correo" an email field, "number/total/amount" a number field. Use the same full label (type included) every time the same fact appears.
- **Undecided facts** ("no date yet", "TBD") are not placeholders: write them as text, for example "⏳ To be decided" in the message language, so the page does not ask the user for something nobody knows.
- **Relative dates** ("on Thursday", "end of month"): when today's date is known, write weekday plus date ("Thursday, October 29") so readers in other time zones and later readers agree. "End of month" is the last calendar day; if it falls on a weekend, say so in your delivery note. Mention in the delivery note that you added the dates.
- **Conflicting facts:** check what you can. For a date and a weekday, compute the weekday (`python3 -c "import datetime; print(datetime.date(2026, 11, 7).strftime('%A'))"`), assuming the next occurrence of the date when no year is given. If they conflict, bracket both options (`[Friday 6 or Saturday 7] November`) and say so.

## Phase B: build the page

1. **Write the fragment** as Teams-safe HTML (subset below) in `<slug>.message.html`, next to where the page will go. Mark the optional parts so the page can switch them on or off:
   - `data-part="header"` on the header line or heading,
   - `data-part="cta"` on the call-to-action line,
   - `data-part="signoff"` on the closing and signature.
2. **Write the settings** as JSON in `<slug>.settings.json`, using the canonical values from the table, for example `{"channel": "meeting_chat", "tone": "friendly", "emoji": "few", "header": "bold_line", "cta": "reply", "signoff": "name", "length": "standard", "language": "es", "pattern": "meeting_recap"}`.
3. **Build:**
   ```bash
   python3 <skill-dir>/scripts/build_teams_message.py --body <slug>.message.html \
       --settings <slug>.settings.json --out <slug>.html --sender "<user name>" --lang <en|es>
   ```
   - `--lang` sets the language of the whole page UI: tabs, panels, buttons, How To and About (en or es; any other language falls back to `en`). Use the language the user writes in. The footer is the brand signature and stays in English. The message itself can be in any language.
   - `--sender` is only the name in the preview (use the user's full name). In Teams the author is whoever pastes the message, so use the user's own name when known. A team signature goes in the message, inside the sign-off part.
   - `--title` is optional; by default the page title is the header line.
   - The script lints first. Fix every `ERROR`. Read every `WARN` and fix it unless it is deliberate. `INFO` lines are reminders for your delivery note.
4. **Check** when Playwright is available: `python3 <skill-dir>/scripts/check_page.py <slug>.html --out-dir <scratch>`. It saves desktop and mobile screenshots, tests the copy button and prints the plain text. Look at the screenshots. They are for you, not deliverables, so keep them out of the user's folder.
5. **Deliver** the `.html` page as a file (Claude.ai) or save it where the user works (Claude Code). Never paste the HTML source or the message text into the chat. Keep the note short and make the page the clear next step:
   - first line: the page is ready, for example "Your Teams message page is ready: open it in Edge or Chrome.",
   - what to do there: fill the blanks (say how many), adjust settings, edit if needed, then **Copy for Teams** and Ctrl+V,
   - the defaults you assumed, in one line, and that you can rebuild it with another tone, length or format,
   - conflicting facts, @mentions to retype, and for a channel post a suggested subject line.
6. **Revisions:** change the fragment or the settings and rebuild to the same path. Never hand-edit the built page.

## Recipes

The page can save a **recipe**: a markdown file with the settings in front matter and the last message as Teams-safe HTML. When the user gives you a recipe ("write this week's update from this recipe"):

- reuse its settings and its structure (sections, tables, marked parts, order),
- replace only the facts with the new ones, using placeholders for anything missing,
- build the page right away, as usual.

Recurring messages (weekly status, meeting recaps, workshop follow-ups) benefit most. Offer to save a recipe when the user says a message repeats.

## Teams-safe subset

| Need | Write | Notes |
|---|---|---|
| Paragraph | `<p>` | All text sits inside a block. |
| Line break | `<br>` | For emoji lines inside one paragraph. |
| Headings | `<h1>` `<h2>` `<h3>` | Teams has three levels. In chats prefer a bold first line. |
| Emphasis | `<strong>` `<em>` `<u>` `<s>` | |
| Text color | `<span style="color:#2F80ED">` | Dual-mode palette only. |
| Highlight | `<span style="background-color:#FFF100;color:#1A1A1A">` | Always with the dark text color on the same span. |
| Small print | `<span style="font-size:12px">` | |
| Lists | `<ul>` `<ol>` `<li>` | Nest up to 3 levels. |
| Quote | `<blockquote><p>…</p></blockquote>` | |
| Code | `<code>`, `<pre><code>` | Snippets: one triple-click copies them. |
| Table | `<table><thead><tr><th>`… | Teams draws the borders. Up to about 5 columns, short cells. |
| Divider | `<hr>` | |
| Link | `<a href="https://…">text</a>` | Absolute URLs only. |

**Teams drops:** `class`, `id`, `<style>`, `<div>` layout, padding, margin, borders, border-radius, width, flex or grid, `font-family`, `<sup>` and `<sub>` (shown as italic), `<h4>` to `<h6>`. The message must still read well if only the tags survive.

**Cannot come through a paste** (tell the user to add them in Teams when they matter): live @mentions, the channel subject line, the announcement banner, the Important or Urgent flag, GIFs, stickers, Loop components, file attachments. Do not write `<img>` tags yourself; use an image slot. In edit mode the user can also paste, drop or insert images anywhere. Images are resized to 1000 px and embedded; Teams does not count embedded images toward the message limit. Format Lab item ⑲ checks that pasted images show in the user's Teams.

## Dual-mode palette

Readers use light or dark Teams, so every color must read on both. These pass 3:1 on white and on the dark bubble (#292929). Use them for short bold text, never for whole paragraphs.

| Red | Orange | Gold | Green | Teal | Blue | Purple | Pink | Gray |
|---|---|---|---|---|---|---|---|---|
| `#E04B4F` | `#D9640F` | `#A67C00` | `#1B9E52` | `#0A9396` | `#2F80ED` | `#8B6FE8` | `#D24DB0` | `#808080` |

- **Highlights**, always with `color:#1A1A1A`: yellow `#FFF100`, mint `#C6F6D5`, sky `#D0EBFF`, peach `#FFD8A8`, rose `#FCC2D7`.
- **Status chips**, in the message language, padded with `&nbsp;`:
  - green: `background-color:#107C10;color:#FFFFFF;font-weight:600`
  - red: `background-color:#C4314B;color:#FFFFFF;font-weight:600`
  - amber: `background-color:#FFF100;color:#1A1A1A;font-weight:600`
- Never use black, near-black, white or pale text colors.

## Writing rules

- **Key fact first.** The first line is what people see in notifications and the chat list: what happens and when.
- **Emoji are the icons of Teams.** With `few`, one per line, list item or heading at most (a status emoji inside a table cell is fine), with stable meanings: ✅ done, ⏳ in progress, ⚠️ risk, 🚫 blocked, 📅 date, 🕘 time, 📍 place, 🔗 link, 👉 main action, 📞 contact, 🛠️ maintenance, 🩹 workaround, 🎉 celebration, ❓ question. With `none`, use none at all. The page can also switch emoji off.
- **Tone:** `formal` has no jokes and few emoji; `friendly` is warm and direct; `festive` allows celebration emoji and exclamation marks; `urgent` puts the deadline in the first line and keeps every line short.
- **Actions:** one main action, near the end, inside the `cta` part. Its wording follows the `cta` setting (reply, open a link, decide by a date, attend). A help or contact line goes after it, outside the part. A link placeholder fills only the address, so write link text that reads well on its own ("Open the Power BI workspace").
- **Locale:** write dates and times the way readers write them, and add the time zone for distributed teams. Spanish team messages usually address readers as "ustedes".
- Bold carries the scan: at most 1 to 3 bold phrases per paragraph.

For a message that matches a common type, read `references/message-patterns.md` and start from its skeleton. The skeletons are in English: translate them naturally into the message language (for example "recap" is "resumen" in Spanish), do not copy English labels.

## Format Lab

`assets/format-lab.html` tests 19 features, one numbered line each. When the user asks what Teams supports or says a format disappeared after pasting, build it:

```bash
python3 <skill-dir>/scripts/build_teams_message.py --body <skill-dir>/assets/format-lab.html --out teams-format-lab.html
```

Ask the user to paste it into a chat with themselves, in light and dark mode, and report the numbers that broke. Record the results in `references/teams-formatting.md`. The **About this skill** tab of every page also has a copyable format sample.

## Files

- `scripts/build_teams_message.py`: lint and build (Python standard library only).
- `scripts/check_page.py`: screenshots and a copy-button test (needs Playwright).
- `assets/template.html`: the page in the TapKit App Shell (TapKit frame with band and teal footer around one skill card: skill header, side navigation with Download and Save recipe, views). "Use the skill" view: a workspace with collapsible Data and Settings panels and the Preview panel (Edit, Copy for Teams, edit toolbar with formatting, Teams-safe colors, emoji picker, links). Light theme only. Message-specific content never goes here.
- `assets/howto.{en,es}.html`, `assets/about.{en,es}.html`, `assets/showcase.{en,es}.html`: the How To view (steps, format playbook, copyable format sample) and the About view (what it does, TapKit, authorship).
- `references/tapkit-ui.md`: the TapKit App Shell rules shared by all TapKit skills.
- `assets/format-lab.html`: the capability test message.
- `references/teams-formatting.md`: capability matrix, evidence and verification log.
- `references/message-patterns.md`: skeletons for chat and channel messages.

## About

Part of **TapKit**, a personal collection of AI skills by Alfredo De Regil.
tap-teams-message version 1.0 (2026). Get it at https://github.com/aderegil/tapkit
Made by Alfredo De Regil
