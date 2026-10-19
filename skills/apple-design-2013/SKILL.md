---
name: apple-design-2013
description: Apple's OS X Human Interface Guidelines as of 2013 (OS X 10.9 Mavericks, Aqua era), translated for the web. Use when building or reviewing desktop-style UI that should look and behave like a classic Mac app — windows, toolbars, source lists, sheets, popovers, panels, alerts, push buttons, menus, Lucida Grande typography, control sizing, ellipsis/capitalization rules, keyboard-first behavior, forgiveness/undo, and subtle, purposeful animation.
---

# Apple Design — OS X HIG 2013 (Aqua)

## Initial Response

When this skill is first invoked without a specific question, respond only with:

> I'm ready to help you build classic Mac-style (OS X Mavericks / Aqua) interfaces on the web. My knowledge comes from Apple's 2013 *OS X Human Interface Guidelines*, translated for the web.

Do not provide any other information until the user asks a question.

---

Source: *OS X Human Interface Guidelines* (Apple, revision 2013-10-22, OS X 10.9). The HIG describes native AppKit apps; it contains no CSS and almost no animation numbers. Everything below that is web code is a **translation**. Values not stated in the HIG itself are marked **[AppKit default]** or **[convention]** — treat them as reasonable starting points, not Apple rules.

The through-line of the 2013 HIG: **the UI is subordinate to the user's content.** Use the standard Aqua elements exactly as users already know them, make every command findable in a menu, make every action reversible, give immediate feedback, and animate only when the animation explains something.

## 1. The fundamental principles (HIG ch. "Philosophy of UI Design")

Reason with these names — they are the 2013 vocabulary:

1. **Metaphors.** Use concrete, familiar real-world ideas (folders, Trash, albums). A metaphor suggests use but must not limit it — the Trash holds more than a real wastebasket.
2. **Mental model.** Discover how users already think about the task and mirror it in window layout, menu order, toolbar contents and panels. Supporting traits: **familiarity, simplicity, availability** (don't bury key features in submenus or contextual menus only), **discoverability** (if it's clickable, it must look clickable).
3. **Explicit and implied actions.** Explicit = menu commands that name the action and dim when invalid. Implied = drag-and-drop, where the objects themselves convey the result. Support both where the mental model suggests it.
4. **Direct manipulation.** The object stays visible while acted on, and the effect is immediately visible. Don't force users through controls when dragging the thing itself would do.
5. **See and point.** Noun-then-verb: select an object, then choose the action (from a menu), or drag the object onto another object that carries the verb.
6. **User control.** The user, not the computer, initiates actions. Warn before destructive actions, but let the user proceed.
7. **Feedback and communication.** Acknowledge every input. Explain failures and what to do instead. Use progress indicators for long operations with approximate estimates ("About a minute remaining", "Copying 30 of 850 files").
8. **Consistency.** With OS X standards, within the app, with earlier versions, with user expectations.
9. **WYSIWYG.** No significant difference between screen and output (print, export, publish).
10. **Forgiveness.** Most actions easily reversible (Undo, Revert). Frequent alerts mean the design is flawed.
11. **Perceived stability.** A finite, predictable set of objects and actions. **Dim unavailable commands instead of hiding them.** Preserve window sizes/positions and other user-set state.
12. **Aesthetic integrity.** Pleasant for long sessions. Keep graphics simple and meaningful; one font family and one control size per window; never change the meaning of standard elements (checkboxes = independent choices, radio buttons = mutually exclusive, push buttons = immediate commands, never tabs or menus).

## 2. User experience rules (HIG ch. "User Experience Guidelines")

