# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tidy itself: when the icons hide and show, focus mode, rules, profiles."""

import json
import os
import shutil
import sys
import time

from PyQt6.QtCore import QMetaType, QObject, QProcess, QSettings, QTimer, pyqtSlot
from PyQt6.QtDBus import (QDBusArgument, QDBusConnection, QDBusInterface, QDBusMessage,
                          QDBusServiceWatcher)
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import QCheckBox, QMenu, QMessageBox, QSystemTrayIcon, QWidget

from .catcher import Catcher
from .checks import Checks
from .consts import (APP, APP_ICON, APP_NAME, AUTOSTART, BUTTONS, CLICKS_DOUBLE, CLICKS_SINGLE, DATA_DIR,
                     DONATE_URL, DRAWER_DEFAULTS, DRAWER_STATE, EMPTY_DIR, EMPTY_URL, IDLE_LINK,
                     IDLE_STEP, MODE_ACTIVITY, MODE_CLICK, PANEL_AFTER_CLOSE, PANEL_AFTER_NEVER,
                     PANEL_SETTLE,
                     PROFILE_SETTINGS,
                     TASK_POPUPS_PREVIEW,
                     REHIDE_FIXED, REHIDE_IDLE, RULE_FOCUS, RULE_NIGHT_LIGHT, RULE_PROFILE, TRAY_HIDDEN, TRAY_ICON,
                     TRAY_ICON_HIDDEN, TRAY_SHOWN,
                     VERSION)
from .i18n import set_language, tr
from .kwin import KWin
from .peek import PeekKey
from .plasma import Plasma, plasma_balloons, set_plasma_balloons
from .settings import SettingsDialog, open_donate
from .tray import TrayTab, remember_tray, tray_app_items, tray_minimal, tray_rule_mode, tray_rules
from .welcome import Welcome
from .widgets import drawer_texts, install_drawer, stored


def give_back_memory():
    """The settings window is gone: hand the memory it used back to the system. Python and
    the C library keep freed memory for later use by themselves; Tidy has no later use."""
    import ctypes
    import gc
    gc.collect()
    try:
        ctypes.CDLL(None).malloc_trim(0)
    except (OSError, AttributeError):
        pass  # another C library than glibc: nothing to do


