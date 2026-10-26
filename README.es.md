# TapKit

[English](README.md) · **Español**

**Skills de IA que te dan resultados al instante.**

TapKit es una colección de skills para Claude. Pides algo con tus palabras y la skill te entrega un resultado terminado: una página que abres, revisas, ajustas y usas de inmediato. Todas las skills de TapKit empiezan con `tap-`.

| Skill | Qué te da | Versión |
|---|---|---|
| [tap-teams-message](skills/tap-teams-message) | Mensajes de Microsoft Teams con formato, listos para pegar | 1.0.0 |

Vienen más skills.

---

## tap-teams-message

Pídele a Claude un mensaje de Teams, por ejemplo *"resumen de la llamada de hoy para el chat del equipo"*. Claude lo escribe con formato real (emojis, negritas, colores, listas, tablas, etiquetas de estatus, texto para copiar) y arma una página donde puedes:

- **Verlo** como se verá en Teams.
- **Completar los datos** con el control adecuado: calendario, hora, números, opciones, imágenes.
- **Mostrar u ocultar partes**: emojis, encabezado, llamada a la acción, cierre.
- **Editar** el texto con una pequeña barra de formato.
- **Copiar para Teams** y pegarlo en cualquier chat o canal.
- **Descargar** la página con tus cambios, o **guardar una receta** para que Claude escriba el siguiente igual.

La página funciona en español y en inglés, según el idioma en que le pidas el mensaje a Claude.

![Página de tap-teams-message](docs/images/tap-teams-message.png)

---

## Instalación

### Claude (web y app de escritorio)

1. Descarga **[tap-teams-message.zip](https://github.com/aderegil/tapkit/releases/latest/download/tap-teams-message.zip)** del release más reciente.
2. Revisa que la ejecución de código esté activa: **Settings > Capabilities > Code execution and file creation**. En planes Team y Enterprise la activa un administrador para toda la organización.
3. Ve a **Customize > Skills**, haz clic en **+**, luego **Create skill > Upload a skill**, y elige el zip.
4. Activa la skill.

Los menús pueden aparecer traducidos en tu idioma. Después, pide un mensaje de Teams en cualquier chat: Claude usa la skill por su cuenta.

### Claude Code

Agrega TapKit como marketplace de plugins e instala las skills que quieras:

```
/plugin marketplace add aderegil/tapkit
/plugin install tap-teams-message@tapkit
```

Para recibir actualizaciones: `/plugin marketplace update tapkit`.

### Copia manual (Claude Code y otras herramientas que leen Agent Skills)

Copia la carpeta `skills/tap-teams-message` a tu carpeta de skills, por ejemplo `~/.claude/skills/tap-teams-message` en Claude Code.

---

## Requisitos

- Python 3 donde Claude ejecuta la skill. El script usa solo la biblioteca estándar.
- Para pegar: Microsoft Teams (escritorio, web o móvil) y un navegador actual para abrir la página.

La información para mantener el repo (estructura, agregar skills, releases) está en el [README en inglés](README.md#repository-layout).

---

Hecho por Alfredo De Regil. Licencia [CC BY-ND 4.0](LICENSE): puedes usarla y compartirla sin cambios, dando crédito; no se pueden compartir versiones modificadas.
