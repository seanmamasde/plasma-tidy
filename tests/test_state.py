# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""What Tidy changes in Plasma and puts back: hiding and showing, focus mode, the balloons.
Tidy's real code, against a Plasma that only remembers what it is told."""

import json
import unittest
from unittest import mock

from tests import SRC  # noqa: F401
from tests.fakes import FakeTidy, Switch

import plasma_tidy.core as core
from plasma_tidy.core import Tidy


class FakePlasma:
    """A Plasma with one panel, one desktop and two drawers. `down` is Plasma restarting:
    nothing gets through and nothing comes back."""

    def __init__(self):
        self.panels = {2: "dodgewindows"}
        self.urls = {1: "desktop:/"}
        self.closed = {39: False, 40: False}
        self.drawer_config = {"taskTips": True, "balloons": True, "taskBare": False,
                              "taskClose": True, "taskGap": False, "tipGap": False}
        self.previews = {5: True}
        self.down = False
        self.reached = True
        self.order = []  # what was changed, in order

    def get(self, value):
        self.reached = not self.down
        return {} if self.down else value

    def change(self, what, do):
        self.reached = not self.down
        if not self.down:
            self.order.append(what)
            do()

    def panel_modes(self):
        return self.get(dict(self.panels))

    def set_panel_modes(self, modes):
        self.change("panels", lambda: self.panels.update({int(k): v for k, v in modes.items()}))

    def desktop_urls(self):
        return self.get(dict(self.urls))

    def set_desktop_urls(self, urls):
        self.change("urls", lambda: self.urls.update(urls))

    def desktop_screens(self):
        return {}

    def drawers(self):
        return [] if self.down else [{"id": k, "config": dict(self.drawer_config, closed=v)}
                                     for k, v in self.closed.items()]

    def set_drawers_closed(self, closed):
        self.change("drawers", lambda: self.closed.update({k: closed for k in self.closed}))

    def set_drawer_config(self, drawer_id, config):
        def do():
            for key, value in config.items():
                if key == "closed":
                    self.closed.update({k: value for k in self.closed
                                        if drawer_id in (None, k)})
                else:
                    self.drawer_config[key] = value
        self.change("drawer config", do)

    def tray_config(self):
        return None

    def task_previews(self):
        return self.get(dict(self.previews))

    def set_task_previews(self, previews):
        self.change("previews", lambda: self.previews.update(
            {int(k): v for k, v in previews.items()}))


class StateTidy(FakeTidy):
    """Tidy with its own hiding, showing and focus mode."""
    show, hide, set_focus = Tidy.show, Tidy.hide, Tidy.set_focus

    def __init__(self, **settings):
        super().__init__(**dict({"use_helper": False}, **settings))
        self.plasma = FakePlasma()
        self.focus_action = mock.Mock()
        self.tray = None
        self.saved_before_change = None
        self.peek_state = None

    def hide_catchers(self):
        pass

    def show_catchers(self):
        pass

    def update_icon(self):
        pass

    def send_state(self):
        pass

    def peek(self, on):
        pass

    @property
    def saved(self):
        return json.loads(self.settings.value("saved_state", "") or "{}")


class HideAndShow(unittest.TestCase):
    def test_everything_is_back_after_hiding_and_showing(self):
        tidy = StateTidy(hide_panel=True, drawer_follow=True)
        tidy.hide()
        self.assertTrue(tidy.hidden)
        self.assertEqual(tidy.plasma.panels, {2: "autohide"})
        self.assertNotEqual(tidy.plasma.urls[1], "desktop:/")
        self.assertEqual(tidy.plasma.closed, {39: True, 40: True})
        tidy.show()
        self.assertFalse(tidy.hidden)
        self.assertEqual(tidy.plasma.panels, {2: "dodgewindows"})
        self.assertEqual(tidy.plasma.urls, {1: "desktop:/"})
        self.assertEqual(tidy.plasma.closed, {39: False, 40: False})
        self.assertEqual(tidy.saved, {})

    def test_what_was_there_is_saved_before_anything_changes(self):
        tidy = StateTidy(hide_panel=True)
        seen = []
        change = tidy.plasma.change
        tidy.plasma.change = lambda what, do: (seen.append(dict(tidy.saved)), change(what, do))
        tidy.hide()
        self.assertTrue(seen)
        for saved in seen:
            self.assertEqual(saved.get("panels"), {"2": "dodgewindows"})

    def test_hiding_twice_notes_the_original_only(self):
        tidy = StateTidy(hide_panel=True)
        tidy.hide()
        tidy.hide()
        self.assertEqual(tidy.saved["panels"], {"2": "dodgewindows"})

    def test_plasma_away_while_showing_keeps_what_was_saved(self):
        tidy = StateTidy(hide_panel=True)
        tidy.hide()
        tidy.plasma.down = True
        tidy.show()
        self.assertEqual(tidy.saved["panels"], {"2": "dodgewindows"})
        # Hiding again before Plasma is back must not note the hidden state as the original.
        tidy.hide()
        self.assertEqual(tidy.saved["panels"], {"2": "dodgewindows"})
        tidy.plasma.down = False
        tidy.show()
        self.assertEqual(tidy.plasma.panels, {2: "dodgewindows"})
        self.assertEqual(tidy.plasma.urls, {1: "desktop:/"})
        self.assertEqual(tidy.saved, {})

    def test_a_broken_note_does_not_stop_tidy(self):
        tidy = StateTidy()
        tidy.settings.setValue("saved_state", "{not json")
        tidy.show()
        self.assertEqual(tidy.saved, {})

    def test_with_hide_after_never_a_shortcut_still_hides(self):
        tidy = StateTidy(timeout=0)
        tidy.hide()   # what --hide and the shortcut do
        self.assertTrue(tidy.hidden)
        self.assertNotEqual(tidy.plasma.urls[1], "desktop:/")


