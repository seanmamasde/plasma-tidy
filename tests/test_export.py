# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every setting as one piece of text for another program, and the way back in."""

import json
import unittest

from tests import SRC  # noqa: F401
from tests.fakes import FakeTidy

from plasma_tidy.consts import APP


class Plasma:
    """Just enough of Plasma: it answers or it does not, and holds one tray."""

    def __init__(self, reached=True):
        self.reached = reached
        self.tray = {"extra": ["a"], "shown": ["b"], "hidden": ["c"]}

    def tray_config(self):
        return dict(self.tray)

    def drawers(self):
        return []

    def run(self, _script):
        return ""


def tidy(**settings):
    t = FakeTidy(**settings)
    t.plasma = Plasma()
    t.imported = []
    t.import_snapshot = t.imported.append
    return t


class Export(unittest.TestCase):
    def test_it_holds_the_settings_the_rules_and_the_profiles(self):
        t = tidy(rules=json.dumps([{"when": "battery", "then": "focus"}]), rules_else="Home")
        data = t.export_data()
        self.assertEqual(data["app"], APP)
        self.assertEqual(data["settings"]["timeout"], 5)
        self.assertEqual(data["rules"], [{"when": "battery", "then": "focus"}])
        self.assertEqual(data["rules_else"], "Home")
        self.assertEqual(set(data["profiles"]), {"Work", "Home"})

    def test_in_focus_mode_the_tray_is_told_as_it_was_before(self):
        before = {"extra": ["x"], "shown": ["y"], "hidden": ["z"]}
        t = tidy(focus_state=json.dumps({"tray": before}))
        t.focus = True
        self.assertEqual(t.export_data()["tray"], before)
        t.focus = False
        self.assertEqual(t.export_data()["tray"], t.plasma.tray)


class Import(unittest.TestCase):
    def test_what_was_exported_goes_back_in(self):
        t = tidy()
        self.assertEqual(t.import_text(json.dumps(t.export_data())), "")
        self.assertEqual(len(t.imported), 1)

    def test_something_else_is_refused_in_words(self):
        t = tidy()
        self.assertIn("JSON", t.import_text("{not json"))
        self.assertIn("Tidy settings", t.import_text(json.dumps({"app": "other"})))
        self.assertIn("Tidy settings", t.import_text("[1, 2]"))
        self.assertEqual(t.imported, [])

    def test_not_while_plasma_does_not_answer(self):
        t = tidy()
        text = json.dumps(t.export_data())
        t.plasma.reached = False
        self.assertIn("Plasma does not answer", t.import_text(text))
        self.assertEqual(t.imported, [])

    def test_not_over_changes_in_the_open_settings_window(self):
        t = tidy()
        text = json.dumps(t.export_data())
        t.dialog = type("Dialog", (), {"changed": True})()
        self.assertIn("settings window", t.import_text(text))
        self.assertEqual(t.imported, [])


if __name__ == "__main__":
    unittest.main()
