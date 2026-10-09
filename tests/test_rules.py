# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rules: which profile is used, and when focus mode goes on and off."""

import json
import unittest

from tests.fakes import FakeTidy


def fake(rules, **settings):
    return FakeTidy(rules=json.dumps(rules), **settings)


class Profiles(unittest.TestCase):
    RULES = [{"when": "app", "arg": "Firefox", "then": "profile", "name": "Home"},
             {"when": "battery", "then": "profile", "name": "Work"}]

    def test_nothing_applies(self):
        tidy = fake(self.RULES)
        tidy.evaluate_rules()
        self.assertEqual(tidy.applied, [])

    def test_a_profile_is_applied_once(self):
        tidy = fake(self.RULES)
        tidy.battery = True
        tidy.evaluate_rules()
        tidy.evaluate_rules()
        self.assertEqual(tidy.applied, ["Work"])

    def test_the_highest_rule_decides(self):
        tidy = fake(self.RULES)
        tidy.battery = True
        tidy.on_active_window("firefox", False)
        tidy.evaluate_rules()
        self.assertEqual(tidy.applied, ["Home"])

    def test_back_to_the_lower_rule(self):
        tidy = fake(self.RULES)
        tidy.battery = True
        tidy.on_active_window("firefox", False)
        tidy.evaluate_rules()
        tidy.on_active_window("dolphin", False)
        tidy.evaluate_rules()
        self.assertEqual(tidy.applied, ["Home", "Work"])

    def test_otherwise(self):
        tidy = fake(self.RULES, rules_else="Home")
        tidy.evaluate_rules()
        tidy.battery = True
        tidy.evaluate_rules()
        tidy.battery = False
        tidy.evaluate_rules()
        self.assertEqual(tidy.applied, ["Home", "Work", "Home"])

    def test_a_profile_that_is_gone_is_skipped(self):
        tidy = fake([{"when": "battery", "then": "profile", "name": "Gone"}])
        tidy.battery = True
        tidy.evaluate_rules()
        self.assertEqual(tidy.applied, [])

    def test_waits_while_you_change_settings(self):
        tidy = fake(self.RULES)
        tidy.battery = True
        tidy.dialog = type("Dialog", (), {"changed": True})()
        tidy.evaluate_rules()
        self.assertEqual(tidy.applied, [])

    def test_does_nothing_while_switched_off(self):
        tidy = fake(self.RULES)
        tidy.battery = True
        tidy.enabled_action.on = False
        tidy.evaluate_rules()
        self.assertEqual(tidy.applied, [])


class NightLight(unittest.TestCase):
    RULES = [{"when": "app", "arg": "mpc-qt", "then": "nightlight"}]

    def test_off_while_the_program_is_in_front_and_back_after(self):
        tidy = fake(self.RULES)
        tidy.on_active_window("mpc-qt", False)
        tidy.evaluate_rules()
        tidy.evaluate_rules()                    # asked once, however often it is looked at
        self.assertEqual(tidy.night_light, [True])
        tidy.on_active_window("dolphin", False)
        tidy.evaluate_rules()
        self.assertEqual(tidy.night_light, [True, False])

    def test_it_leaves_the_profile_and_focus_mode_alone(self):
        tidy = fake(self.RULES)
        tidy.on_active_window("mpc-qt", False)
        tidy.evaluate_rules()
        self.assertFalse(tidy.focus)
        self.assertEqual(tidy.applied, [])


class FocusMode(unittest.TestCase):
    RULES = [{"when": "fullscreen", "then": "focus"}, {"when": "vdesktop", "arg": "2", "then": "focus"}]

    def test_on_while_a_rule_applies(self):
        tidy = fake(self.RULES)
        tidy.on_active_window("mpv", True)
        tidy.evaluate_rules()
        self.assertTrue(tidy.focus)
        tidy.on_active_window("mpv", False)
        tidy.evaluate_rules()
        self.assertFalse(tidy.focus)

    def test_switched_off_by_hand_stays_off(self):
        tidy = fake(self.RULES)
        tidy.on_active_window("mpv", True)
        tidy.evaluate_rules()
        tidy.focus = False
        tidy.evaluate_rules()
        self.assertFalse(tidy.focus)

    def test_virtual_desktop(self):
        tidy = fake(self.RULES)
        tidy.evaluate_rules()
        tidy.on_virtual_desktop(2, ["One", "Two"])
        tidy.evaluate_rules()
        self.assertTrue(tidy.focus)
        tidy.on_virtual_desktop(1, ["One", "Two"])
        tidy.evaluate_rules()
        self.assertFalse(tidy.focus)


class Times(unittest.TestCase):
    def matches(self, span, now):
        import time as real
        tidy = fake([])
        original = real.strftime
        real.strftime = lambda fmt, *a: now if fmt == "%H:%M" else original(fmt, *a)
        try:
            return tidy.rule_matches({"when": "time", "arg": span})
        finally:
            real.strftime = original

    def test_within_the_day(self):
        self.assertTrue(self.matches("09:00-17:00", "09:00"))
        self.assertTrue(self.matches("09:00-17:00", "16:59"))
        self.assertFalse(self.matches("09:00-17:00", "17:00"))

    def test_across_midnight(self):
        self.assertTrue(self.matches("22:00-07:00", "23:10"))
        self.assertTrue(self.matches("22:00-07:00", "06:59"))
        self.assertFalse(self.matches("22:00-07:00", "07:00"))
        self.assertFalse(self.matches("22:00-07:00", "12:00"))

    def test_the_clock_is_set_for_the_next_moment(self):
        tidy = fake([{"when": "time", "arg": "22:00-07:00", "then": "focus"}])
        tidy.evaluate_rules()
        self.assertTrue(0 < tidy.rules_clock.interval <= 24 * 3600 * 1000)

    def test_no_clock_without_a_time_rule(self):
        tidy = fake([{"when": "battery", "then": "focus"}])
        tidy.evaluate_rules()
        self.assertIsNone(tidy.rules_clock.interval)


if __name__ == "__main__":
    unittest.main()
