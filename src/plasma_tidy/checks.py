# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tidy's look at itself. Part of what Tidy does reaches into Plasma and KWin where they have
no public interface, so a new version of either may change it. The widgets and the KWin
script tell what they find; a part that is not there any more is left alone by them (it is
switched off, nothing half works), and Tidy says so once, and in full with --check."""

from .i18n import tr

OK, MISSING, UNUSED, NOT_YET = "ok", "missing", "unused", "not yet seen"

# What each part is, for a person.
DRAWER_PARTS = {
    "panel": "the drawers",
    "tasks": "hiding programs in a drawer",
    "tray": "the system tray in a drawer",
    "popup": "only the preview in a program's pop-up",
    "gap": "pop-ups and balloons floating above the panel",
    "link": "knowing where another program (Modish) has moved a widget",
}
HELPER_PARTS = {
    "icons": "the desktop helper",
    "widgets": "hiding the widgets on the desktop",
    "view": "the double-click on the desktop",
}
KWIN_PARTS = {
    "active": "knowing which window is in front",
    "pointer": "the pointer over the desktop counting",
    "menus": "drawers staying open under a menu",
    "panels": "drawers closing when the panel hides",
}
STATES = {OK: "works", MISSING: "does not work in this version", UNUSED: "not in use",
          NOT_YET: "not seen yet"}


class Checks:
    def __init__(self):
        self.kwin = {}
        self.drawers = {}   # drawer id -> {part: state}
        self.helpers = {}   # desktop id -> {part: state}

    def take(self, kind, key, found):
        """A report from a widget or the KWin script."""
        if not isinstance(found, dict):
            return
        found = {k: v for k, v in found.items() if isinstance(v, str)}
        if kind == "kwin":
            self.kwin = found
        elif kind == "drawer":
            self.drawers[key] = found
        elif kind == "helper":
            self.helpers[key] = found

    def keep_only(self, drawers, desktops=None):
        """Forget the drawers that are gone (removed from the panel, or a panel removed), and
        the helpers on a desktop without a screen: unplug a screen and Plasma keeps its
        desktop, but builds nothing in it, so its helper finds nothing to reach into.
        `desktops`: the desktops on a screen, or None when Plasma did not say."""
        self.drawers = {k: v for k, v in self.drawers.items() if k in drawers}
        if desktops is not None:
            self.helpers = {k: v for k, v in self.helpers.items() if k in desktops}

    def problems(self):
        """The parts that do not work, each named once, in a fixed order."""
        found = []
        for parts, reports in ((KWIN_PARTS, [self.kwin]), (HELPER_PARTS, self.helpers.values()),
                               (DRAWER_PARTS, self.drawers.values())):
            for part in parts:
                if any(report.get(part) == MISSING for report in reports):
                    found.append(parts[part])
        return found

    def notice(self, plasma_version):
        """The one message that says what does not work. Empty when everything does."""
        problems = self.problems()
        if not problems:
            return ""
        return tr("Plasma {version} is new to Tidy in some places. These parts are switched "
                  "off: {parts}. Everything else works as before. In a terminal, "
                  "plasma-tidy --check tells more.").format(
            version=plasma_version or "?", parts=", ".join(tr(p) for p in problems))

    def report(self, version, plasma_version, names):
        """Everything, for --check. `names`: drawer id -> name."""
        lines = [tr("Tidy {version} on Plasma {plasma}").format(version=version,
                                                                 plasma=plasma_version or "?")]

        def block(title, parts, found):
            lines.append("")
            lines.append(title)
            if not found:
                lines.append("  " + tr("has not reported (yet)"))
                return
            for part, text in parts.items():
                state = found.get(part, UNUSED)
                lines.append("  %s %s: %s" % ("✓" if state == OK else "✗" if state == MISSING
                                               else "·", tr(text), tr(STATES.get(state, state))))
        block(tr("KWin script"), KWIN_PARTS, self.kwin)
        for desktop, found in sorted(self.helpers.items()):
            block(tr("Desktop helper on desktop {id}").format(id=desktop), HELPER_PARTS, found)
        if not self.helpers:
            block(tr("Desktop helper"), HELPER_PARTS, {})
        for drawer, found in sorted(self.drawers.items()):
            name = names.get(drawer) or drawer
            block(tr("Drawer: {name}").format(name=name), DRAWER_PARTS, found)
        return "\n".join(lines)
