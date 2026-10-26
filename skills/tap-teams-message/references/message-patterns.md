# Message patterns

Skeletons for common Teams messages, chats first. Replace the bracketed parts, drop lines that do not apply, and keep the order: the point first, details next, the action last. Keep the `data-part` markers so the page can switch those parts on or off. Write chip labels and all text in the message language (ON TRACK = EN TIEMPO, AT RISK = EN RIESGO, BLOCKED = BLOQUEADO, SCHEDULED = PROGRAMADO, INCIDENT = INCIDENTE, RESOLVED = RESUELTO). Use a link only when a real URL exists.

Each pattern lists its usual settings. They are starting points; the user's settings win.

---

## Chat patterns

### meeting_recap: recap in the chat of a meeting or call
Settings: `meeting_chat`, `friendly`, `few`, `bold_line`, `reply`, `name`, `standard`.

```html
<p data-part="header"><strong>📝 [Meeting name] recap, [weekday, date]</strong></p>
<p>Thanks for joining. Here is what we agreed:</p>
<ul>
  <li>✅ <strong>[Decision 1]</strong></li>
  <li>✅ <strong>[Decision 2]</strong></li>
</ul>
<table>
  <thead><tr><th>Action</th><th>Owner</th><th>Due</th></tr></thead>
  <tbody>
    <tr><td>[Action]</td><td>[Owner]</td><td>[Due date]</td></tr>
  </tbody>
</table>
<p>📅 Next meeting: <strong>[date, time, time zone]</strong></p>
<p data-part="cta">👉 [Main action, or "Reply here if I missed anything"]</p>
<p data-part="signoff">[Name]</p>
```

Add a snippet when the meeting produced something people will copy (a prompt, a command, an ID).

### follow_up: after a conversation or a request
Settings: `chat` or `group_chat`, `friendly`, `few`, `none`, `reply`, `none`, `short`.

```html
<p>Hi [name], following up on [topic].</p>
<p>[One or two lines with the status or the question.]</p>
<p data-part="cta">👉 Could you [specific ask] by <strong>[date]</strong>?</p>
```

### quick_update: short update to a group chat
Settings: `group_chat`, `friendly`, `few`, `bold_line`, `none`, `none`, `short`.

```html
<p data-part="header"><strong>[Emoji] [Update in one line]</strong></p>
<ul>
  <li>✅ [Done]</li>
  <li>⏳ [In progress]</li>
  <li>⚠️ [Risk or blocker]</li>
</ul>
```

### reminder: something people must do
Settings: `group_chat`, `friendly` or `urgent`, `few`, `bold_line`, `link` or `decide`, `none`, `short`.

```html
<p data-part="header"><strong>⏰ Reminder: [action] by [deadline]</strong></p>
<p>[Why it matters, one line.]</p>
<p data-part="cta">👉 <a href="[link]">[Do it now]</a></p>
```

### share_snippet: share text people will copy
Settings: `chat` or `group_chat`, `friendly`, `few`, `none`, `none`, `none`, `short`.

```html
<p>[What this is and when to use it.]</p>
<pre><code>[Text to copy]</code></pre>
<p>Triple-click the box to copy it.</p>
```

### thanks: thank a person or a group
Settings: `chat` or `group_chat`, `festive`, `many`, `none`, `none`, `name`, `short`.

```html
<p>🎉 Thank you, [name]! [What they did] made [concrete impact] possible. 🙌</p>
<p data-part="signoff">[Name]</p>
```

Remind the user to retype the @mention in Teams so the person is notified.

---

## Channel patterns

Channel posts can carry more structure. Remind the user to add a subject line in Teams.

### announcement: launch, change, new policy
Settings: `channel`, `friendly`, `few`, `heading`, `link`, `team`, `standard`.

```html
<h2 data-part="header">🚀 [What is new, in one line]</h2>
<p>[Who it affects] [what changes] starting <strong>[date]</strong>.</p>
<h3>✨ What changes</h3>
<ul>
  <li><strong>[Benefit 1]</strong>: [one line]</li>
  <li><strong>[Benefit 2]</strong>: [one line]</li>
</ul>
<blockquote><p>⚠️ [The one thing people must not miss.]</p></blockquote>
<p data-part="cta">👉 <a href="[link]">[Action label]</a></p>
<p data-part="signoff">[Team signature]</p>
```

