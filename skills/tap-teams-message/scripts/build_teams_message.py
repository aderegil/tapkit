#!/usr/bin/env python3
"""Lint a Teams-safe HTML message fragment and build the self-contained preview + copy page.

Usage:
  python3 build_teams_message.py --body message.html --out page.html
         [--title "Q4 kickoff"] [--sender "Ana Ruiz"] [--lang en|es] [--settings settings.json]
         [--check] [--force]

  --check   lint only, do not write the page
  --force   build even when the lint finds errors

Standard library only. Exit code 1 when the lint finds errors (unless --force).
"""
import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
TEMPLATE = ASSETS / "template.html"

# ---------------------------------------------------------------- Teams-safe subset
SAFE_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "s", "strike", "del", "span", "a",
    "h1", "h2", "h3", "ul", "ol", "li", "blockquote", "pre", "code",
    "table", "thead", "tbody", "tr", "th", "td", "hr",
}
VOID_TAGS = {"br", "hr", "img", "wbr", "meta", "link", "input"}
BLOCKED_TAGS = {"script", "style", "iframe", "object", "embed", "form", "input", "button",
                "link", "meta", "svg", "canvas", "video", "audio", "template"}
TEXT_HOMES = {"p", "h1", "h2", "h3", "li", "blockquote", "pre", "td", "th"}
TAG_HINTS = {
    "div": "use <p> for paragraphs; Teams flattens <div> and drops its layout styles",
    "h4": "Teams has Heading 1-3 only; use <h3> or a bold <p>",
    "h5": "Teams has Heading 1-3 only; use <h3> or a bold <p>",
    "h6": "Teams has Heading 1-3 only; use <h3> or a bold <p>",
    "img": "inline images are not verified for paste; test with Format Lab item 19, or attach the image in Teams",
    "sup": "Teams shows superscript as italic; use Unicode (², ³) or plain text",
    "sub": "Teams shows subscript as italic; use Unicode (₂) or plain text",
    "font": "use <span style=\"color:...\"> instead of <font>",
    "center": "use style=\"text-align:center\" on the <p> (may still be dropped)",
    "mark": "use <span style=\"background-color:#FFF100;color:#1A1A1A\">",
    "small": "use <span style=\"font-size:12px\">",
    "big": "use a heading or <span style=\"font-size:18px\">",
}
SAFE_STYLE = {"color", "background-color", "font-size", "font-weight", "font-style",
              "text-decoration", "text-align"}
OK_ATTRS = {"style", "href", "colspan", "rowspan", "title", "target", "rel", "src", "alt", "width", "height"}

LIGHT_BG = (255, 255, 255)   # Teams light message bubble
DARK_BG = (41, 41, 41)       # Teams dark message bubble (#292929)
NAMED = {
    "black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
    "yellow": "#ffff00", "orange": "#ffa500", "purple": "#800080", "gray": "#808080", "grey": "#808080",
    "navy": "#000080", "maroon": "#800000", "teal": "#008080", "silver": "#c0c0c0", "lime": "#00ff00",
    "fuchsia": "#ff00ff", "aqua": "#00ffff", "pink": "#ffc0cb", "gold": "#ffd700",
}
SIZE_WARN_BYTES = 80 * 1024   # Teams posts cap near 100 KB; Microsoft advises staying under 80 KB


def parse_color(value):
    if not value:
        return None
    v = value.strip().lower()
    v = NAMED.get(v, v)
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*[\d.]+)?\s*\)", v)
    if m:
        return tuple(min(255, int(x)) for x in m.groups())
    return None


