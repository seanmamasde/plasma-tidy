# Changes

## 0.4.0 — not released yet

- The Desktop tab of the settings is in four groups: when the icons hide, how they come back,
  what hides along, and how it is done.
- One choice instead of two for how the icons come back: on any movement or key press, on a
  click on the desktop, or on a double-click on the desktop. What only goes with a click
  shows only then. Your own settings stay as they are.
- The *Panel* tab is called *Drawers* now, because drawers is what it holds. A new *Panel*
  tab has what is about the panel as a whole: *Show the panel* (it was on *Desktop*) and
  *Balloons and previews* (it was below the drawers).
- A search field at the top of the settings window. Type a word, pick a setting from the
  list, and the window opens the right tab and marks the setting. It finds the names of
  settings, the choices in their lists, and the names of tabs and groups.
- Rules can keep Plasma's night light off: true colours while a program is in front or fills
  the screen, for a film or photo work. It comes back by itself afterwards.
- The rule *A program fills the whole screen* can be for one program: name it, or leave the
  field empty for any program.
- A drawer that slides and is turned round halfway goes back from where it is. (It used to jump
  to the end first and start again.)
- For other programs: a drawer makes known how far open it is, under the name `wispwareLink`
  on its widget (state, progress, duration, its icons and the room they take). Modish's centre
  mod follows it. Without such a program nothing changes.
- A folder you add to a drawer sorts its contents by name, folders first. (Folders that are
  in the panel already stay as they are.)
- A settings button next to each folder in a drawer's *In this drawer* list opens that
  folder's own settings: its icon, title, sorting and more.

## 0.3.5 — 2026-10-07

- *Add a folder…* in a drawer's settings puts a folder in the panel, in that drawer, for quick
  access. It is Plasma's own Folder View widget. A folder in the list is called after its
  folder and can be taken out of the panel there.

## 0.3.4 — 2026-10-07

- A new drawer leaves open programs in the panel: only the pinned programs that are not open
  go into it. (It used to take all programs, open ones too; that is still a choice, and the
  drawers you have keep their setting.)
- Installing from source is one step, `./build.py --install`, and its menu entry names the
  program by its full path: on Arch the entry and the shortcuts did not find `plasma-tidy`,
  because `~/.local/bin` is not on the desktop session's PATH there.

## 0.3.3 — 2026-10-07

- *One by one* is no longer slow: the next icon starts while the one before it is still coming,
  and the last icon of a long row starts within 1.2 s. It took 0.2 s and more for each icon,
  at any speed. Opening also goes one by one where the icons used to come all at once.
- A drawer does not close by itself while its icons are still coming.
- After unplugging a second screen Tidy no longer says that a part does not work in this
  Plasma version: the desktop of that screen is left out of its look at itself.

## 0.3.2 — 2026-10-06

- When Plasma starts, a closed drawer is closed from the first moment the panel shows. The
  panel used to come up with everything in view and tidy itself a third of a second later.
- Two drawers that open on a click on the panel stay together: a drawer that was open
  already no longer closes a moment after the click that opened the other, so they no longer
  take turns.
- Tidy's widgets no longer fill Plasma's log with "No signal handler" lines.

## 0.3.1 — 2026-10-06

- The drawer that the welcome window adds starts closed: the programs are tucked away at once.
- In a drawer's settings the list of programs keeps its rows together; room to spare stays
  below the list instead of between the rows.

## 0.3.0 — 2026-10-06

The first version meant for others. Since 0.2.0:

**Desktop icons**
- Icons that fade stay where they are: a panel that hides with them waits until they are gone.
- Fading, hiding the desktop widgets along with the icons (each widget can stay), a double-click
  on an empty spot hides them, and moving over the panel can count as activity.
- Hiding is done by a small helper on the desktop: instant, without reloading the desktop.
  The old way (an empty folder) stays as a fallback.
- Tidy no longer polls: it sleeps until something happens.

**Panel drawers**
- Open with a click on an empty spot of the panel; close when the pointer leaves, after use,
  when a window fills the screen, or when the panel slides out of view.
- A pop-up drawer that leaves the panel as it is (also for panels as long as their contents),
  in a row, column, grid or list, with or without a background, above the arrow or at the
  start, in the middle or at the end of the panel. It ends where the panel ends; at the edge
  of the screen a pointer pushed against that edge is on the icons.
- A row or a column in a pop-up is as thick as the panel, with icons as large as the panel's.
- Drag a program in a pop-up to another place, as in the panel.
- With open programs sent to the front or the back, a pinned program is back on its own spot
  when you close it, and dragging no longer moves the spot of a program that is open.
- An arrow without room stays out of the panel while its pop-up is open (the panel no longer
  shifts a little), and the pop-up lines up with the widget beside it.
- Which programs go in a drawer, where open programs stand, animations (slide, grow, one by
  one, fade), a mark on a closed drawer, names, and an arrow that can take no room at all.
- A drawer stays open under a program's pop-up or a menu, and while you drag a program to
  another place.
- Close a program from its pop-up and the panel and the drawer stay three seconds, to choose
  something else. Start a program from a drawer and the panel can stay a time you set.

**More**
- The panel can come into view by itself after you minimise (or close) a window.
- Focus mode: everything away until you switch it off.
- Rules and profiles: switch settings by power, screen, time, program, virtual desktop or
  activity; export and import.
- A peek key: hold it to see everything for a moment.
- Balloons and previews: Plasma's balloons on or off, the pop-up of a program with or without
  its preview (or only the preview), and both floating above the panel.
- Restore everything; switching Tidy off or quitting leaves Plasma as it is without Tidy.
- A welcome window on the first start.

**Look**
- Tidy's own icon: three slanted bars on a green tile, for the menu, Discover and the windows,
  and a one-colour version in the system tray that follows the theme, with its own look when
  the icons are hidden.
- The settings window fits a low screen: the Panel tab scrolls where it has no room. The
  list of programs of a drawer fills its box, without an empty strip or half a row.

**Under the hood**
- Lighter: about 24 MB of memory, no processor time at rest.
- Tidy checks what it reaches into in Plasma and KWin and says once what does not work in a new
  Plasma version; `plasma-tidy --check` lists it all.
- `plasma-tidy --report` for bug reports, without personal data.
- A package for Fedora, on COPR (`wispware/plasma-tidy`), and 102 tests.
- A page for software centres such as Discover (AppStream), with screenshots; the README
  shows Tidy at work.

## 0.2.0 — 2026-10-01

- Panel drawers: an arrow in the panel that tucks the programs and widgets you choose away.

## 0.1.0 — 2026-09-30

- First version: hides the desktop icons when you are not using them and brings them back on
  mouse movement, a click on the desktop, a screen corner or a shortcut; organises the system
  tray.