class ShowDesktop(unittest.TestCase):
    """Show desktop (Meta+D) brings the icons back, unless that is switched off."""

    def hidden(self, **settings):
        tidy = StateTidy(**settings)
        tidy.hide()
        tidy.on_showing_desktop(True)
        return tidy

    def test_it_brings_them_back(self):
        tidy = self.hidden()
        self.assertFalse(tidy.hidden)
        self.assertEqual(tidy.plasma.urls, {1: "desktop:/"})

    def test_switched_off_they_stay_away(self):
        tidy = self.hidden(desktop_shows=False)
        self.assertTrue(tidy.hidden)
        self.assertNotEqual(tidy.plasma.urls[1], "desktop:/")


class FocusMode(unittest.TestCase):
    def tidy(self, **settings):
        tidy = StateTidy(**dict({"hide_panel": True, "drawer_follow": True, "focus_panel": True,
                                 "focus_tray": False}, **settings))
        tidy.restore_focus_state = lambda: Tidy.restore_focus_state(tidy)
        return tidy

    def test_on_and_off_puts_everything_back(self):
        tidy = self.tidy()
        tidy.set_focus(True)
        self.assertEqual(tidy.plasma.panels, {2: "autohide"})
        self.assertEqual(tidy.plasma.closed, {39: True, 40: True})
        tidy.set_focus(False)
        self.assertEqual(tidy.plasma.panels, {2: "dodgewindows"})
        self.assertEqual(tidy.plasma.closed, {39: False, 40: False})

    def test_switched_on_while_the_icons_are_hidden(self):
        tidy = self.tidy()
        tidy.hide()
        tidy.set_focus(True)
        tidy.set_focus(False)
        self.assertEqual(tidy.plasma.panels, {2: "dodgewindows"})
        self.assertEqual(tidy.plasma.closed, {39: False, 40: False})
        self.assertEqual(tidy.plasma.urls, {1: "desktop:/"})


class Balloons(unittest.TestCase):
    def setUp(self):
        self.on = True
        patches = [mock.patch.object(core, "plasma_balloons", lambda: self.on),
                   mock.patch.object(core, "set_plasma_balloons",
                                     lambda on: setattr(self, "on", on))]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.tidy = StateTidy()

    def choose(self, **settings):
        for key, value in settings.items():
            self.tidy.settings.setValue(key, value)
        self.tidy.apply_tips()
        return self.tidy.plasma.drawer_config

    def test_nothing_chosen_changes_nothing(self):
        self.choose()
        self.assertEqual(self.tidy.plasma.order, [])
        self.assertEqual(self.tidy.settings.value("tips_original", ""), "")

    def test_each_choice_reaches_plasma_and_the_drawers(self):
        config = self.choose(balloons=False, task_popup="only", task_gap=True, balloon_gap=True)
        self.assertFalse(self.on)
        self.assertEqual(self.tidy.plasma.previews, {5: True})
        self.assertEqual((config["balloons"], config["taskBare"], config["taskTips"],
                          config["taskGap"], config["tipGap"]), (False, True, True, True, True))
        config = self.choose(task_popup="text")
        self.assertEqual(self.tidy.plasma.previews, {5: False})
        self.assertFalse(config["taskBare"])
        config = self.choose(task_popup="none")
        self.assertFalse(config["taskTips"])

    def test_the_original_is_noted_once_and_put_back(self):
        self.choose(balloons=False, task_popup="text")
        self.choose(task_popup="none")
        self.assertEqual(json.loads(self.tidy.settings.value("tips_original")),
                         {"balloons": True, "previews": {"5": True}})
        self.tidy.restore_tips()
        self.assertTrue(self.on)
        self.assertEqual(self.tidy.plasma.previews, {5: True})
        self.assertEqual(self.tidy.settings.value("tips_original", ""), "")
        config = self.tidy.plasma.drawer_config
        self.assertEqual((config["taskTips"], config["balloons"], config["taskBare"]),
                         (True, True, False))


