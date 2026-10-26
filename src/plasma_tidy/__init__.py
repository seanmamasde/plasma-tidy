# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tidy (plasma-tidy): keeps your KDE Plasma desktop clean (Wayland).

Desktop:

Hides the desktop icons (and optionally the panel) after a configurable time
without activity. They come back on any mouse movement or key press, or only on
a click on the desktop, a screen corner or a shortcut.

- Idle time comes from swayidle (Wayland protocol ext_idle_notifier_v1). It
  reports after 1 s of stillness; from there the program counts on by itself.
  It only runs while there is something to learn from it.
- Hiding is done by a helper: an invisible widget on each desktop, which Tidy
  tells over D-Bus what to do. It makes the icons see-through and unreachable
  and catches the click that brings them back.
- Without the helper, hiding = pointing the desktop's folder view at an empty
  folder; the original folder is saved first and put back afterwards. Each
  screen then has an invisible "catcher" window just above the desktop for the
  click. A small KWin script keeps it there and out of the taskbar/Alt+Tab.
- That KWin script also handles the screen corner, and tells whether the
  desktop is the active window and when the pointer moves over the desktop
  (for the setting "Activity in other windows doesn't count").
- Show desktop (Meta+D) brings the icons back, and every activity counts in
  that view, unless that is switched off (desktop_shows).

Panel:

- A drawer is a small widget with an arrow. It tucks the widgets you choose away:
  all of them, or for a task manager only the pinned programs that aren't open.
  The widget ships inside this file and is written to Plasma's widget folder.

System tray:

- Choose per icon: automatic, show, hide (under ^) or off.

Rules and profiles:

- A profile keeps all settings together. A rule uses a profile, or focus mode, while
  something is the case: on battery, an external screen, a time of day, the program
  in front, a virtual desktop or an activity.

Nothing here polls: Tidy sleeps until it is told something changed, or until the
moment the icons are due to hide.

Only one copy ever runs. A second invocation (e.g. with --show from a shortcut)
passes its command to the running copy over D-Bus.

The code is in this package; build.py packs it into the single file `plasma-tidy`.
"""
