# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Searching the settings window: what is found, and where it says it is."""

import unittest

from tests import SRC  # noqa: F401

from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout, QGroupBox,
                             QStackedWidget, QTabWidget, QVBoxLayout, QWidget)

from plasma_tidy.search import SEPARATOR, entries

app = QApplication.instance() or QApplication([])


class Search(unittest.TestCase):
    def setUp(self):
        self.top = QWidget()
        outer = QVBoxLayout(self.top)
        self.tabs = QTabWidget()
        outer.addWidget(self.tabs)
        page = QWidget()
        layout = QVBoxLayout(page)
        box = QGroupBox("How they come back")
        self.form = QFormLayout(box)
        self.back = QComboBox()
        self.back.addItems(["On a click", "On a double-click"])
        self.form.addRow("The icons come back:", self.back)
        self.corner = QComboBox()
        self.form.addRow("Screen corner shows:", self.corner)
        layout.addWidget(box)
        self.fade = QCheckBox("Fade the icons")
        layout.addWidget(self.fade)
        self.tabs.addTab(page, "Desktop")
        # two drawers, of which one is in view
        drawers = QWidget()
        self.stack = QStackedWidget()
        QVBoxLayout(drawers).addWidget(self.stack)
        for name in ("left", "right"):
            drawer = QWidget()
            QVBoxLayout(drawer).addWidget(QCheckBox(f"Open on attention ({name})"))
            self.stack.addWidget(drawer)
        self.tabs.addTab(drawers, "Drawers")

    def shown(self):
        return [text for text, _widget, _steps in entries(self.top)]

    def test_a_row_is_found_with_its_tab_and_group(self):
        self.assertIn("The icons come back" + SEPARATOR + "Desktop › How they come back",
                      self.shown())

    def test_the_choices_of_a_list_are_found_too(self):
        self.assertIn("On a double-click" + SEPARATOR
                      + "Desktop › How they come back › The icons come back", self.shown())

    def test_a_tick_box_outside_a_group(self):
        self.assertIn("Fade the icons" + SEPARATOR + "Desktop", self.shown())

    def test_only_the_drawer_in_view(self):
        found = [t for t in self.shown() if t.startswith("Open on attention")]
        self.assertEqual(found, ["Open on attention (left)" + SEPARATOR + "Drawers"])
        self.stack.setCurrentIndex(1)
        found = [t for t in self.shown() if t.startswith("Open on attention")]
        self.assertEqual(found, ["Open on attention (right)" + SEPARATOR + "Drawers"])

    def test_a_row_that_is_out_of_sight_is_not_offered(self):
        self.form.setRowVisible(self.corner, False)
        self.assertFalse([t for t in self.shown() if t.startswith("Screen corner")])

    def test_the_steps_lead_to_the_tab(self):
        steps = {text: s for text, _w, s in entries(self.top)}
        self.assertEqual(steps["Fade the icons" + SEPARATOR + "Desktop"], [(self.tabs, 0)])


if __name__ == "__main__":
    unittest.main()