class Tidy(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.settings = QSettings(APP, APP)
        self.plasma = Plasma()
        self.kwin = KWin()
        self.hidden = False
        self.focus = False          # focus mode: everything away, and it stays away
        self.pointer_on_panel = False
        self.hold_icons = False     # in focus mode, with the desktop icons part of it
        # The helpers on the desktops: how many there should be, and which have reported.
        self.adaptor = None         # set once Tidy is on the bus: its signals go through it
        self.helper_count = 0
        self.helpers = set()
        self.hidden_by_helper = False
        self.idle = None
        self.idle_since = None      # moment the current stillness began
        self.desktop_active = True  # is the desktop the active window?
        self.popup_open = False     # is a menu or pop-up open somewhere?
        self.shown_at = time.monotonic()
        self.catchers = []
        self.dialog = None
        self.quitting = False
        self.peeking = False        # the peek key is held: everything is shown for a moment
        self.peek_state = None
        self.rule_focus = False     # focus mode was switched on by a rule
        self.night_cookie = None    # held while a rule keeps the night light off
        self.rule_kinds = set()
        self.active_class = ""      # the program in front, and whether it fills the screen
        self.active_fullscreen = False
        self.seen_classes = set()
        self.vdesktop = 0
        self.vdesktop_names = []
        os.makedirs(EMPTY_DIR, exist_ok=True)
        install_drawer()
        self.checks = Checks()
        self.check_timer = QTimer(self, interval=8000, singleShot=True)
        self.check_timer.timeout.connect(self.review_checks)

        self.restore_peek_panels()  # crashed while peeking: the panel back to how it was
        self.restore_after_panels()
        self.recover_after_crash()
        self.restore_focus_state()  # crashed or logged out in focus mode: put things back
        self.showing_desktop = self.kwin.showing_desktop()
        bus = QDBusConnection.sessionBus()
        bus.connect("org.kde.KWin", "/KWin", "org.kde.KWin",
                    "showingDesktopChanged", self.on_showing_desktop)

        # Plasma restarted: check afterwards that everything is still right.
        self.plasma_watcher = QDBusServiceWatcher(
            "org.kde.plasmashell", bus, QDBusServiceWatcher.WatchModeFlag.WatchForRegistration)
        self.plasma_watcher.serviceRegistered.connect(
            lambda _: QTimer.singleShot(3000, self.on_plasma_restarted))

        # Screen connected/disconnected: rebuild the catchers.
        app.screenAdded.connect(self.on_screens_changed)
        app.screenRemoved.connect(self.on_screens_changed)

        self.tray = QSystemTrayIcon()
        menu = QMenu()
        self.enabled_action = QAction(menu, checkable=True)
        self.enabled_action.setChecked(self.settings.value("enabled", True, bool))
        self.enabled_action.toggled.connect(self.set_enabled)
        menu.addAction(self.enabled_action)
        self.focus_action = QAction(menu, checkable=True)
        self.focus_action.toggled.connect(self.set_focus)
        menu.addAction(self.focus_action)
        settings_action = menu.addAction(QIcon.fromTheme("configure"), "", self.show_settings)
        restore_action = menu.addAction(QIcon.fromTheme("edit-undo"), "", self.ask_restore)
        about_action = menu.addAction(QIcon.fromTheme("help-about"), "",
                                      lambda: self.show_settings(about=True))
        donate_action = menu.addAction("", self.on_donate)
        menu.addSeparator()
        self.profiles_menu = menu.addMenu("")
        self.profiles_menu.aboutToShow.connect(self.fill_profiles_menu)
        menu.addSeparator()
        quit_action = menu.addAction("", lambda: self.quit(by_hand=True))
        # English texts; retranslate() fills them in, and again when the language changes.
        self.menu_texts = [(self.enabled_action, "Enabled"), (self.focus_action, "Focus mode"),
                           (settings_action, "Settings…"),
                           (restore_action, "Restore everything…"),
                           (about_action, "About {app}"), (donate_action, "♥ Donate…"),
                           (quit_action, "Quit")]
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_click)
        self.retranslate()
        self.tray.show()

        # Fires once, at the moment the icons are due to hide: nothing runs in between.
        self.hide_timer = QTimer(self, singleShot=True)
        self.hide_timer.timeout.connect(self.on_tick)
        # The panel in view after a window was put away: until this fires.
        self.after_timer = QTimer(self, singleShot=True)
        self.after_timer.timeout.connect(self.on_after_timeout)
        self.schedule()

        QTimer.singleShot(5000, self.backup_launchers)
        QTimer.singleShot(2500, self.update_helpers)
        QTimer.singleShot(4000, self.update_fit_panels)

        # New icons in the system tray.
        self.tray_new = set()  # the applications whose icon just came
        self.tray_timer = QTimer(self, interval=2000, singleShot=True)
        self.tray_timer.timeout.connect(self.check_tray_items)
        bus.connect("org.kde.StatusNotifierWatcher", "/StatusNotifierWatcher",
                    "org.kde.StatusNotifierWatcher", "StatusNotifierItemRegistered",
                    self.on_tray_item)
        QTimer.singleShot(6000, self.check_tray_items)  # note which icons are there now

        # Rules: looked at again whenever something they depend on changes.
        self.rules_timer = QTimer(self, interval=400, singleShot=True)
        self.rules_timer.timeout.connect(self.evaluate_rules)
        self.rules_clock = QTimer(self, singleShot=True)
        self.rules_clock.timeout.connect(self.rules_changed)
        system = QDBusConnection.systemBus()
        system.connect("org.freedesktop.UPower", "/org/freedesktop/UPower",
                       "org.freedesktop.DBus.Properties", "PropertiesChanged", self.rules_changed)
        system.connect("org.freedesktop.login1", "/org/freedesktop/login1",
                       "org.freedesktop.login1.Manager", "PrepareForSleep", self.rules_changed)
        bus.connect("org.kde.ActivityManager", "/ActivityManager/Activities",
                    "org.kde.ActivityManager.Activities", "CurrentActivityChanged",
                    self.rules_changed)
        app.screenAdded.connect(self.rules_changed)
        app.screenRemoved.connect(self.rules_changed)
        QTimer.singleShot(4000, self.rules_changed)

        self.peek_key = PeekKey(self.peek)
        self.peek_key.set(self.settings.value("peek_key", ""))
        # Quit by hand the last time: back to work.
        if self.enabled_action.isChecked() and self.suspended():
            self.resume()

    def timed(name):
        """A value the moment of hiding depends on: changing it sets the timer afresh."""
        def get(self):
            return self.__dict__.get(name)

        def set_(self, value):
            self.__dict__[name] = value
            self.schedule()
        return property(get, set_)

    hidden = timed("hidden")
    idle_since = timed("idle_since")
    shown_at = timed("shown_at")
    del timed

    def schedule(self):
        """Set the timer for the moment the icons are due to hide, or stop it when there is
        nothing to wait for: icons hidden, Tidy off, or you are busy at the desktop."""
        timer = self.__dict__.get("hide_timer")
        if timer is None:
            return  # still starting up
        self.update_idle()
        waiting = self.fixed_rehide() or self.idle_since is not None
        if self.hidden or self.peeking or not self.enabled_action.isChecked() or not waiting:
            timer.stop()
        else:
            timer.start(int(self.remaining() * 1000) + 20)

    def mode(self):
        return self.settings.value("mode", MODE_ACTIVITY)

    def fixed_rehide(self):
        return self.mode() == MODE_CLICK and self.settings.value("rehide", REHIDE_IDLE) == REHIDE_FIXED

    def counts_activity(self):
        """Does mouse/keyboard input count right now? Not while you work in another window;
        then only moving the pointer over the desktop itself does, see on_desktop_motion."""
        return self.desktop_active or not self.settings.value("only_desktop", True, bool)

    def kwin_setup(self):
        """The settings that decide what the KWin helper does."""
        return (self.settings.value("corner", "none"),
                self.settings.value("only_desktop", True, bool),
                self.settings.value("panel_counts", True, bool),
                # Does a rule look at the program in front?
                any(r["when"] in ("app", "fullscreen") for r in self.rules()),
                self.settings.value("panel_after", PANEL_AFTER_NEVER) != PANEL_AFTER_NEVER)

    def load_kwin(self):
        self.kwin.load(*self.kwin_setup())

    def on_desktop_active(self, active):
        was = self.desktop_active
        self.desktop_active = active
        if active and not was:
            # Going to the desktop is activity in itself.
            self.idle_since = None
            if self.hidden and self.mode() == MODE_ACTIVITY and not self.hold_icons:
                self.show()
            if not self.focus:
                self.tell("DesktopActivated")  # for the drawers that open then
        elif not active and was and self.idle_since is None and not self.counts_activity():
            # Away from the desktop: from now on the timer keeps counting.
            self.idle_since = time.monotonic()
        self.update_idle()  # whether what you do counts has changed

    def on_desktop_motion(self):
        """Told by the KWin helper while another window is the active one: the pointer moves
        over the desktop (or the panel). That postpones hiding; the time starts again from
        this movement, whatever you do in the other window."""
        if self.counts_activity():
            return  # all input counts already
        if not self.hidden:
            self.idle_since = time.monotonic()
        elif self.mode() == MODE_ACTIVITY and not self.hold_icons:
            self.show()

    def restart_countdown(self):
        """The time until the icons hide starts afresh, as after showing them."""
        self.shown_at = time.monotonic()
        self.idle_since = None if self.counts_activity() else time.monotonic()

    def remaining(self):
        """Seconds until hiding (only meaningful while the icons are visible)."""
        timeout = self.settings.value("timeout", 10, int)
        now = time.monotonic()
        if self.fixed_rehide():
            left = timeout - (now - self.shown_at)
        elif self.idle_since is None:
            left = timeout
        else:
            left = timeout - (now - self.idle_since)
        return max(0.0, left)

    def busy(self):
        """Don't hide while you are editing Plasma or have a menu open:
        hiding reloads the desktop, which closes edit mode and menus."""
        return self.popup_open or bool(self.plasma.iface.property("editMode"))

    def on_tick(self):
        if not self.enabled_action.isChecked() or self.hidden or self.peeking:
            return
        if self.remaining() > 0:
            self.schedule()
        elif self.busy():
            # Postpone: the timer starts again once you're done. Look again in a moment.
            self.shown_at = time.monotonic()
            self.idle_since = time.monotonic()
            self.hide_timer.start(1000)
        else:
            self.hide()

    # --- hide / show -------------------------------------------------------

    def hide(self):
        if self.peeking:
            self.peek(False)  # first the panel back to how it was: hiding notes how it is set
        if self.hidden:
            return
        if self.settings.value("saved_state", ""):
            # An earlier putting back did not reach Plasma. First that, or what is noted
            # below would be the hidden state.
            self.show()
            if self.settings.value("saved_state", ""):
                return
        saved = {}
        by_helper = self.helper_way()
        if not by_helper:
            urls = self.urls_to_hide()
            if not urls:
                return  # plasmashell unreachable (e.g. restarting right now), or nothing to hide
            saved["urls"] = urls
        if self.settings.value("hide_panel", False, bool):
            saved["panels"] = self.plasma.panel_modes()
            # A panel that is in view because a window was just put away: how it is set is
            # what it was before that.
            for panel, mode in stored(self.settings, "after_panels").items():
                if int(panel) in saved["panels"]:
                    saved["panels"][int(panel)] = mode
        if saved:
            # Save first, hide afterwards: that way a crash can never lose anything.
            self.settings.setValue("saved_state", json.dumps(saved))
            self.settings.sync()
        if saved.get("panels"):
            # Icons that fade keep their places until they are gone: a panel that starts
            # hiding gives the desktop more room, and the icons would shift while they fade.
            fading = by_helper and self.settings.value("fade_icons", False, bool)
            wait = self.settings.value("fade_duration", 300, int) if fading else 0
            if wait > 0:
                QTimer.singleShot(wait, self.tuck_panels)
            else:
                self.tuck_panels(now=True)
        if not by_helper:
            self.plasma.set_desktop_urls({k: EMPTY_URL for k in saved["urls"]})
        self.hidden_by_helper = by_helper
        self.hidden = True
        self.update_icon()
        if self.settings.value("drawer_follow", False, bool):
            self.plasma.set_drawers_closed(True)
        if by_helper:
            self.send_state()  # the helper also catches the click that brings them back
        elif self.mode() == MODE_CLICK and not self.hold_icons:
            self.show_catchers()

    def tuck_panels(self, now=False):
        """The panels go with the icons: they hide by themselves from now on. A panel that
        is in view because a window was just put away stays for its time, and hides after."""
        panels = stored(self.settings, "saved_state").get("panels")
        if not panels or not (now or self.hidden):
            return  # shown again in the meantime
        after = stored(self.settings, "after_panels")
        if after:
            after.update({k: "autohide" for k in panels if k in after})
            self.settings.setValue("after_panels", json.dumps(after))
            self.settings.sync()
        modes = {int(k): "autohide" for k in panels if k not in after}
        if modes:
            self.plasma.set_panel_modes(modes)

    def urls_to_hide(self):
        """The other way of hiding: the desktops whose folder is swapped for an empty one,
        with the folder each shows now."""
        urls = {k: v for k, v in self.plasma.desktop_urls().items() if v != EMPTY_URL}
        skipped = self.skipped_screens()
        if skipped:
            # Leave the screens alone that are set to keep their icons.
            where = self.plasma.desktop_screens()

            def screen_name(desktop_id):
                # Plasma and Qt may round a scaled screen's size differently.
                for screen in self.app.screens():
                    g = screen.geometry()
                    if desktop_id in where and all(abs(a - b) <= 2 for a, b in zip(
                            where[desktop_id], (g.x(), g.y(), g.width(), g.height()))):
                        return screen.name()
                return None

            urls = {k: v for k, v in urls.items() if screen_name(k) not in skipped}
        return urls

    def show(self):
        self.hide_catchers()
        raw = self.settings.value("saved_state", "")
        panels_back = False
        if raw:
            state = stored(self.settings, "saved_state")
            reached = True
            if state.get("urls"):
                self.plasma.set_desktop_urls({int(k): v for k, v in state["urls"].items()})
                reached = self.plasma.reached
            if state.get("panels"):
                # A panel that is in view because a window was just put away goes straight
                # to how it is set, without hiding in between: its time is over.
                after = stored(self.settings, "after_panels")
                if any(k in after for k in state["panels"]):
                    after = {k: v for k, v in after.items() if k not in state["panels"]}
                    if after:
                        self.settings.setValue("after_panels", json.dumps(after))
                    else:
                        self.settings.remove("after_panels")
                        self.after_timer.stop()
                self.plasma.set_panel_modes({int(k): v for k, v in state["panels"].items()})
                reached = reached and self.plasma.reached
                panels_back = True
            # Plasma not there right now (restarting): keep what was saved, it is put back
            # when Plasma is.
            if reached:
                self.settings.remove("saved_state")
                self.settings.sync()
        if (self.hidden or raw) and self.settings.value("drawer_follow", False, bool):
            self.plasma.set_drawers_closed(False)
        fading = (panels_back and self.hidden_by_helper
                  and self.settings.value("fade_icons", False, bool))
        self.hidden = False
        self.hidden_by_helper = False
        self.restart_countdown()
        if hasattr(self, "tray"):
            self.update_icon()
        if fading:
            # A panel that comes back takes room from the desktop, and the icons move over
            # for it. They fade in once that is done, so they are not seen moving.
            QTimer.singleShot(PANEL_SETTLE, self.send_state)
        else:
            self.send_state()

    # --- the helpers on the desktops ----------------------------------------------------

    def tell(self, signal, *args):
        """Send one of Tidy's signals to its widgets in Plasma."""
        if self.adaptor:
            getattr(self.adaptor, signal).emit(*args)

    def helper_way(self):
        """Can the icons be hidden by the helpers? Only when every desktop that is on a
        screen has one that has reported. Otherwise Tidy swaps the desktop's folder for an
        empty one, which works without anything inside Plasma."""
        return (self.settings.value("use_helper", True, bool)
                and 0 < self.helper_count <= len(self.helpers))

    def desktop_state(self):
        """How the desktop should be, the way the helpers are told."""
        value = self.settings.value
        chosen = value("buttons", "left,right,middle").split(",")
        fade = value("fade_icons", False, bool)
        return {"hidden": bool(self.hidden and self.hidden_by_helper),
                "duration": value("fade_duration", 300, int) if fade else 0,
                "widgets": value("hide_widgets", False, bool),
                "keep": [i for i in value("widgets_keep", "").split(",") if i],
                "skip": sorted(self.skipped_screens()),
                # The click that brings the icons back: which buttons, one click or two.
                "catch": self.mode() == MODE_CLICK and not self.hold_icons,
                "buttons": sum(BUTTONS[k].value for k in chosen if k in BUTTONS),
                "double": value("clicks", CLICKS_SINGLE) == CLICKS_DOUBLE,
                "doubleHides": value("double_hides", False, bool)}

    def send_state(self):
        if self.helpers:
            self.tell("DesktopState", json.dumps(self.desktop_state()))

    def on_helper_ready(self, desktop):
        """A helper has started on a desktop (at Tidy's start, or Plasma's): tell it how
        things are."""
        self.helpers.add(desktop)
        if self.hidden and not self.hidden_by_helper and self.helper_way():
            # The icons were hidden the other way while the helper was not there yet (it was
            # just switched on, or Plasma has just started): hand them over to the helper.
            self.show()
            self.hide()
        self.send_state()

    def on_desktop_click(self):
        """Reported by a helper: a click on the desktop while the icons are away."""
        if self.hidden and not self.hold_icons:
            self.show()

    def apply_tips(self):
        """Bring Plasma's text balloons and the pop-ups of the programs in the panel in line
        with the settings. These are Plasma's own settings, so how they were is remembered
        the first time, for "Restore everything"."""
        if self.suspended():
            return  # Tidy is off: Plasma stays as it is without Tidy, until resume()
        balloons = self.settings.value("balloons", True, bool)
        popup = self.settings.value("task_popup", "preview")
        now_balloons, now_previews = plasma_balloons(), self.plasma.task_previews()
        previews = {k: popup in TASK_POPUPS_PREVIEW for k, v in now_previews.items()
                    if v != (popup in TASK_POPUPS_PREVIEW)}
        if (balloons != now_balloons or previews) and not self.settings.value("tips_original", ""):
            self.settings.setValue("tips_original", json.dumps(
                {"balloons": now_balloons, "previews": now_previews}))
        if balloons != now_balloons:
            set_plasma_balloons(balloons)
        if previews:
            self.plasma.set_task_previews(previews)
        # No pop-up at all is something the task manager cannot do itself, and with Plasma's
        # balloons off it shows none: a drawer that has the task manager in it takes the
        # pop-up away, or shows it, instead. The drawers' own balloons follow Plasma's too.
        want = {"taskTips": popup != "none", "balloons": balloons, "taskBare": popup == "only",
                "taskClose": self.settings.value("task_close", True, bool),
                "taskGap": self.settings.value("task_gap", False, bool),
                "tipGap": self.settings.value("balloon_gap", False, bool)}
        if any(d["config"][k] != v for d in self.plasma.drawers() for k, v in want.items()):
            self.plasma.set_drawer_config(None, want)

    def restore_tips(self):
        """Put Plasma's balloons and pop-ups back as they were before Tidy changed them."""
        saved = stored(self.settings, "tips_original")
        if saved:
            set_plasma_balloons(bool(saved.get("balloons", True)))
            self.plasma.set_task_previews({int(k): bool(v)
                                           for k, v in saved.get("previews", {}).items()})
            self.settings.setValue("balloons", bool(saved.get("balloons", True)))
            self.settings.remove("tips_original")
        self.settings.setValue("task_popup", "preview" if all(
            self.plasma.task_previews().values()) else "text")
        self.plasma.set_drawer_config(None, {"taskTips": True, "balloons": True, "taskBare": False, "taskGap": False, "tipGap": False})

    def update_fit_panels(self):
        """Tell each drawer whether its panel is as long as its contents; it then fades
        instead of sliding. Looked at when Tidy or Plasma starts and when settings change."""
        fit = {panel["panel"]: bool(panel.get("fit")) for panel in self.plasma.panel_widgets()}
        for drawer in self.plasma.drawers():
            wanted = fit.get(drawer["panel"], False)
            if drawer["config"]["fitPanel"] != wanted:
                self.plasma.set_drawer_config(drawer["id"], {"fitPanel": wanted})

    def update_helpers(self):
        """Put a helper on the desktops, or take it away, as the setting says."""
        wanted = self.settings.value("use_helper", True, bool)
        self.helper_count = self.plasma.ensure_helpers(wanted)
        if not wanted:
            self.helpers.clear()
        elif len(self.helpers) < self.helper_count:
            self.tell("Started")  # one may have missed us: ask them to report

    def recover_after_crash(self):
        """Was the desktop still on the empty folder (crash, logout)? Put it back."""
        if self.settings.value("saved_state", ""):
            self.show()
        stuck = {k: "desktop:/" for k, v in self.plasma.desktop_urls().items() if v == EMPTY_URL}
        if stuck:
            self.plasma.set_desktop_urls(stuck)

    def on_plasma_restarted(self):
        self.helpers.clear()  # the new Plasma's helpers report by themselves
        self.update_helpers()
        self.update_fit_panels()
        if not self.hidden:
            self.recover_after_crash()
        if not self.focus:
            self.restore_focus_state()

    # --- looking at itself ----------------------------------------------------

    def on_check(self, kind, key, text):
        try:
            found = json.loads(text)
        except ValueError:
            return
        self.checks.take(kind, key, found)
        self.check_timer.start()  # all reports in, then one look

    def plasma_version(self):
        return self.plasma.run("print(applicationVersion);").strip()

    def review_checks(self):
        """Say once, per Plasma version, what does not work in it. Nothing when all is well."""
        version = self.plasma_version()
        self.checks.keep_only({str(d["id"]) for d in self.plasma.drawers()},
                              self.plasma.desktops_on_screen())
        text = self.checks.notice(version)
        told = version + "|" + ",".join(self.checks.problems()) if text else ""
        if told == self.settings.value("checks_told", ""):
            return
        self.settings.setValue("checks_told", told)
        if text and getattr(self, "tray", None):
            self.tray.showMessage(APP_NAME, text, QSystemTrayIcon.MessageIcon.Warning, 20000)

    def check_report(self):
        names = {str(d["id"]): d["config"].get("name", "") for d in self.plasma.drawers()}
        self.checks.keep_only(set(names))
        return self.checks.report(VERSION, self.plasma_version(), names)

    # --- focus mode -----------------------------------------------------------

    def set_focus(self, on):
        """Focus mode: tuck everything away at once and keep it away until it is switched
        off; then everything goes back to how it was."""
        if on == self.focus:
            return
        self.peek(False)
        if on:
            # From how things are with the icons in view: what is noted here is put back
            # when focus mode goes off, and hiding has changed the panel and the drawers.
            if self.hidden:
                self.show()
            setting = lambda key, default: self.settings.value("focus_" + key, default, bool)
            state = {}
            if setting("drawers", True):
                state["drawers"] = {str(d["id"]): d["config"]["closed"]
                                    for d in self.plasma.drawers()}
            tray = self.plasma.tray_config() if setting("tray", True) else None
            if tray:
                state["tray"] = {k: tray[k] for k in ("extra", "shown", "hidden")}
            if setting("panel", False):
                state["panels"] = self.plasma.panel_modes()
            # Save first, change afterwards: that way a crash can never lose anything.
            self.settings.setValue("focus_state", json.dumps(state))
            self.settings.sync()
            self.focus = True
            if "drawers" in state:
                self.plasma.set_drawers_closed(True)
            if tray:
                remember_tray(self.settings, tray)
                extra, shown, hidden = tray_minimal(tray, tray_app_items())
                if APP not in tray["hidden"]:
                    # Our own icon stays where it was: it is the way out of focus mode.
                    hidden = [i for i in hidden if i != APP]
                self.plasma.set_tray_config(extra, shown, hidden)
            if state.get("panels"):
                self.plasma.set_panel_modes({k: "autohide" for k in state["panels"]})
            if setting("icons", True):
                self.hold_icons = True
                self.hide_catchers()  # no click on the desktop brings them back now
                self.hide()
        else:
            self.focus = False
            self.hold_icons = False
            self.show()
            self.restore_focus_state()
        self.focus_action.setChecked(on)
        self.update_icon()
        self.send_state()  # in focus mode a click on the desktop does not bring the icons back

    def restore_focus_state(self):
        """Put back what focus mode changed. Also after a crash or a logout in focus mode."""
        raw = self.settings.value("focus_state", "")
        if not raw or not self.plasma.panel_modes():
            return  # nothing to do, or plasmashell unreachable: a later try will do it
        state = stored(self.settings, "focus_state")
        for drawer_id, closed in state.get("drawers", {}).items():
            self.plasma.set_drawer_config(int(drawer_id), {"closed": closed})
        if "tray" in state:
            tray = state["tray"]
            self.plasma.set_tray_config(tray["extra"], tray["shown"], tray["hidden"])
        if state.get("panels"):
            self.plasma.set_panel_modes(state["panels"])
        self.settings.remove("focus_state")
        self.settings.sync()

    # --- catchers ---------------------------------------------------------

    def show_catchers(self):
        self.hide_catchers()
        skipped = self.skipped_screens()
        for screen in self.app.screens():
            if screen.name() in skipped:
                continue
            catcher = Catcher(screen, self.on_catcher_click)
            catcher.show()
            self.catchers.append(catcher)

    def hide_catchers(self):
        for catcher in self.catchers:
            catcher.close()
            catcher.deleteLater()
        self.catchers = []

    def on_screens_changed(self, _screen):
        QTimer.singleShot(3000, self.update_helpers)  # a new screen gets a desktop first
        if self.catchers:
            self.show_catchers()

    def on_catcher_click(self, button, double):
        if double != (self.settings.value("clicks", CLICKS_SINGLE) == CLICKS_DOUBLE):
            return
        chosen = self.settings.value("buttons", "left,right,middle").split(",")
        if any(BUTTONS[k] == button for k in chosen if k in BUTTONS) and not self.hold_icons:
            self.show()

    @pyqtSlot(bool)
    def on_showing_desktop(self, showing):
        self.showing_desktop = showing
        if showing and self.hidden and not self.hold_icons:
            self.show()
        self.update_idle()

    # --- idle -------------------------------------------------------------

    def idle_program(self):
        """swayidle, started through a link with a neutral name. Some programs look for
        "sway" in the process list to detect the Sway compositor (Warp then drops its
        window buttons); a process called swayidle fools them."""
        target = shutil.which("swayidle")
        try:
            if not target:
                return "swayidle"
            if not os.path.islink(IDLE_LINK) or os.readlink(IDLE_LINK) != target:
                os.makedirs(DATA_DIR, exist_ok=True)
                if os.path.lexists(IDLE_LINK):
                    os.remove(IDLE_LINK)
                os.symlink(target, IDLE_LINK)
            return IDLE_LINK
        except OSError:
            return target

    def idle_needed(self):
        """Is there anything to learn from the idle watcher right now? With the icons in view:
        when you stop moving. With the icons hidden: only if movement brings them back. And
        nothing at all while what you do does not count: in another window (the time then
        runs from when you left the desktop, and the KWin helper tells of the pointer over
        the desktop), or with a fixed time until the icons hide again."""
        if self.quitting or not self.enabled_action.isChecked() or not self.counts_activity():
            return False
        if not self.hidden:
            return not self.fixed_rehide()
        return not self.hold_icons and (self.mode() == MODE_ACTIVITY or self.showing_desktop)

    def update_idle(self):
        """Run the idle watcher only while it is needed. It starts a small process each time
        you pause and each time you go on, and with the icons hidden until you click there
        is nothing to do with that."""
        needed = self.idle_needed()
        if needed and not self.idle:
            self.start_idle()
        elif not needed and self.idle:
            self.stop_idle()

    def start_idle(self):
        self.stop_idle()
        self.idle = QProcess()
        self.idle.readyReadStandardOutput.connect(self.on_idle_output)
        self.idle.finished.connect(self.on_idle_died)
        self.idle.start(self.idle_program(), ["-w", "timeout", str(IDLE_STEP), "echo idle",
                                              "resume", "echo active"])

    def stop_idle(self):
        if self.idle:
            self.idle.readyReadStandardOutput.disconnect()
            self.idle.finished.disconnect()
            self.idle.kill()
            self.idle.waitForFinished(1000)
            self.idle = None

    def on_idle_died(self):
        # swayidle stopped unexpectedly: start it again after a short wait, if still needed.
        self.idle = None
        QTimer.singleShot(2000, self.update_idle)

    def on_idle_output(self):
        if not self.idle:
            return  # swayidle already gone (shutdown): a late signal has nothing to read
        for line in bytes(self.idle.readAllStandardOutput()).decode().split():
            if line == "idle":
                since = time.monotonic() - IDLE_STEP
                if self.idle_since is None or self.counts_activity():
                    self.idle_since = since
            elif line == "active":
                if not self.counts_activity():
                    continue
                self.idle_since = None
                if self.hidden and not self.hold_icons and (self.mode() == MODE_ACTIVITY
                                                       or self.showing_desktop):
                    self.show()

    # --- tray -------------------------------------------------------------

    def update_icon(self):
        shown = QIcon.fromTheme(TRAY_ICON, QIcon.fromTheme("view-visible"))
        hidden = QIcon.fromTheme(TRAY_ICON_HIDDEN, QIcon.fromTheme("view-hidden"))
        if self.focus:
            self.tray.setIcon(hidden)
            status = tr("{app} — focus mode")
        elif not self.enabled_action.isChecked():
            self.tray.setIcon(QIcon(shown.pixmap(64, QIcon.Mode.Disabled)))
            status = tr("{app} — disabled")
        elif self.hidden:
            self.tray.setIcon(hidden)
            status = tr("{app} — icons hidden")
        else:
            self.tray.setIcon(shown)
            status = tr("{app} — icons visible")
        self.tray.setToolTip(status.format(app=APP_NAME))

    def retranslate(self):
        for action, text in self.menu_texts:
            action.setText(tr(text).format(app=APP_NAME))
        self.profiles_menu.setTitle(tr("Profiles"))
        self.update_icon()
        self.plasma.set_drawer_config(None, drawer_texts())

    def set_enabled(self, on):
        self.settings.setValue("enabled", on)
        self.update_icon()
        self.schedule()
        self.rules_changed()
        if on:
            self.idle_since = None
            self.shown_at = time.monotonic()
            self.resume()
        else:
            self.rule_focus = False
            self.peek(False)
            self.set_focus(False)
            self.hold_night_light(False)
            self.stop_idle()
            self.show()
            self.suspend()

    def suspended(self):
        return self.settings.value("suspended", False, bool)

    def suspend(self):
        """Tidy switched off, or quit by hand: Plasma is as it is without Tidy. The drawers
        are paused (everything in them in view, their arrows dimmed) and Plasma's balloons
        and pop-ups go back to how they were. Tidy's own settings stay, for resume()."""
        self.settings.setValue("suspended", True)
        self.settings.sync()
        self.plasma.set_drawer_config(None, {"paused": True})
        saved = stored(self.settings, "tips_original")
        if saved:
            if bool(saved.get("balloons", True)) != plasma_balloons():
                set_plasma_balloons(bool(saved.get("balloons", True)))
            self.plasma.set_task_previews({int(k): bool(v)
                                           for k, v in saved.get("previews", {}).items()})

    def resume(self):
        """Tidy is on again: the drawers work again, and the balloons are as set in Tidy."""
        self.settings.remove("suspended")
        self.plasma.set_drawer_config(None, {"paused": False})
        self.apply_tips()

    def backup_launchers(self):
        """Keep a copy of every task manager's pinned programs, as a last resort for "Restore
        everything"."""
        held = self.plasma.held_launchers()
        backup = stored(self.settings, "launchers_backup")
        for widget_id, launchers in self.plasma.task_launchers().items():
            # What a closed drawer holds, plus whatever was pinned since.
            complete = held.get(widget_id, []) + [i for i in launchers
                                                  if i not in held.get(widget_id, [])]
            if complete:
                backup[str(widget_id)] = complete
        self.settings.setValue("launchers_backup", json.dumps(backup))

    def recover_launchers(self):
        """A task manager without any pinned program, while we have a copy: put it back."""
        backup = stored(self.settings, "launchers_backup")
        for widget_id, launchers in self.plasma.task_launchers().items():
            if not launchers and backup.get(str(widget_id)):
                self.plasma.set_task_launchers(widget_id, backup[str(widget_id)])

    def restore_everything(self, tray=False):
        """Put the desktop back as if Tidy were not there: everything visible, every Plasma
        setting that Tidy or a drawer changed restored, and Tidy itself switched off."""
        self.set_focus(False)
        self.enabled_action.setChecked(False)  # stops the timer and shows the icons
        self.show()                            # also when Tidy already was off
        self.recover_after_crash()
        self.backup_launchers()
        self.settings.setValue("suspended", True)  # also when Tidy already was off
        self.plasma.set_drawer_config(None, {"paused": True})
        self.restore_tips()
        # Once the drawers have handed everything back.
        QTimer.singleShot(2000, self.recover_launchers)
        original = self.settings.value("tray_original", "")
        if tray and original:
            try:
                saved = json.loads(original)
                self.plasma.set_tray_config(saved["extra"], saved["shown"], saved["hidden"])
            except (ValueError, KeyError):
                pass

    def ask_restore(self, parent=None):
        box = QMessageBox(QMessageBox.Icon.Question, APP_NAME, tr("Restore everything?"),
                          parent=parent if isinstance(parent, QWidget) else None)
        box.setInformativeText(tr(
            "This shows your desktop icons, your panel and everything in the drawers again, "
            "and puts back the Plasma settings that {app} changed. {app} is switched off and "
            "the drawers are paused until you switch {app} on again.").format(app=APP_NAME))
        tray = None
        if self.settings.value("tray_original", ""):
            tray = QCheckBox(tr("Also put the system tray back as it was before {app} changed "
                                "it").format(app=APP_NAME))
            box.setCheckBox(tray)
        restore = box.addButton(tr("Restore"), QMessageBox.ButtonRole.AcceptRole)
        box.addButton(QMessageBox.StandardButton.Cancel)
        box.exec()
        if box.clickedButton() is restore:
            self.restore_everything(tray=bool(tray and tray.isChecked()))

    def welcome(self):
        self.settings.setValue("welcomed", True)
        self.welcome_dialog = Welcome(self)
        self.welcome_dialog.show()

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_settings()

    def on_donate(self):
        if DONATE_URL:
            open_donate()
        else:
            self.show_settings(about=True)

    def show_settings(self, about=False, tab=None):
        if self.dialog:
            if about:
                self.dialog.tabs.setCurrentWidget(self.dialog.about_tab)
            self.dialog.raise_()
            self.dialog.activateWindow()
            return
        # Non-modal: a modal window would block clicks on our own catchers,
        # and with that trying out click mode.
        self.dialog = SettingsDialog(self)
        # OK with nothing changed is just closing the window.
        self.dialog.accepted.connect(
            lambda dlg=self.dialog: self.apply_settings(dlg) if dlg.changed else None)
        self.dialog.finished.connect(self.on_dialog_closed)
        if about:
            self.dialog.tabs.setCurrentWidget(self.dialog.about_tab)
        elif tab is not None:
            self.dialog.tabs.setCurrentIndex(tab)
        self.dialog.show()

    def on_dialog_closed(self):
        self.dialog.deleteLater()
        self.dialog = None
        self.rules_changed()
        QTimer.singleShot(1500, give_back_memory)

    def hidden_setup(self):
        """The settings that decide what exactly is hidden while the icons are hidden."""
        return (self.settings.value("hide_panel", False, bool),
                self.settings.value("skip_screens", ""),
                self.settings.value("use_helper", True, bool))

    def after_settings(self, was_hidden, setup):
        """New settings are in use from now. Icons that were hidden stay hidden."""
        if was_hidden and self.hidden:
            if setup != self.hidden_setup():
                # What is hidden has changed (the panel, which screens): hide afresh.
                self.show()
                self.hide()
            elif self.mode() == MODE_CLICK and not self.hold_icons:
                self.show_catchers()
            else:
                self.hide_catchers()
        else:
            self.restart_countdown()
        self.schedule()  # the way of showing may have changed, and with it what is needed
        self.send_state()

    def apply_settings(self, dlg):
        self.peek(False)
        self.rule_focus = False
        self.set_focus(False)  # the settings below would get mixed up with what it holds
        was_hidden, setup = self.hidden, self.hidden_setup()
        dlg.focus_tab.save()
        old_kwin = self.kwin_setup()
        self.settings.setValue("timeout", dlg.timeout.value())
        self.settings.setValue("mode", dlg.chosen_mode())
        self.settings.setValue("buttons", dlg.chosen_buttons())
        self.settings.setValue("rehide", dlg.rehide.currentData())
        self.settings.setValue("corner", dlg.corner.currentData())
        self.settings.setValue("hide_panel", dlg.panel.isChecked())
        self.settings.setValue("panel_after", dlg.panel_after.currentData())
        self.settings.setValue("only_desktop", dlg.only_desktop.isChecked())
        self.settings.setValue("panel_counts", dlg.panel_counts.isChecked())
        self.settings.setValue("skip_screens", dlg.skipped_screens())
        self.settings.setValue("fade_icons", dlg.fade_icons.isChecked())
        self.settings.setValue("fade_duration", dlg.fade_duration.value())
        self.settings.setValue("clicks", dlg.chosen_clicks())
        self.settings.setValue("double_hides", dlg.double_hides.isChecked())
        self.settings.setValue("hide_widgets", dlg.hide_widgets.isChecked())
        self.settings.setValue("widgets_keep", ",".join(
            [i for i in dlg.widgets_gone if i not in dlg.widget_boxes]
            + [i for i, box in dlg.widget_boxes.items() if not box.isChecked()]))
        self.settings.setValue("use_helper", dlg.use_helper.isChecked())
        self.update_helpers()
        self.settings.setValue("peek_panel", dlg.peek_panel.isChecked())
        peek = dlg.peek_key.keySequence().toString(QKeySequence.SequenceFormat.PortableText)
        if peek != self.settings.value("peek_key", ""):
            self.settings.setValue("peek_key", peek)
            self.peek_key.set(peek)
        dlg.rules_tab.save()
        self.set_autostart(dlg.autostart.isChecked())
        if dlg.language.currentData() != self.settings.value("language", "auto"):
            self.settings.setValue("language", dlg.language.currentData())
            set_language(dlg.language.currentData())
            self.retranslate()
        dlg.tray_tab.apply()
        self.backup_launchers()  # before a drawer may start holding them
        dlg.drawer_tab.apply()
        self.update_fit_panels()
        self.settings.setValue("balloons", dlg.drawer_tab.balloons.isChecked())
        self.settings.setValue("task_popup", dlg.drawer_tab.task_popup.currentData())
        self.settings.setValue("task_close", dlg.drawer_tab.task_close.isChecked())
        self.settings.setValue("task_gap", dlg.drawer_tab.task_gap.isChecked())
        self.settings.setValue("balloon_gap", dlg.drawer_tab.balloon_gap.isChecked())
        self.apply_tips()
        self.settings.setValue("drawer_follow", dlg.drawer_tab.follow.isChecked())
        if self.kwin_setup() != old_kwin:
            self.load_kwin()
        self.after_settings(was_hidden, setup)
        dlg.applied()
        self.rules_changed()

    def skipped_screens(self):
        return {name for name in self.settings.value("skip_screens", "").split(",") if name}

    # --- peek: everything shown while a key is held -----------------------------------

    def peek(self, on):
        """Show everything for a moment (True) or end that (False); None switches."""
        if on is None:
            on = not self.peeking
        if on == self.peeking:
            return
        self.peeking = on
        self.tell("Peeking", on)  # the drawers stay open for as long as it lasts
        if on:
            self.restore_after_panels()
            self.peek_state = {"hidden": bool(self.hidden)}
            if self.hidden:
                self.show()
            if self.settings.value("peek_panel", True, bool):
                # A panel that hides, or sits behind a window: in view, on top of the windows.
                # They keep their size; a window in full screen stays on top of the panel.
                tucked = {k: v for k, v in self.plasma.panel_modes().items()
                          if v in ("autohide", "dodgewindows")}
                if tucked:
                    # Saved first: a crash while peeking must not leave the panel like this.
                    self.settings.setValue("peek_panels", json.dumps(tucked))
                    self.settings.sync()
                    self.plasma.set_panel_modes({k: "windowsgobelow" for k in tucked})
        else:
            state, self.peek_state = self.peek_state or {}, None
            self.restore_peek_panels()  # before hiding, which notes how the panels are set
            if state.get("hidden"):
                self.hide()
            else:
                # The icons were in view already: the time until they hide starts afresh.
                self.shown_at = time.monotonic()
                if not self.counts_activity():
                    self.idle_since = time.monotonic()
        self.schedule()

    # --- the panel in view after a window is put away --------------------------------------

    def on_window_gone(self, how):
        """Told by the KWin helper: a window was minimised ("minimized") or closed. A panel
        that is out of view then comes up, on top of the windows, the way a peek shows it."""
        wanted = self.settings.value("panel_after", PANEL_AFTER_NEVER)
        if wanted == PANEL_AFTER_NEVER or (how == "closed" and wanted != PANEL_AFTER_CLOSE):
            return
        if self.peeking or self.focus or not self.enabled_action.isChecked():
            return
        if not self.settings.value("after_panels", ""):
            tucked = {k: v for k, v in self.plasma.panel_modes().items()
                      if v in ("autohide", "dodgewindows")}
            if not tucked:
                return
            # Saved first: a crash must not leave the panel like this.
            self.settings.setValue("after_panels", json.dumps(tucked))
            self.settings.sync()
            self.plasma.set_panel_modes({k: "windowsgobelow" for k in tucked})
        self.after_timer.start(self.after_time())

    def after_time(self):
        return max(1, self.settings.value("timeout", 10, int)) * 1000

    def on_panel_pointer(self, on):
        """Told by the KWin helper: the pointer came onto a panel, or left it."""
        self.pointer_on_panel = on
        if not on and self.settings.value("after_panels", ""):
            self.after_timer.start(self.after_time())  # the time starts when you leave it

    def on_after_timeout(self):
        if not self.pointer_on_panel:
            self.restore_after_panels()

    def restore_after_panels(self):
        """Put the panels back as they were before a window was put away; also after a
        crash, and before anything else changes how the panels are set."""
        raw = self.settings.value("after_panels", "")
        if not raw:
            return
        timer = self.__dict__.get("after_timer")
        if timer is not None:
            timer.stop()
        try:
            self.plasma.set_panel_modes({int(k): v for k, v in json.loads(raw).items()})
        except (ValueError, AttributeError):
            pass
        self.settings.remove("after_panels")
        self.settings.sync()

    def restore_peek_panels(self):
        """Put the panels back as they were before a peek; also after a crash while peeking."""
        raw = self.settings.value("peek_panels", "")
        if not raw:
            return
        try:
            self.plasma.set_panel_modes({int(k): v for k, v in json.loads(raw).items()})
        except (ValueError, AttributeError):
            pass
        self.settings.remove("peek_panels")
        self.settings.sync()

    # --- double-click on the desktop ----------------------------------------------------

    def on_desktop_double_click(self):
        """Reported by the helper on the desktop: a double-click on an empty spot."""
        if (self.settings.value("double_hides", False, bool) and not self.hidden
                and self.enabled_action.isChecked() and not self.peeking
                and time.monotonic() - self.shown_at > 0.6):
            self.hide()

    # --- rules ----------------------------------------------------------------------

    def rules(self):
        found = stored(self.settings, "rules", list)
        return [r for r in found if isinstance(r, dict) and r.get("when")]

    def on_battery(self):
        props = QDBusInterface("org.freedesktop.UPower", "/org/freedesktop/UPower",
                               "org.freedesktop.DBus.Properties", QDBusConnection.systemBus())
        props.setTimeout(1000)
        args = props.call("Get", "org.freedesktop.UPower", "OnBattery").arguments()
        return bool(args and args[0] is True)

    def ask_activities(self, *call):
        manager = QDBusInterface("org.kde.ActivityManager", "/ActivityManager/Activities",
                                 "org.kde.ActivityManager.Activities",
                                 QDBusConnection.sessionBus())
        manager.setTimeout(1000)
        reply = manager.call(*call)
        args = reply.arguments()
        ok = reply.type() == QDBusMessage.MessageType.ReplyMessage
        return args[0] if ok and args else None

    def activities(self):
        """The activities as {id: name}, and the id of the current one."""
        names = {i: self.ask_activities("ActivityName", i) or i
                 for i in self.ask_activities("ListActivities") or []}
        return names, self.current_activity()

    def current_activity(self):
        return self.ask_activities("CurrentActivity") or ""

    def rule_matches(self, rule):
        when, arg = rule.get("when"), str(rule.get("arg", ""))
        if when == "battery":
            return self.on_battery()
        if when == "mains":
            return not self.on_battery()
        if when == "external":
            return len(self.app.screens()) > 1
        if when == "time":
            start, _, end = arg.partition("-")
            now = time.strftime("%H:%M")
            if start <= end:
                return start <= now < end
            return now >= start or now < end  # over midnight
        if when == "app":
            return bool(arg) and arg.lower() == self.active_class.lower()
        if when == "fullscreen":   # of any program, or only of the one that is named
            return self.active_fullscreen and (not arg or arg.lower() == self.active_class.lower())
        if when == "vdesktop":
            return arg == str(self.vdesktop)
        if when == "activity":
            return bool(arg) and arg == self.current_activity()
        return False

    @pyqtSlot()
    def rules_changed(self):
        self.rules_timer.start()

    def on_active_window(self, name, fullscreen):
        self.active_class, self.active_fullscreen = name, fullscreen
        self.rules_changed()

    def on_window_classes(self, names):
        """The programs that are open, told when the settings window opens."""
        self.seen_classes = set(names)
        if self.dialog:
            self.dialog.rules_tab.update_programs()

    def on_virtual_desktop(self, number, names):
        self.vdesktop, self.vdesktop_names = number, names
        if "vdesktop" in self.rule_kinds:
            self.rules_changed()

    def evaluate_rules(self):
        """Use the profile of the first rule that applies, and focus mode when a rule that
        applies asks for it. A profile is only applied when the choice changes, so what you
        set by hand in between stays."""
        rules = self.rules()
        self.rule_kinds = {r["when"] for r in rules}
        # The next moment a time in a rule comes by.
        now = time.localtime()
        waits = []
        for rule in rules:
            if rule["when"] != "time":
                continue
            for moment in str(rule.get("arg", "")).split("-"):
                hours, _, minutes = moment.partition(":")
                if hours.isdigit() and minutes.isdigit():
                    wait = (int(hours) * 60 + int(minutes) - now.tm_hour * 60 - now.tm_min) % 1440
                    waits.append(wait or 1440)
        if waits:
            self.rules_clock.start((min(waits) * 60 - now.tm_sec + 1) * 1000)
        else:
            self.rules_clock.stop()
        if not self.enabled_action.isChecked():
            return
        if self.dialog and self.dialog.changed:
            return  # you are changing settings: looked at again once they are applied
        matching = [r for r in rules if self.rule_matches(r)]
        wanted = next((r.get("name", "") for r in matching if r.get("then") == RULE_PROFILE), "")
        if not wanted and rules:
            wanted = self.settings.value("rules_else", "")
        if wanted != self.settings.value("rules_profile", ""):
            self.settings.setValue("rules_profile", wanted)
            profiles = self.profiles()
            if wanted in profiles:
                self.apply_snapshot(profiles[wanted])
        focus = any(r.get("then") == RULE_FOCUS for r in matching)
        if focus and not self.rule_focus:
            self.rule_focus = True
            self.set_focus(True)
        elif not focus and self.rule_focus:
            self.rule_focus = False
            self.set_focus(False)
        self.hold_night_light(any(r.get("then") == RULE_NIGHT_LIGHT for r in matching))

    def hold_night_light(self, off):
        """Keep Plasma's night light off for as long as a rule asks: true colours for a film
        or for photo work. KWin lets go by itself should Tidy stop without saying so."""
        if off == (self.night_cookie is not None):
            return
        kwin = QDBusInterface("org.kde.KWin", "/org/kde/KWin/NightLight",
                              "org.kde.KWin.NightLight", QDBusConnection.sessionBus())
        kwin.setTimeout(1000)
        if off:
            args = kwin.call("inhibit").arguments()
            self.night_cookie = args[0] if args and isinstance(args[0], int) else None
        else:
            cookie = QDBusArgument()
            cookie.add(self.night_cookie, QMetaType.Type.UInt.value)   # KWin wants it unsigned
            kwin.call("uninhibit", cookie)
            self.night_cookie = None

    # --- new icons in the system tray ---------------------------------------------

    @pyqtSlot(str)
    def on_tray_item(self, service):
        self.tray_new.add(service)
        self.tray_timer.start()  # a moment later: by then the icon has a name

    def check_tray_items(self):
        """Hide the icon of an application that shows one for the first time, if that is
        switched on. Which icons have been seen is always kept, so that switching it on
        later doesn't hide the ones you already had."""
        raw = self.settings.value("tray_seen", None)
        try:
            seen = set(json.loads(raw)) if raw else None
        except ValueError:
            seen = None
        rules = tray_rules(self.settings)
        # Only the applications that just came are asked who they are, and for their title
        # only when a rule needs it. (The first time ever: all of them.)
        new, self.tray_new = self.tray_new, set()
        titles = tray_app_items(only=None if seen is None else new, titles=bool(rules))
        apps = set(titles)
        default = TRAY_HIDDEN if self.settings.value("tray_hide_new", False, bool) else None
        if seen is not None and (rules or default):
            config = self.plasma.tray_config()
            shown, hidden = [], []
            for item in sorted(apps - seen):
                if item == APP or not config or item in config["shown"] + config["hidden"]:
                    continue
                # A rule for its name goes first; without one, the general choice.
                mode = tray_rule_mode(rules, item, TrayTab.label(item, titles)) or default
                if mode == TRAY_HIDDEN:
                    hidden.append(item)
                elif mode == TRAY_SHOWN:
                    shown.append(item)
            if shown or hidden:
                remember_tray(self.settings, config)
                self.plasma.set_tray_config(config["extra"], config["shown"] + shown,
                                            config["hidden"] + hidden)
        if seen is None or apps - seen:
            self.settings.setValue("tray_seen", json.dumps(sorted(apps | (seen or set()))))

    # --- profiles, export and import ------------------------------------------------

    def snapshot(self):
        """Every setting as one piece of data: for a profile or an export."""
        tray = self.plasma.tray_config()
        return {"app": APP, "version": VERSION,
                "settings": {key: self.settings.value(key, default, type(default))
                             for key, default in PROFILE_SETTINGS.items()},
                "tray": {k: tray[k] for k in ("extra", "shown", "hidden")} if tray else None,
                "drawers": [{"id": d["id"], "shortcut": d.get("shortcut", ""),
                             "config": {k: v for k, v in d["config"].items()
                                        if k not in DRAWER_STATE}}
                            for d in self.plasma.drawers()]}

    def apply_snapshot(self, data):
        """Apply settings from a profile or an import. Drawers are matched by the place they
        have in the panel's bookkeeping (their id); a drawer that isn't there is skipped."""
        self.peek(False)
        self.rule_focus = False
        self.set_focus(False)
        was_hidden, setup = self.hidden, self.hidden_setup()
        # Only what differs is written: a rule may switch profiles many times a day, and
        # most of a profile is the same as the one before it.
        old_kwin, changed = self.kwin_setup(), set()
        for key, default in PROFILE_SETTINGS.items():
            value = data.get("settings", {}).get(key)
            if isinstance(value, type(default)) and value != self.settings.value(
                    key, default, type(default)):
                self.settings.setValue(key, value)
                changed.add(key)
        tray = data.get("tray")
        parts = ("extra", "shown", "hidden")
        if isinstance(tray, dict) and all(isinstance(tray.get(k), list) for k in parts):
            current = self.plasma.tray_config()
            if current and any(tray[k] != current[k] for k in parts):
                remember_tray(self.settings, current)
                self.plasma.set_tray_config(*(tray[k] for k in parts))
        existing = {d["id"]: d for d in self.plasma.drawers()}
        backed_up = False
        for saved in data.get("drawers", []):
            now = existing.get(saved.get("id")) if isinstance(saved, dict) else None
            if not now or not isinstance(saved.get("config", {}), dict):
                continue
            config = {k: v for k, v in saved.get("config", {}).items()
                      if k in DRAWER_DEFAULTS and k not in DRAWER_STATE
                      and isinstance(v, type(DRAWER_DEFAULTS[k])) and v != now["config"][k]}
            if config:
                if not backed_up:
                    self.backup_launchers()  # before a drawer may start holding them
                    backed_up = True
                self.plasma.set_drawer_config(saved["id"], config)
            if "targets" in config or "place" in config:
                # The arrow belongs next to what it hides.
                placed = dict(now["config"], **config)
                self.plasma.place_drawer(saved["id"], placed["targets"], placed["place"])
            if isinstance(saved.get("shortcut"), str) and saved["shortcut"] != now.get("shortcut", ""):
                self.plasma.set_drawer_shortcut(saved["id"], saved["shortcut"])
        if self.kwin_setup() != old_kwin:
            self.load_kwin()
        if "use_helper" in changed:
            self.update_helpers()
        if changed & {"balloons", "task_popup", "task_close", "task_gap", "balloon_gap"}:
            self.apply_tips()
        if "peek_key" in changed:
            self.peek_key.set(self.settings.value("peek_key", ""))
        self.after_settings(was_hidden, setup)
        self.rules_changed()
        if self.dialog:
            # The window shows the old values: open it afresh, on the same tab.
            tab = self.dialog.tabs.currentIndex()
            self.dialog.reject()
            QTimer.singleShot(0, lambda: self.show_settings(tab=tab))

    def profiles(self):
        return stored(self.settings, "profiles")

    def save_profile(self, name):
        self.settings.setValue("profiles", json.dumps(dict(self.profiles(),
                                                           **{name: self.snapshot()})))

    def delete_profile(self, name):
        found = self.profiles()
        found.pop(name, None)
        self.settings.setValue("profiles", json.dumps(found))

    def apply_profile(self, name):
        data = self.profiles().get(name)
        if data:
            self.apply_snapshot(data)

    def fill_profiles_menu(self):
        self.profiles_menu.clear()
        names = sorted(self.profiles())
        for name in names:
            self.profiles_menu.addAction(name, lambda name=name: self.apply_profile(name))
        if not names:
            self.profiles_menu.addAction(tr("None yet: save one in the settings")).setEnabled(False)

    def import_snapshot(self, data):
        found = self.profiles()
        if isinstance(data.get("profiles"), dict):
            found.update(data["profiles"])
            self.settings.setValue("profiles", json.dumps(found))
        if isinstance(data.get("rules"), list):
            self.settings.setValue("rules", json.dumps(data["rules"]))
            self.settings.setValue("rules_else", str(data.get("rules_else", "")))
            self.settings.setValue("rules_profile", "")
        self.apply_snapshot(data)

    def reset_defaults(self):
        """Every setting back to how Tidy comes; the drawers keep what is in them."""
        keep = ("targets", "place")
        defaults = {k: v for k, v in DRAWER_DEFAULTS.items()
                    if k not in DRAWER_STATE and k not in keep}
        self.apply_snapshot({"settings": dict(PROFILE_SETTINGS),
                             "drawers": [{"id": d["id"], "shortcut": "", "config": defaults}
                                         for d in self.plasma.drawers()]})

    def set_autostart(self, on):
        if on:
            os.makedirs(os.path.dirname(AUTOSTART), exist_ok=True)
            with open(AUTOSTART, "w") as f:
                f.write(f"[Desktop Entry]\nType=Application\nName={APP_NAME}\n"
                        f"Exec={os.path.abspath(sys.argv[0])}\nIcon={APP_ICON}\n"
                        "X-KDE-autostart-after=panel\n")
        elif os.path.exists(AUTOSTART):
            os.remove(AUTOSTART)

    def quit(self, by_hand=False):
        """Stop. Quit from the menu leaves Plasma as it is without Tidy: drawers paused,
        balloons back. At logout (or when Tidy is restarted) the drawers are left working,
        so that nothing jumps when Tidy starts with the next session."""
        if self.dialog:
            self.dialog.reject()
        self.quitting = True
        self.peek(False)
        self.set_focus(False)
        self.stop_idle()
        self.show()
        if by_hand and not self.suspended():
            self.suspend()
        self.kwin.unload()
        self.peek_key.release()
        self.app.quit()
