# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""A stand-in for the running program: Tidy's own logic, with everything it would touch
outside itself (Plasma, KWin, timers, the settings file) replaced by something harmless."""

import time
import types

from tests import SRC  # noqa: F401  (sets the path to the code)

from plasma_tidy.core import Tidy


class Settings:
    """Settings kept in memory."""

    def __init__(self, values):
        self.values = dict(values)

    def value(self, key, default=None, kind=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value

    def remove(self, key):
        self.values.pop(key, None)

    def sync(self):
        pass


class Recorder:
    """Takes any call and remembers it; answers with nothing."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def call(*args, **kwargs):
            self.calls.append((name, args))
            return {}
        return call


class Clock:
    """A timer that only remembers what it was asked."""

    def __init__(self):
        self.interval = None

    def start(self, interval=None):
        self.interval = interval if interval is not None else 0

    def stop(self):
        self.interval = None


class Switch:
    def __init__(self, on=True):
        self.on = on

    def isChecked(self):
        return self.on


class FakeTidy:
    def __init__(self, **settings):
        base = {"mode": "click", "rehide": "idle", "only_desktop": True, "timeout": 5}
        self.settings = Settings(dict(base, **settings))
        self.plasma = Recorder()
        self.enabled_action = Switch()
        self.hide_timer, self.rules_timer, self.rules_clock = Clock(), Clock(), Clock()
        self.hidden = False
        self.idle_since = None
        self.shown_at = time.monotonic()
        self.desktop_active = True
        self.popup_open = self.showing_desktop = False
        self.focus = self.hold_icons = self.peeking = self.quitting = False
        self.rule_focus = False
        self.night_cookie = None
        self.night_light = []
        self.rule_kinds = set()
        self.active_class, self.active_fullscreen = "", False
        self.seen_classes, self.vdesktop, self.vdesktop_names = set(), 1, []
        self.dialog = self.idle = None
        self.shown = self.hidden_times = 0
        self.helpers, self.helper_count, self.hidden_by_helper = set(), 0, False
        self.told = []
        self.battery = False
        self.applied = []

    # What would reach outside, made harmless.
    def show(self):
        self.shown += 1
        self.hidden = False

    def hide(self):
        self.hidden_times += 1
        self.hidden = True

    def tell(self, signal, *args):
        self.told.append((signal, args))

    def skipped_screens(self):
        return set()

    def schedule(self):
        pass

    def update_idle(self):
        pass

    def on_battery(self):
        return self.battery

    def profiles(self):
        return {"Work": {"name": "Work"}, "Home": {"name": "Home"}}

    def apply_snapshot(self, data):
        self.applied.append(data["name"])

    def set_focus(self, on):
        self.focus = on

    def hold_night_light(self, off):
        if off != (self.night_cookie is not None):
            self.night_light.append(off)
            self.night_cookie = 1 if off else None

    def busy(self):
        return False


# Everything else is Tidy's own code.
for _name, _value in vars(Tidy).items():
    if isinstance(_value, types.FunctionType) and _name not in vars(FakeTidy):
        setattr(FakeTidy, _name, _value)