### status_update: project status
Settings: `channel` or `group_chat`, `formal` or `friendly`, `few`, `heading`, `decide`, `none`, `standard`.

```html
<h2 data-part="header">📊 [Project]: [period] status</h2>
<p><span style="background-color:#107C10;color:#FFFFFF;font-weight:600">&nbsp;ON TRACK&nbsp;</span> [One-line summary.]</p>
<table>
  <thead><tr><th>Workstream</th><th>Status</th><th>Next step</th></tr></thead>
  <tbody>
    <tr><td>[Name]</td><td>✅ Done</td><td>[Next]</td></tr>
    <tr><td>[Name]</td><td>⏳ In progress</td><td>[Next]</td></tr>
  </tbody>
</table>
<p data-part="cta">👉 <strong>Need from you</strong>: [decision or input] by <strong>[date]</strong>.</p>
```

Chips: ON TRACK `#107C10`, OFF TRACK `#C4314B` (both with white text), AT RISK `background-color:#FFF100;color:#1A1A1A`.

### event_invitation
Settings: `channel` or `group_chat`, `friendly`, `few`, `heading`, `attend`, `none`, `standard`.

```html
<h2 data-part="header">🎟️ [Event name]</h2>
<p>[One sentence on why to come.]</p>
<p>📅 <strong>[Day, date]</strong><br>🕘 <strong>[Start]–[End] [time zone]</strong><br>📍 [Room or Teams meeting]</p>
<h3>🗒️ Agenda</h3>
<ol>
  <li>[Topic] ([owner])</li>
  <li>[Topic] ([owner])</li>
</ol>
<p data-part="cta">👉 <a href="[link]">Save your spot</a></p>
```

### maintenance: planned downtime
Settings: `channel` or `group_chat`, `formal`, `few`, `heading`, `none`, `team`, `standard`.

```html
<h2 data-part="header">🛠️ [System] maintenance: [day, date], [start]–[end]</h2>
<p><span style="background-color:#FFF100;color:#1A1A1A;font-weight:600">&nbsp;SCHEDULED&nbsp;</span> [System] <strong>will not be available</strong> during this window.</p>
<p>📅 <strong>[Day, date]</strong><br>🕘 <strong>[Start]–[End] [time zone]</strong></p>
<blockquote><p>⚠️ [Who is affected and what they cannot do.]</p></blockquote>
<p data-part="cta">👉 <strong>[What to do before: save work, finish uploads…]</strong></p>
<p>📞 Questions: <strong>[help desk, extension or link]</strong>.</p>
<p data-part="signoff">[Thanks line]<br><strong>[Team signature]</strong></p>
```

When the work is done, a short follow-up with a green RESOLVED chip closes the loop.

### incident: unplanned outage
Settings: `channel` or `group_chat`, `urgent`, `few`, `bold_line`, `none`, `team`, `short`.

```html
<p data-part="header"><span style="background-color:#C4314B;color:#FFFFFF;font-weight:600">&nbsp;INCIDENT&nbsp;</span> <strong>[Service] is [down / degraded]</strong></p>
<p>🕘 Started <strong>[time, time zone]</strong>. Impact: [who and what].</p>
<p>🩹 <strong>Workaround</strong>: [steps or "none yet"]</p>
<p>⏭️ Next update by <strong>[time]</strong>.</p>
```

For the resolved follow-up, use a `RESOLVED` chip on `#107C10` and add the root cause in one line.

### weekly_digest: newsletter
Settings: `channel`, `friendly`, `few`, `heading`, `link`, `team`, `detailed`.

```html
<h2 data-part="header">📰 [Team] weekly: [date]</h2>
<h3>🏆 Highlights</h3>
<ul><li>[Item]</li><li>[Item]</li></ul>
<h3>📅 Coming up</h3>
<table>
  <thead><tr><th>Date</th><th>What</th><th>Owner</th></tr></thead>
  <tbody><tr><td>[Date]</td><td>[What]</td><td>[Owner]</td></tr></tbody>
</table>
<h3>🔗 Worth reading</h3>
<ul><li><a href="[link]">[Title]</a>: [why]</li></ul>
<p data-part="signoff">[Team signature]</p>
```