- **Don't burden users with app management.** Restore previous state (open windows, scroll positions, selections). Save continuously (Auto Save). Don't expose file formats, raw paths or filename extensions unless the user asked for them.
- **Solutions, not features.** Avoid feature cascade; heed the 80/20 rule — design for the handful of features most people use, keep power features one level deeper.
- **Embrace modelessness.** Modes only for small, self-contained tasks. If you have modes: show the current one clearly (pointer, segmented control, popover) and make it trivial to leave. Save work when users leave a mode unexpectedly.
- **Progressive disclosure.** Common choices first; advanced options behind a disclosure triangle/button.
- **Menus mirror the object hierarchy.** High-level objects on the left (in LTR locales), specific ones to the right.
- **Don't use dynamic (Option-key) menu items just to shorten menus.** List important commands openly.
- **Be responsive.** Acknowledge instantly (buttons highlight on press, pointer changes over controls). Show partial results early. Remember: after ~2 s without response the system shows the spinning wait cursor and users assume a hang.
- **Offer alternate ways.** Every command in the menu bar; keyboard-only operation; accessibility (VoiceOver). Toolbar and contextual menus may be hidden, so they are never the *only* path.
- **Use standard elements correctly.** Don't give built-in elements new behaviors, don't recreate a built-in element as a custom one, don't import elements from other platforms. A custom element must look clearly custom and earn its place.
- **Be productive immediately.** No forced setup, intelligent defaults, no restart.
- **Make exploration safe.** Undo everywhere; warn only for *unexpected* irreversible loss (Secure Empty Trash), not for expected loss (moving a file to the Trash).
- **Don't be paternalistic.** Avoid constraining user actions.
- **User input.** Auto-fill only when you're sure it's correct, and mark auto-filled fields. Validate as users type when the rule is simple (digits only). **Don't show "required" markers up front** — mark a missed required field only when the user tries to leave. Password fields: bullets, always start empty.
- **User-centric terminology.** Pointer (not cursor), Start (not launch), Restart (not reboot), Text (not string), Click (not mouse-up event). "Select" a checkbox, not "check".
- **Branding stays subordinate.** Brand through a subtle, consistent design language and a great app icon — not logos in the content area.
- **Keyboard shortcuts.** Never override system-reserved shortcuts; avoid redefining common ones; don't invent a shortcut for every command.

## 3. Animation — subtle, explanatory, rare

The 2013 HIG treats animation as *communication*, never as the experience itself. It gives no curves or durations.

**Animate when:**
- it clarifies a relationship or consequence (window genies into the Dock; sheet unfurls from the title bar; Dock items move aside to show where a drop will land);
- an object changes properties (show the transition, not just start and end);
- an action is too fast to follow (minimize, duplicate);
- the object is a realistic physical thing (a heavy object slows down faster than a light one);
- a window enters/leaves full screen — all parts move together, nothing lags or breaks apart.

**Don't animate:**
- gratuitously or as the focus of the UX;
- everything — most actions are best done quickly with minimal fanfare;
- routine actions on standard controls (button clicks, tab switches).

**Realistic motion over realistic imagery:** rubber-banding at the end of scrollable content is the canonical example.

**Web translation:**

```css
/* [AppKit default] NSAnimationContext's default duration is 0.25 s.
   Use ease-in-out; no overshoot on standard UI. */
:root { --aqua-duration: 250ms; --aqua-ease: cubic-bezier(0.42, 0, 0.58, 1); }

/* Sheet: emerges from the bottom edge of the toolbar/title bar */
.sheet {
  transform-origin: top center;
  animation: sheet-in var(--aqua-duration) var(--aqua-ease);
}
@keyframes sheet-in { from { transform: translateY(-100%); } to { transform: none; } }

/* Buttons: no transition — the pressed state is instant */
.push-button:active { background: var(--aqua-pressed); transition: none; }

@media (prefers-reduced-motion: reduce) {
  .sheet { animation: none; }
}
```

## 4. Windows

**Anatomy:** a *window frame* (title bar + unified toolbar, rarely a bottom bar) with a **light gray gradient**, and a *window body* (content views white, surrounding body light gray). The overall look is "subtle and understated" so content dominates.

- **Every window has a title bar** (even untitled tool panels — users must be able to drag it) and a **close button**.
- **Title bar contains only four things:** title (centered), close/minimize/zoom buttons (top-left), full-screen button (top-right), proxy icon (documents). Nothing else.
- **Titles:** document name (no path, extension only if the user shows extensions); app name for app windows; descriptive noun for panels. Separate multiple parts with a spaced em dash: `Inbox — Work`. New documents: "untitled", "untitled 2", …
- **Main / key / inactive:** only the key window's controls have color; inactive windows have a lighter frame. On the web: dim the frame and desaturate controls when the app/window loses focus.
- **Positioning:** new document windows horizontally centered, top at the menu bar; each further window offset **20 pt right and 20 pt down**. Non-document windows visually centered (space below ≈ 2× space above). Never overlap the Dock; never place a window where it can't be retrieved.
- **Reopen at the size and position the user last set.** A change of ≥ 7 pt counts as a user state; zoom toggles between standard and user state and should not simply fill the screen.
- **Closing:** non-document apps generally quit when the last window closes. Unsaved-change confirmation only for never-saved documents; otherwise save continuously.
- **Click-through:** allowed for harmless toolbar items in inactive windows, never for destructive or irreversible ones (Delete, Send).
- **Scrolling:** scroll bars are transient, translucent overlays and **must not shift content when they appear**. Keep important UI ~10 pt clear of the scroll edge (8 pt for small scroll bars); persistent legacy scroll bars are 15 pt wide. Hint at more content by cutting a row in half at the bottom edge.