def luminance(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def parse_style(text):
    props = {}
    for decl in (text or "").split(";"):
        if ":" in decl:
            k, v = decl.split(":", 1)
            if k.strip():
                props[k.strip().lower()] = v.strip()
    return props


class Linter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.issues = []
        self.stack = []
        self.h1_count = 0
        self.mention_seen = False
        self.placeholders = []

    def add(self, level, text):
        self.issues.append((level, self.getpos()[0], text))

    # -- tags
    def handle_starttag(self, tag, attrs):
        self._check_tag(tag, attrs)
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self._check_tag(tag, attrs)

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack:
                if self.stack.pop() == tag:
                    break

    def handle_data(self, data):
        if data.strip() and not any(t in TEXT_HOMES for t in self.stack):
            self.add("warn", f"text outside a block ({data.strip()[:40]!r}): wrap it in <p>")
        if re.search(r"(^|[\s(])@[A-Za-zÀ-ÿ]", data):
            self.mention_seen = True
        self.placeholders += re.findall(r"\[[^\]\n]{1,120}\]", data)

    def _check_tag(self, tag, attrs):
        a = dict(attrs)
        if tag in BLOCKED_TAGS:
            self.add("error", f"<{tag}> is not allowed in a Teams message")
            return
        if tag not in SAFE_TAGS:
            hint = TAG_HINTS.get(tag, "not in the Teams-safe subset; Teams drops the tag and keeps its text")
            self.add("warn", f"<{tag}>: {hint}")
        if tag == "h1":
            self.h1_count += 1
        if tag in ("ul", "ol") and sum(t in ("ul", "ol") for t in self.stack) >= 2:
            self.add("warn", "list nested deeper than 3 levels; Teams readers lose the thread")
        if tag == "table" and "table" in self.stack:
            self.add("warn", "nested table; Teams does not render tables inside tables")

        for name, value in attrs:
            n = name.lower()
            if n.startswith("on"):
                self.add("error", f"<{tag}> has an event handler ({n}); remove it")
            elif n == "href":
                if re.match(r"\s*(javascript|data|vbscript):", value or "", re.I):
                    self.add("error", f"<a href> uses a script/data URL; use https://")
                elif re.fullmatch(r"\s*\[[^\[\]]{1,120}\]\s*", value or ""):
                    self.placeholders.append(value.strip())
                elif not re.match(r"\s*(https?:|mailto:|tel:|msteams:)", value or "", re.I):
                    self.add("warn", f"link {value!r} is not absolute; Teams needs a full https:// URL")
            elif n == "src":
                if not re.match(r"\s*(https:|data:image/(png|jpe?g|gif|webp);base64,)", value or "", re.I):
                    self.add("error", f"<img src> must be https: or a base64 PNG/JPEG/GIF/WebP data URL")
            elif n == "data-part":
                if value not in PARTS:
                    self.add("warn", f"data-part={value!r} is not one of {sorted(PARTS)}")
            elif n in ("class", "id") or n.startswith("data-"):
                self.add("info", f"<{tag} {n}> is ignored by Teams; only inline styles survive")
            elif n not in OK_ATTRS:
                self.add("info", f"<{tag} {n}> is ignored by Teams")
        if tag == "a" and not a.get("href"):
            self.add("warn", "<a> without href")

        props = parse_style(a.get("style"))
        dropped = [p for p in props if p not in SAFE_STYLE]
        if dropped:
            hint = " (custom fonts never survive)" if "font-family" in dropped else ""
            self.add("warn", f"<{tag}> style {', '.join(dropped)} will be dropped by Teams{hint}")
        fg_raw, bg_raw = props.get("color"), props.get("background-color")
        fg, bg = parse_color(fg_raw), parse_color(bg_raw)
        if bg and not fg:
            self.add("warn", f"<{tag}> has background-color {bg_raw} but no text color; add color:#1A1A1A "
                             "on the same element or the text turns white-on-highlight in dark mode")
        if fg and bg:
            c = contrast(fg, bg)
            if c < 4.5:
                self.add("warn", f"<{tag}> {fg_raw} on {bg_raw} has contrast {c:.1f}; aim for 4.5 or more")
        if fg and not bg:
            cl, cd = contrast(fg, LIGHT_BG), contrast(fg, DARK_BG)
            if min(cl, cd) < 3:
                where = "light" if cl < 3 else "dark"
                self.add("warn", f"<{tag}> color {fg_raw} reads poorly in {where} mode (contrast {cl:.1f} light / "
                                 f"{cd:.1f} dark; need 3+). Use the dual-mode palette")
        if fg_raw and not fg:
            self.add("info", f"<{tag}> color {fg_raw!r} not checked (use hex)")
        fs = props.get("font-size")
        if fs:
            m = re.fullmatch(r"([\d.]+)px", fs)
            if not m:
                self.add("info", f"<{tag}> font-size {fs!r}: use px values")
            elif not 11 <= float(m.group(1)) <= 24:
                self.add("warn", f"<{tag}> font-size {fs} is outside 11-24px; use a heading for big text")


def lint(body):
    p = Linter()
    p.feed(body)
    p.close()
    issues = p.issues
    if p.h1_count > 1:
        issues.append(("info", 0, f"{p.h1_count} <h1> headings; one is enough, use <h2>/<h3> below it"))
    size = len(body.encode("utf-8"))
    if size > SIZE_WARN_BYTES:
        issues.append(("warn", 0, f"message is {size/1024:.1f} KB; Teams posts cap near 100 KB (stay under 80 KB)"))
    for code in re.findall(r"<pre[^>]*>(.*?)</pre>", body, re.S | re.I):
        if "[" in re.sub(r"<[^>]+>", "", code) and re.search(r"\[[^\]\n]{1,60}\]", code):
            issues.append(("warn", 0, "a snippet contains [brackets]; snippets are not turned into fields, so put the fact in the snippet or move it out"))
    if p.placeholders:
        shown = ", ".join(p.placeholders[:4]) + (" ..." if len(p.placeholders) > 4 else "")
        issues.append(("info", 0, f"{len(p.placeholders)} placeholder(s) become fields in the page panel: {shown}; mention them to the user"))
    if p.mention_seen:
        issues.append(("info", 0, "contains @name text; mentions are not live after a paste, retype them in Teams"))
    return issues


# ---------------------------------------------------------------- labels
LABELS = {
    "en": {
        "kicker": "Teams message", "skill_desc": "Writes richly formatted Teams messages and copies them ready to paste.", "copy": "Copy for Teams", "copied_short": "Copied",
        "copied": "Copied. In Teams, click the message box and press Ctrl+V.",
        "manual": "Your browser blocked the button. The message is now selected, so press Ctrl+C.",
        "edit": "Edit", "done": "Done",
        "preview_hint": "Preview", "preview_label": "Message preview",
        "editing": "Editing. Your changes are included when you copy.",
        "size_title": "A Teams post holds about 100 KB", "size_fmt": "{kb} KB of 100 KB",
        "compose": "Type a message", "how": "How to send it",
        "step1": "Select <b>Copy for Teams</b>.",
        "step2": "In Teams, click the message box of the chat or channel.",
        "step3": "Press <kbd>Ctrl</kbd>+<kbd>V</kbd> (Mac: <kbd>⌘</kbd>+<kbd>V</kbd>), check it, and send.",
        "note_placeholders": "Replace the [text in brackets] before you send.",
        "fill_title": "Fill in the blanks", "fill_hint": "Type each value once. Every place it appears in the message updates.",
        "fill_left": "{n} left", "fill_choose": "Choose…", "img_hint": "Paste, drop or choose an image", "img_replace": "Replace", "img_not_image": "That file is not an image.", "tb_image": "Insert image (you can also paste or drop one)", "fill_done": "All set", "fill_link": "Link",
        "fill_warn": "{n} blank(s) still empty. Fill them, or select Copy again to copy as is.",
        "note_mentions": "@mentions are not kept when you paste. In Teams, type @ and pick the person again.",
        "tb_label": "Formatting", "tb_bold": "Bold", "tb_italic": "Italic", "tb_underline": "Underline", "tb_strike": "Strikethrough",
        "tb_color": "Text color", "tb_color_reset": "Clear formatting", "tb_highlight": "Highlight", "tb_bullets": "Bulleted list",
        "tb_numbers": "Numbered list", "tb_quote": "Quote", "tb_hr": "Divider", "tb_link": "Link", "tb_link_prompt": "Link address", "tb_link_add": "Add link",
        "tb_emoji": "Emoji", "tb_undo": "Undo", "tb_redo": "Redo",
        "emoji_groups": [["Status", "✅ ⏳ ⚠️ 🚫 ❌ 🟢 🟡 🔴 ❓ ❗ 💡 🔄"], ["Time and place", "📅 🗓️ 🕘 ⏰ 📍 🌎 🏢 🏠"],
                         ["Actions", "👉 📌 📎 🔗 📝 ✏️ 📣 📢 🔍 📊 📈 🛠️"], ["People", "👋 🙌 👏 🙏 👍 🤝 💪 🎯"],
                         ["Celebration", "🎉 🥳 🏆 ⭐ 🚀 🔥 ✨ 💯"], ["Objects", "💬 📞 📧 💻 📱 📄 📁 🔒"]],
        "skill_tag": "Formatted Teams messages, ready to paste.", "tab_use": "Use the skill", "tab_howto": "How To", "tab_about": "About",
        "data_title": "Data", "data_empty": "Nothing to fill in. This message has no blanks.",
        "config_title": "Settings", "config_built": "Written for", "config_show": "Show in the message",
        "recipe_title": "Saves a small file with this message and its settings. Give it to Claude next time to get one written the same way.",
        "download_title": "Downloads this page with your changes and filled-in data, so you can open it again later.",
        "copy_title": "Copies the message with its formatting. Then click the Teams message box and press Ctrl+V.",
        "edit_title": "Edit the text right in the preview. Your changes are included when you copy.",
        "opts_title": "Message options", "opt_emoji": "Emoji", "opt_header": "Header",
        "opt_cta": "Call to action", "opt_signoff": "Sign-off",
        "save_title": "Save", "save_hint": "Keep this page with your changes, or save a recipe so Claude writes the next one the same way.",
        "btn_download": "Download", "btn_recipe": "Save recipe",
        "done_title": "Copied!", "done_body": "Now paste it in Teams.",
        "downloaded": "Saved. Open the downloaded page to keep working.", "recipe_saved": "Recipe saved. Give it to Claude next time.",
    },
    "es": {
        "kicker": "Mensaje para Teams", "skill_desc": "Escribe mensajes de Teams con formato y los copia listos para pegar.", "copy": "Copiar para Teams", "copied_short": "Copiado",
        "copied": "Copiado. En Teams, haz clic en el cuadro de mensaje y presiona Ctrl+V.",
        "manual": "Tu navegador bloqueó el botón. El mensaje quedó seleccionado: presiona Ctrl+C.",
        "edit": "Editar", "done": "Listo",
        "preview_hint": "Vista previa", "preview_label": "Vista previa del mensaje",
        "editing": "Editando. Tus cambios se incluyen al copiar.",
        "size_title": "Un mensaje de Teams admite unos 100 KB", "size_fmt": "{kb} KB de 100 KB",
        "compose": "Escribe un mensaje", "how": "Cómo enviarlo",
        "step1": "Haz clic en <b>Copiar para Teams</b>.",
        "step2": "En Teams, haz clic en el cuadro de mensaje del chat o canal.",
        "step3": "Presiona <kbd>Ctrl</kbd>+<kbd>V</kbd> (Mac: <kbd>⌘</kbd>+<kbd>V</kbd>), revisa y envía.",
        "note_placeholders": "Reemplaza el [texto entre corchetes] antes de enviar.",
        "fill_title": "Completa los datos", "fill_hint": "Escribe cada dato una vez. Se actualiza en todos los lugares del mensaje.",
        "fill_left": "faltan {n}", "fill_choose": "Elige…", "img_hint": "Pega, arrastra o elige una imagen", "img_replace": "Cambiar", "img_not_image": "Ese archivo no es una imagen.", "tb_image": "Insertar imagen (también puedes pegarla o arrastrarla)", "fill_done": "Todo listo", "fill_link": "Enlace",
        "fill_warn": "Faltan {n} dato(s). Complétalos, o haz clic otra vez en Copiar para copiar así.",
        "note_mentions": "Las @menciones no se conservan al pegar. En Teams escribe @ y elige a la persona otra vez.",
        "tb_label": "Formato", "tb_bold": "Negritas", "tb_italic": "Itálicas", "tb_underline": "Subrayado", "tb_strike": "Tachado",
        "tb_color": "Color de texto", "tb_color_reset": "Quitar formato", "tb_highlight": "Resaltar", "tb_bullets": "Lista con viñetas",
        "tb_numbers": "Lista numerada", "tb_quote": "Cita", "tb_hr": "Separador", "tb_link": "Enlace", "tb_link_prompt": "Dirección del enlace", "tb_link_add": "Agregar enlace",
        "tb_emoji": "Emoji", "tb_undo": "Deshacer", "tb_redo": "Rehacer",
        "emoji_groups": [["Estatus", "✅ ⏳ ⚠️ 🚫 ❌ 🟢 🟡 🔴 ❓ ❗ 💡 🔄"], ["Fecha y lugar", "📅 🗓️ 🕘 ⏰ 📍 🌎 🏢 🏠"],
                         ["Acciones", "👉 📌 📎 🔗 📝 ✏️ 📣 📢 🔍 📊 📈 🛠️"], ["Personas", "👋 🙌 👏 🙏 👍 🤝 💪 🎯"],
                         ["Celebración", "🎉 🥳 🏆 ⭐ 🚀 🔥 ✨ 💯"], ["Objetos", "💬 📞 📧 💻 📱 📄 📁 🔒"]],
        "skill_tag": "Mensajes de Teams con formato, listos para pegar.", "tab_use": "Usar la skill", "tab_howto": "Cómo se usa", "tab_about": "Acerca de",
        "data_title": "Datos", "data_empty": "No hay nada que completar. Este mensaje no tiene datos pendientes.",
        "config_title": "Configuración", "config_built": "Escrito para", "config_show": "Mostrar en el mensaje",
        "recipe_title": "Guarda un archivo pequeño con este mensaje y su configuración. Dáselo a Claude la próxima vez para que escriba otro igual.",
        "download_title": "Descarga esta página con tus cambios y datos capturados, para abrirla otra vez después.",
        "copy_title": "Copia el mensaje con su formato. Después haz clic en el cuadro de mensaje de Teams y presiona Ctrl+V.",
        "edit_title": "Edita el texto directamente en la vista previa. Tus cambios se incluyen al copiar.",
        "opts_title": "Opciones del mensaje", "opt_emoji": "Emojis", "opt_header": "Encabezado",
        "opt_cta": "Llamada a la acción", "opt_signoff": "Cierre",
        "save_title": "Guardar", "save_hint": "Guarda esta página con tus cambios, o guarda una receta para que Claude escriba el siguiente igual.",
        "btn_download": "Descargar", "btn_recipe": "Guardar receta",
        "done_title": "¡Copiado!", "done_body": "Ahora pégalo en Teams.",
        "downloaded": "Guardado. Abre la página descargada para seguir trabajando.", "recipe_saved": "Receta guardada. Dásela a Claude la próxima vez.",
    },
}
HTML_LABELS = {"step1", "step2", "step3"}   # trusted markup from the table above

# Message settings chosen in the skill (Phase A). Canonical values -> display text.
SETTINGS_SCHEMA = {
    "channel": ["chat", "group_chat", "meeting_chat", "channel"],
    "tone": ["formal", "friendly", "festive", "urgent"],
    "emoji": ["none", "few", "many"],
    "header": ["none", "bold_line", "heading"],
    "cta": ["none", "reply", "link", "decide", "attend"],
    "signoff": ["none", "name", "team"],
    "length": ["short", "standard", "detailed"],
}
SETTINGS_SHOWN = ["channel", "tone", "emoji", "length"]
SETTINGS_TEXT = {
    "en": {"_keys": {"channel": "Sent in", "tone": "Tone", "emoji": "Emoji", "length": "Length"},
           "chat": "One-to-one chat", "group_chat": "Group chat", "meeting_chat": "Meeting chat", "channel": "Channel post",
           "formal": "Formal", "friendly": "Friendly", "festive": "Festive", "urgent": "Urgent",
           "none": "None", "few": "A few", "many": "Many",
           "short": "Short", "standard": "Standard", "detailed": "Detailed"},
    "es": {"_keys": {"channel": "Para", "tone": "Tono", "emoji": "Emojis", "length": "Largo"},
           "chat": "Chat 1:1", "group_chat": "Chat grupal", "meeting_chat": "Chat de reunión", "channel": "Publicación en canal",
           "formal": "Formal", "friendly": "Amable", "festive": "Festivo", "urgent": "Urgente",
           "none": "Ninguno", "few": "Pocos", "many": "Muchos",
           "short": "Corto", "standard": "Normal", "detailed": "Detallado"},
}
PARTS = {"header", "cta", "signoff"}


def check_settings(settings, body=""):
    problems = []
    for part in sorted(PARTS):
        marked = f'data-part="{part}"' in body
        if settings.get(part) == "none" and marked:
            problems.append(f"settings: {part} is 'none' but the message has data-part=\"{part}\"")
        if settings.get(part) not in (None, "none") and not marked:
            problems.append(f"settings: {part} is {settings[part]!r} but no element has data-part=\"{part}\"")
    for k, v in settings.items():
        if k in SETTINGS_SCHEMA and v not in SETTINGS_SCHEMA[k]:
            problems.append(f"settings: {k}={v!r} is not one of {SETTINGS_SCHEMA[k]}")
    return problems


def built_for_html(settings, lang):
    t = SETTINGS_TEXT[lang]
    rows = [(t["_keys"][k], t.get(settings[k], str(settings[k]))) for k in SETTINGS_SHOWN if settings.get(k)]
    if not rows:
        return ""
    return '<dl class="built">' + "".join(f"<dt>{html.escape(a)}</dt><dd>{html.escape(b)}</dd>" for a, b in rows) + "</dl>"


def initials(name):
    parts = [w for w in re.split(r"\s+", name.strip()) if w]
    if not parts:
        return "?"
    letters = parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")
    return letters.upper()


def first_heading(body):
    """Page title: first heading, else the header part, else the first bold phrase."""
    for pat in (r"<h[1-3][^>]*>(.*?)</h[1-3]>",
                r"<[a-z0-9]+[^>]*data-part=\"header\"[^>]*>(.*?)</[a-z0-9]+>",
                r"<(?:strong|b)>(.*?)</(?:strong|b)>"):
        m = re.search(pat, body, re.S | re.I)
        if m:
            text = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
            if text:
                return text[:120]
    return None


def build(body, title, sender, lang, settings):
    labels = LABELS[lang]
    tokens = {
        "LANG": lang,
        "SETTINGS_JSON": json.dumps(settings, ensure_ascii=False).replace("</", "<\\/"),
        "BUILT_FOR": built_for_html(settings, lang),
        "TITLE": html.escape(title), "SENDER": html.escape(sender), "INITIALS": html.escape(initials(sender)),
        "LABELS_JSON": json.dumps(labels, ensure_ascii=False).replace("</", "<\\/"),
    }
    for k, v in labels.items():
        if isinstance(v, str):
            tokens["L_" + k.upper()] = v if k in HTML_LABELS else html.escape(v)
    page = TEMPLATE.read_text(encoding="utf-8")

    def sub(m):
        key = m.group(1)
        if key not in tokens:
            raise SystemExit(f"template token {{{{{key}}}}} has no value")
        return tokens[key]

    page = re.sub(r"\{\{([A-Z0-9_]+)\}\}", sub, page)
    for slot in ("<!--MESSAGE-->", "<!--HOWTO-->", "<!--ABOUT-->"):
        if slot not in page:
            raise SystemExit(f"template is missing the {slot} slot")
    def asset(name):   # language version first, English as fallback
        f = ASSETS / f"{name}.{lang}.html"
        return (f if f.exists() else ASSETS / f"{name}.en.html").read_text(encoding="utf-8")
    howto = asset("howto").replace("<!--SHOWCASE-->", asset("showcase").strip(), 1)
    page = page.replace("<!--HOWTO-->", howto, 1).replace("<!--ABOUT-->", asset("about"), 1)
    # Footer repo icon: the official GitHub mark if the user added assets/github-mark.svg, else a code icon.
    mark = ASSETS / "github-mark.svg"
    if mark.exists():
        svg = re.sub(r"<\?xml[^>]*>|<!--.*?-->", "", mark.read_text(encoding="utf-8"), flags=re.S).strip()
        svg = re.sub(r"<svg\b", '<svg class="repo-ico" aria-hidden="true"', svg, count=1)
        svg = re.sub(r"<svg\b[^>]*>", lambda m: re.sub(r'\s(width|height)="[^"]*"', "", m.group(0)), svg, count=1)
        svg = re.sub(r'fill="(#[0-9a-fA-F]{3,6}|white|black)"', 'fill="currentColor"', svg)
    else:
        svg = ('<svg class="code-ico" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" '
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 6l-4 4 4 4M13 6l4 4-4 4M11 4.5l-2 11"/></svg>')
    page = page.replace("<!--REPO_ICON-->", svg, 1)
    return page.replace("<!--MESSAGE-->", body.strip(), 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--body", required=True, help="HTML fragment with the message")
    ap.add_argument("--out", help="output .html page")
    ap.add_argument("--title", help="page title (default: first heading of the message)")
    ap.add_argument("--sender", default=None, help="name shown in the Teams preview")
    ap.add_argument("--lang", choices=sorted(LABELS), default="en", help="page UI language")
    ap.add_argument("--settings", help="JSON file with the message settings chosen in the skill")
    ap.add_argument("--check", action="store_true", help="lint only")
    ap.add_argument("--force", action="store_true", help="build even with lint errors")
    args = ap.parse_args()

    body = Path(args.body).read_text(encoding="utf-8")
    settings = json.loads(Path(args.settings).read_text(encoding="utf-8")) if args.settings else {}
    issues = lint(body) + [("warn", 0, t) for t in check_settings(settings, body)]
    order = {"error": 0, "warn": 1, "info": 2}
    for level, line, text in sorted(issues, key=lambda i: (order[i[0]], i[1])):
        where = f"line {line}" if line else "message"
        print(f"{level.upper():5}  {where:>8}  {text}")
    errors = sum(1 for i in issues if i[0] == "error")
    warns = sum(1 for i in issues if i[0] == "warn")
    print(f"Lint: {errors} error(s), {warns} warning(s), {len(issues) - errors - warns} note(s)")

    if args.check:
        return 1 if errors else 0
    if not args.out:
        ap.error("--out is required unless --check is used")
    if errors and not args.force:
        print("Not built: fix the errors or pass --force.")
        return 1
    title = args.title or first_heading(body) or LABELS[args.lang]["kicker"]
    sender = args.sender or ("Tú" if args.lang == "es" else "You")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(body, title, sender, args.lang, settings), encoding="utf-8")
    print(f"Built {out} ({out.stat().st_size/1024:.1f} KB, lang={args.lang})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