class OffAndQuit(unittest.TestCase):
    """Tidy switched off, or quit by hand: Plasma as it is without Tidy. On again: as set."""

    def setUp(self):
        self.on = True
        for patch in (mock.patch.object(core, "plasma_balloons", lambda: self.on),
                      mock.patch.object(core, "set_plasma_balloons",
                                        lambda on: setattr(self, "on", on))):
            patch.start()
            self.addCleanup(patch.stop)
        self.tidy = StateTidy(balloons=False, task_popup="text")
        self.tidy.update_icon = self.tidy.rules_changed = self.tidy.stop_idle = lambda: None
        self.tidy.app = self.tidy.kwin = self.tidy.peek_key = mock.Mock()
        self.tidy.apply_tips()
        self.plasma = self.tidy.plasma

    def as_set(self):
        return (self.on, self.plasma.previews, self.plasma.drawer_config.get("paused", False))

    def test_as_set_in_tidy(self):
        self.assertEqual(self.as_set(), (False, {5: False}, False))

    def test_switched_off_and_on(self):
        self.tidy.set_enabled(False)
        self.assertEqual(self.as_set(), (True, {5: True}, True))
        self.assertFalse(self.tidy.settings.value("balloons"))   # Tidy's own choice stays
        self.tidy.apply_tips()                                    # the settings window, while off
        self.assertEqual(self.as_set(), (True, {5: True}, True))
        self.tidy.set_enabled(True)
        self.assertEqual(self.as_set(), (False, {5: False}, False))

    def test_quit_by_hand_leaves_plasma_as_without_tidy(self):
        self.tidy.quit(by_hand=True)
        self.assertEqual(self.as_set(), (True, {5: True}, True))
        self.assertTrue(self.tidy.suspended())

    def test_stopped_at_logout_leaves_the_drawers_working(self):
        self.tidy.quit()
        self.assertEqual(self.as_set(), (False, {5: False}, False))
        self.assertFalse(self.tidy.suspended())


class Profiles(unittest.TestCase):
    """Switching to a profile writes what differs, and nothing else."""

    def setUp(self):
        self.tidy = StateTidy(timeout=10, corner="none")
        self.tidy.apply_snapshot = lambda data: Tidy.apply_snapshot(self.tidy, data)
        self.tidy.kwin = mock.Mock()
        self.tidy.peek_key = mock.Mock()
        self.tidy.backup_launchers = mock.Mock()
        self.tidy.update_helpers = mock.Mock()
        self.tidy.after_settings = mock.Mock()
        self.tidy.rules_changed = mock.Mock()
        self.tidy.plasma.set_drawer_shortcut = mock.Mock()
        self.tidy.plasma.place_drawer = mock.Mock()
        patch = mock.patch.object(core, "plasma_balloons", lambda: True)
        patch.start()
        self.addCleanup(patch.stop)

    def same(self):
        drawers = [{"id": d["id"], "shortcut": "", "config": d["config"]}
                   for d in self.tidy.plasma.drawers()]
        return {"settings": {"timeout": 10, "corner": "none"}, "drawers": drawers}

    def test_the_same_profile_again_touches_nothing(self):
        self.tidy.apply_snapshot(self.same())
        self.assertEqual(self.tidy.plasma.order, [])
        self.tidy.kwin.load.assert_not_called()
        self.tidy.update_helpers.assert_not_called()
        self.tidy.peek_key.set.assert_not_called()
        self.tidy.plasma.set_drawer_shortcut.assert_not_called()

    def test_only_the_difference_is_written(self):
        data = self.same()
        data["settings"]["timeout"] = 30
        data["settings"]["corner"] = "topleft"
        data["drawers"][0]["config"] = dict(data["drawers"][0]["config"], taskClose=False,
                                            autoClose=False)
        self.tidy.plasma.drawer_config["autoClose"] = True
        self.tidy.apply_snapshot(data)
        self.assertEqual(self.tidy.settings.value("timeout"), 30)
        self.assertEqual(self.tidy.plasma.order, ["drawer config"])  # taskClose is not a setting of a profile
        self.assertIs(self.tidy.plasma.drawer_config["autoClose"], False)
        self.assertIs(self.tidy.plasma.drawer_config["taskClose"], True)
        self.tidy.kwin.load.assert_called_once()   # the corner is KWin's work
        self.tidy.plasma.place_drawer.assert_not_called()

    def test_never_and_show_desktop_off_go_along(self):
        data = self.same()
        data["settings"].update(timeout=0, desktop_shows=False)
        self.tidy.apply_snapshot(data)
        self.assertEqual(self.tidy.settings.value("timeout"), 0)
        self.assertIs(self.tidy.settings.value("desktop_shows"), False)

    def test_a_file_with_nonsense_in_it_is_taken_as_far_as_it_makes_sense(self):
        self.tidy.apply_snapshot({"settings": {"timeout": "soon"}, "tray": "yes",
                                  "drawers": ["x", {"id": 39, "config": "none"},
                                              {"id": 99, "config": {}}, {"config": {}}]})
        self.assertEqual(self.tidy.settings.value("timeout"), 10)
        self.assertEqual(self.tidy.plasma.order, [])


if __name__ == "__main__":
    unittest.main()