```css
:root {
  --frame-top: #e8e8e8;   /* [convention] approximations of the Mavericks frame gradient */
  --frame-bottom: #d1d1d1;
  --frame-inactive: #f6f6f6;
  --body-bg: #ececec;
  --content-bg: #ffffff;
  --hairline: #b1b1b1;
}
.window-frame {
  background: linear-gradient(var(--frame-top), var(--frame-bottom));
  border-bottom: 1px solid var(--hairline);
}
.window:not(:focus-within) .window-frame { background: var(--frame-inactive); }
.scroll-area { overflow: auto; scrollbar-gutter: auto; } /* never reserve layout space for overlay scrollers */
```

## 5. Toolbar

- Contains the **most frequently used** commands; left = highest visibility (in LTR). Group by subsets (document-level left, object-level right).
- **Every toolbar item also exists as a menu command.** The converse is not true.
- **Use window-frame controls only** (round textured buttons, textured segmented controls, textured pop-ups, search field). Never put body controls (Aqua push buttons) in the toolbar, and never put toolbar controls in the window body.
- **No persistent selected state** on toolbar buttons — they trigger actions. Exception: a segmented control showing a view mode.
- Show/hide and Customize Toolbar live in the **View** menu. Users can choose icon + text (default), icon only, text only.
- No app-specific contextual menu on the toolbar (Control-click there is reserved for customization); use an **Action menu** (gear) instead.
- **Icons inside toolbar controls:** ≤ 19×19 px template images — black, solid, sharp outline, straight-on perspective, little internal detail, vector (PDF → on the web: SVG with `fill: currentColor`), visually centered. **Freestanding toolbar icons:** 32×32 (@2x for Retina), may use color judiciously.
- Use system icons only for their documented meaning (the gear means Action menu, not "settings" or "advanced").

## 6. Source lists (sidebars)

- For primary navigation of user-meaningful collections (iTunes playlists, Mail mailboxes) — a file-system abstraction.
- **Blue-tinted background** only for the single, app-wide primary source list; **white** in all other cases (multiple source lists, panels, preferences).
- Max **two levels** of hierarchy; group with uppercase section titles (Devices, Shared, Tags).
- Sidebar icons: 16×16, 18×18, 32×32; black + alpha for detail ("X-ray" look); must survive color inversion when selected.

```css
.source-list { background: #e0e5eb; font-size: 11px; }            /* [convention] Mavericks sidebar tint */
.source-list .section-title { font-weight: bold; color: #707e8c; text-transform: uppercase; font-size: 11px; }
.source-list .item[aria-selected="true"] { background: linear-gradient(#6aa8e8, #3a7fd4); color: #fff; }
```

## 7. Popovers, panels, sheets, dialogs, alerts — choosing the right container

| Need | Use | Not |
| --- | --- | --- |
| Occasional, focused, small task tied to a control | **Popover** | panel, alert |
| Controls that affect the current selection, kept open | **Panel / inspector** | sheet |
| Task that blocks one document until answered | **Sheet** | app-modal dialog |
| Task affecting the whole app or several windows | **App-modal dialog** | sheet |
| Serious problem / risk of unexpected data loss | **Alert** | popover, banner |
| Settings changed rarely | **Preferences window** (Cmd-,) | inline settings in the main window |

**Popovers**
- Arrow points directly at the element that opened it.
- **No close button** — closes on outside click (transient) or on interaction with the source (semi-transient); edits are kept.
- Never nest popovers; never use one as an alert (users *choose* popovers, they never choose alerts).
- Not too big; may resize in place (minimal → expanded); may detach into a panel that looks the same.
- Standard (light) appearance; dark HUD only for immersive, media-centric apps.

**Panels**
- Float above the app's windows, hide when the app is inactive, not listed in the Window menu.
- Close button only (no active minimize). Standard panels use **small** controls.
- **Inspectors** update live with the selection; **Info windows** stay bound to one item.
- **Transparent (HUD) panels** only for media-centric/immersive/dark contexts: dark translucent body, white controls, gray accents, minimal color, small size, simple controls (sliders, steppers — no typing).

**Sheets**
- Attached to the window, emerge from the bottom of the toolbar/title bar. One sheet per window at a time.
- Don't use a sheet when users need to look at or copy from the window to answer it, or to watch live effects (use a panel).
- No sheet on a window without a title bar.

**Dialogs**
- Pre-fill sensible defaults; put the insertion point in the first field; make error text, serial numbers etc. selectable.
- Validate early, but not on every keystroke; prefer disallowing invalid input.
- Apply button only for previewable settings; Apply never dismisses; **Cancel undoes applied changes**.
- **Button order (bottom right):** action button rightmost, Cancel to its left, a third dismiss button (e.g. Don't Save) further left, **≥ 24 pt away** from the safe buttons. Buttons that affect the dialog itself (Show Details) bottom left, after Help.
- **Default button** (blue, pulsing in Aqua; Return/Enter) only if the likely action is harmless. No default button if the likely action destroys data, or if Return is used in the dialog's text fields.
- Esc and Cmd-. always trigger Cancel.

**Alerts**
- Only when absolutely necessary. Not for pure information (use a status indicator), not for common undoable actions.
- Anatomy: **app icon** left; **message** in emphasized (bold) system font — short, specific; **informative text** in small system font — consequences and a way out (never leave it out); buttons bottom right.
- Phrase as a question only when users may not realize the consequence ("Are you sure you want to clear history?") — sparingly.
- **Avoid "OK"**: name the button for the action (Erase, Convert, Delete).
- Caution icon (badged with the app icon) only for inadvertent, unexpected data destruction.
- Document-scoped alert = sheet; app-scoped alert = app-modal.

**Preferences window**
- Opened via App menu → Preferences… (Cmd-,). Pane-switcher toolbar with freestanding icons, selected pane stays highlighted, toolbar not customizable or hideable.
- Not resizable, no active minimize/zoom. Changes take effect immediately (no OK/Apply).

```css
/* Dialog footer: action right, Cancel left of it, destructive third button pushed away */
.dialog-buttons { display: flex; gap: 12px; justify-content: flex-end; }   /* 12 px: [convention] IB button spacing */
.dialog-buttons .destructive { margin-right: auto; }                         /* well beyond the 24 pt minimum */
.dialog-buttons .local { order: -1; }                                         /* e.g. Show Details, far left */
```

## 8. Controls

- **Prefer standard controls.** Many come in three sizes — **regular, small, mini**. Regular in windows; small in panels/tight panes; **never mix sizes in one window**. Don't resize controls vertically.
- Use the font that matches the control size (regular → 13 pt, small → 11 pt, mini → 9 pt). Space controls evenly (Interface Builder guides).
- **Push buttons:** window body only; text only (no icons); **verb or verb phrase** in title case ("Change Password", "Choose Picture…"); no "Now"; **ellipsis if a window/dialog follows**; never as state toggle, label or menu trigger. Only the default button has color; when another button is pressed, it takes the color temporarily. Keep destructive buttons physically away from safe ones.
- **Checkbox:** two opposite states, or independent multiple choices. **Radio buttons:** mutually exclusive, static set (never changes with context).
- **Pop-up menu:** up to ~12 mutually exclusive choices users don't need to see all the time.
- **Segmented control:** related choices/modes; system icons preferred; custom icons 17×15 (regular), 14×13 (small), 12×11 (mini).
- **Progress:** determinate bar when duration is known (disappears when full, must not stall at 90 %); indeterminate bar when unknown; spinning (asynchronous) indicator only where space is tight. Start indeterminate if it may become determinate.
- **Search field:** standard rounded field with magnifier and clear button; in the toolbar right end.
- **Disclosure triangle** reveals details; **disclosure button** expands choices of a related pop-up.
- **Tab view:** inset with window-body margin on all sides; **group box** without a colon in its title.

Typical Aqua heights for web approximations — **[AppKit default]**, not stated in the HIG (which explicitly says *don't measure its images*):

| Control | Regular | Small | Mini |
| --- | --- | --- | --- |
| Push button (visible bezel) | 21 px | 18 px | 15 px |
| Text field | 22 px | 19 px | 15 px |
| Font | 13 px | 11 px | 9 px |

```css
.push-button {
  font: 13px "Lucida Grande", "Lucida Sans Unicode", Geneva, Verdana, sans-serif;
  height: 21px; padding: 0 14px; border-radius: 4px;
  border: 1px solid #a5a5a5;
  background: linear-gradient(#ffffff, #f1f1f1);
  box-shadow: 0 1px 0 rgba(0,0,0,.08);
}
.push-button.default { /* the one colored button: harmless, Return/Enter */
  border-color: #4a7bd0; color: #fff;
  background: linear-gradient(#6cb3fa, #2a8af6);
}
.push-button:active { background: linear-gradient(#d9d9d9, #c8c8c8); } /* instant, on press */
```

## 9. Menus

- **Every command lives in the menu bar** (single menu bar, never menus inside a window). Order: Apple, *App*, File, Edit, Format, View, app-specific, Window, Help.
- Unavailable commands are **dimmed, not removed.**
- Menu titles: short, ideally one word, no icons. Items: title case, no articles, **ellipsis when more input follows**.
- Most-used items at the top; group related items with separators; don't mix actions and attributes in a group; avoid very long menus; max one level of submenu where possible.
- Toggled items: checkmark for attributes in effect, or a changing label (Show Toolbar / Hide Toolbar) — be unambiguous.
- Contextual menus: only commands relevant to the clicked item, short, and **never the only path** to a command.
- Web: if you build an in-page menu bar (e.g. for a desktop-style web app), every toolbar and contextual action must also be reachable there, with shortcut glyphs (⌘ ⌥ ⇧ ⌃) right-aligned.

## 10. Typography — Lucida Grande system fonts

The 2013 system font is **Lucida Grande** (Helvetica Neue only arrived with OS X 10.10). The HIG defines these roles:

| Role | Font | Use |
| --- | --- | --- |
| System | Regular 13 pt | menus, dialogs, regular controls |
| Emphasized system | Bold 13 pt | alert message (sparingly) |
| Small system | Regular 11 pt | alert informative text, column headers, help tags, small controls |
| Emphasized small | Bold 11 pt | titles of setting groups without a box |
| Mini system | Regular 9 pt | mini controls, panel labels |
| App font | Regular 13 pt | default for user content |
| Label font | Regular 10 pt | toolbar item labels, slider tick labels |
| View font | Regular 12 pt | lists and tables |

Rules: anti-aliased text; **one font family and consistent sizes per window**; type stays subordinate to content.

```css
:root {
  --font-system: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
}
body           { font: 13px/1.3 var(--font-system); color: #000; }
.alert-message { font-weight: bold; font-size: 13px; }
.alert-info,
th, .help-tag  { font-size: 11px; }
.toolbar-label { font-size: 10px; }
table, .list   { font-size: 12px; }
.panel         { font-size: 11px; }    /* panels use small controls */
```

Lucida Grande is not a web font and only exists on Macs; elsewhere the stack falls back. Don't ship a modern `system-ui` stack if the goal is the 2013 look — on current macOS that resolves to San Francisco.

## 11. Text style

- **Title case** for menu titles, menu items, push buttons, toolbar item labels, and labels that aren't full sentences (group box and list headings: "Mouse Speed", "Account Type"). Capitalize every word except articles, coordinating conjunctions and prepositions of ≤ 4 letters (unless first/last or part of a verb phrase).
- **Sentence case** for options that aren't strictly labels (checkbox and radio button text: "Show displays in menu bar") and dialog messages ("Are you sure you want to quit?"). Full sentences get ending punctuation, fragments don't.
- Contractions only where space is tight and the meaning survives ("Don't Allow Printing").
- **Ellipsis (…, the real character, not three periods)** when the command: needs more input (Open…, Find…, Print…), opens a window/dialog where the user completes it (Preferences…), or *always* shows a confirmation alert (Restart…). **No ellipsis** for New, Duplicate, Close, Get Info, Show Inspector (opening a panel completes the command).
- Truncate long names **in the middle** to keep the unique beginning and end.
- **Colon** after introductory labels before a control ("Minimize windows using:"); never inside buttons, menu items, tabs, segmented controls, column headings, or group box titles.
- One space between sentences. Dialog title = the command that opened it, without the ellipsis.
- Be specific; don't repeat the context ("Format", not "File Format", inside a Save dialog).

## 12. Physicality and realism (the 2013-specific bit)

Unlike later Apple guidance, the 2013 HIG *permits* real-world materials — with conditions:

- Add realism only if it improves **both** understanding and usability (Mail does not make you lick a stamp).
- Textures (wood, leather, metal, paper) must be authentic, look great at all resolutions, fit the whole app, and not feel bolted on.
- Simplify the real object freely; never sacrifice clarity for artistic expression (no cork board in a floor-plan app).
- Prefer to add decoration where it doesn't compete with the task — e.g. Photo Booth shows drapes only in full screen, around an untouched main view.
- Default is still the neutral, light-gray Aqua look; realism is the exception that needs a reason.

## 13. Pointers, drag and drop, gestures

- Use standard pointers only for their meaning: arrow, I-beam (text), crosshair (precise selection), pointing hand (links only), open/closed hand (move within view), resize arrows, copy (+), alias, not-allowed, poof, contextual-menu.
  Web: `cursor: default | text | crosshair | pointer | grab | grabbing | ew-resize | copy | alias | not-allowed | context-menu`. **`pointer` only for links**, not for buttons — that is the Mac convention.
- **Drag feedback after ≥ 3 pt of movement**: translucent drag image, correct copy/alias pointer, highlight valid destinations (not if the drag stays inside the source region). Allow dragging selections out of inactive windows.
- Respond to the gesture's *meaning* (go back, zoom), not the physical finger count; never override system gestures; never make a gesture the only way to do something; keep gesture feedback live and cheap.

## 14. Accessibility, internationalization, adaptability

- Every action reachable by keyboard (full keyboard access) and VoiceOver. Web: real `<button>`, `<select>`, `role`/ARIA, visible focus ring (Aqua's blue glow: `box-shadow: 0 0 0 3px rgba(59,153,252,.5)`).
- Plan for localization from the start: text expands; layout adapts (Auto Layout → flex/grid, no fixed text widths); mirror for right-to-left.
- Don't assume locale formats, hardware, a trackpad, a network, admin rights, or a single display.
- Retina: measure in points; provide @2x or vector artwork; start from larger artwork and scale down.
- Respect `prefers-reduced-motion` and `prefers-contrast` (not part of the 2013 HIG — modern additions that don't conflict with it).

## 15. App icon (briefly)

The 2013 Mac icon is a **detailed, realistic object** with real perspective and texture (unlike flat iOS 7 icons) — "your calling card". Toolbar and sidebar icons, by contrast, are simple, straight-on, monochrome templates (see §5, §6). Don't put an iOS icon on a Mac app unchanged.

## What the 2013 HIG does NOT contain

Don't attribute these to it: spring parameters (damping/response), velocity handoff, momentum projection formulas, interruptible-animation rules, haptics/audio-haptic rules, `backdrop-filter`-style vibrancy materials, Dynamic Type, dark mode. These come from later Apple sources (WWDC 2018+, OS X 10.10+). Translucent vibrancy and the flat Helvetica/San Francisco look arrived with Yosemite (2014) — they are **wrong** for a 2013-faithful design.

## Quick Reference

| Need | 2013 rule |
| --- | --- |
| System font | Lucida Grande 13 (regular), 11 (small), 9 (mini), 12 (lists), 10 (toolbar labels) |
| Control sizes | regular / small / mini — never mixed in one window |
| Command availability | everything in the menu bar; dim, don't hide |
| Toolbar | window-frame controls only, no persistent selection, customizable, mirrored in menus |
| Toolbar icon (in control) | ≤ 19×19, black template, straight-on, vector |
| Sidebar | blue only for the one primary source list; ≤ 2 levels |
| Window offset | +20 pt right, +20 pt down per new window |
| Dialog buttons | action rightmost, Cancel left of it, destructive ≥ 24 pt away |
| Default button | only for harmless actions; Esc / Cmd-. = Cancel |
| Alert | icon + bold message + small informative text; no "OK" for actions |
| Popover | arrow to source, no close button, not nested, never an alert |
| Ellipsis | only when more input / a dialog follows |
| Capitalization | title case for commands, sentence case for descriptions |
| Animation | only to explain; none on routine control use; [AppKit] 0.25 s ease-in-out |
| Drag start | after 3 pt; translucent drag image; correct pointer |
| Spinning wait cursor | appears after ~2 s unresponsive — show progress before that |
