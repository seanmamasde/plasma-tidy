# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""The Rules tab."""

import json

from PyQt6.QtCore import QTime, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QComboBox, QFormLayout, QHBoxLayout, QLabel, QPushButton,
                             QSizePolicy, QStackedWidget, QTimeEdit, QVBoxLayout, QWidget)

from .consts import RULE_FOCUS, RULE_NIGHT_LIGHT, RULE_PROFILE, RULE_WHEN
from .i18n import tr


class RuleRow(QWidget):
    """One rule: when something is the case, use a profile or focus mode."""

    def __init__(self, tab, rule):
        super().__init__()
        self.tab = tab
        autohide = tab.autohide
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.mark = QLabel()
        self.mark.setFixedWidth(self.fontMetrics().horizontalAdvance("✓") + 4)
        layout.addWidget(self.mark)

        self.when = QComboBox()
        for key, label in RULE_WHEN:
            self.when.addItem(tr(label), key)
        self.when.setCurrentIndex(max(0, self.when.findData(rule.get("when"))))
        layout.addWidget(self.when)

        arg = str(rule.get("arg", ""))
        self.stack = QStackedWidget()
        self.stack.addWidget(QWidget())  # nothing to choose
        # times
        page = QWidget()
        row = QHBoxLayout(page)
        row.setContentsMargins(0, 0, 0, 0)
        start, _, end = (arg if rule.get("when") == "time" else "09:00-17:00").partition("-")
        self.start = QTimeEdit(QTime.fromString(start, "HH:mm"))
        self.end = QTimeEdit(QTime.fromString(end, "HH:mm"))
        for edit in (self.start, self.end):
            edit.setDisplayFormat("HH:mm")
        row.addWidget(self.start)
        row.addWidget(QLabel(tr("and")))
        row.addWidget(self.end)
        row.addStretch()
        self.stack.addWidget(page)
        # program
        self.program = QComboBox(editable=True)
        self.program.addItems(sorted(autohide.seen_classes, key=str.lower))
        self.program.setEditText(arg if rule.get("when") == "app" else "")
        self.program.lineEdit().setPlaceholderText(tr("Program name"))
        self.program.setToolTip(tr("The list holds the programs that are open now. You can "
                                   "also type the name."))
        self.stack.addWidget(self.program)
        # virtual desktop
        self.vdesktop = QComboBox()
        names = autohide.vdesktop_names or [""]
        count = max(len(names), int(arg) if rule.get("when") == "vdesktop" and arg.isdigit() else 0)
        for number in range(1, count + 1):
            name = names[number - 1] if number <= len(names) else ""
            self.vdesktop.addItem(name or tr("Desktop {n}").format(n=number), str(number))
        if rule.get("when") == "vdesktop":
            self.vdesktop.setCurrentIndex(max(0, self.vdesktop.findData(arg)))
        self.stack.addWidget(self.vdesktop)
        # activity
        self.activity = QComboBox()
        for key, name in tab.activity_names.items():
            self.activity.addItem(name, key)
        if rule.get("when") == "activity":
            if self.activity.findData(arg) < 0 and arg:
                self.activity.addItem(arg, arg)
            self.activity.setCurrentIndex(max(0, self.activity.findData(arg)))
        self.stack.addWidget(self.activity)
        self.stack.setFixedHeight(self.when.sizeHint().height())
        layout.addWidget(self.stack, 1)
        self.pages = {"time": 1, "app": 2, "vdesktop": 3, "activity": 4}
        self.when.currentIndexChanged.connect(self.update_page)
        self.update_page()

        layout.addWidget(QLabel("→"))
        self.then = QComboBox()
        self.wanted = rule.get("then", RULE_FOCUS) + ":" + rule.get("name", "")
        layout.addWidget(self.then)

        for icon, tip, action in (("go-up", "Higher: goes before the rules below it",
                                   lambda: tab.move(self, -1)),
                                  ("go-down", "Lower", lambda: tab.move(self, 1)),
                                  ("list-remove", "Remove this rule", lambda: tab.remove(self))):
            button = QPushButton(QIcon.fromTheme(icon), "")
            button.setToolTip(tr(tip))
            button.clicked.connect(action)
            layout.addWidget(button)

    def update_page(self):
        self.stack.setCurrentIndex(self.pages.get(self.when.currentData(), 0))

    def update_programs(self):
        """Fill the list of programs anew; what was typed or chosen stays."""
        text = self.program.currentText()
        self.program.blockSignals(True)
        self.program.clear()
        self.program.addItems(sorted(self.tab.autohide.seen_classes, key=str.lower))
        self.program.setEditText(text)
        self.program.blockSignals(False)

    def fill_profiles(self, names):
        """The choices on the right: focus mode, or one of the profiles."""
        if self.then.count():
            self.wanted = self.then.currentData()
        self.then.blockSignals(True)
        self.then.clear()
        self.then.addItem(tr("Focus mode"), RULE_FOCUS + ":")
        self.then.addItem(tr("Night light off"), RULE_NIGHT_LIGHT + ":")
        kind, _, wanted = self.wanted.partition(":")
        for name in sorted(set(names) | ({wanted} if kind == RULE_PROFILE and wanted else set())):
            self.then.addItem(tr("Profile: {name}").format(name=name), RULE_PROFILE + ":" + name)
        self.then.setCurrentIndex(max(0, self.then.findData(self.wanted)))
        self.then.blockSignals(False)

    def values(self):
        when = self.when.currentData()
        arg = {"time": self.start.time().toString("HH:mm") + "-" + self.end.time().toString("HH:mm"),
               "app": self.program.currentText().strip(),
               "vdesktop": self.vdesktop.currentData() or "",
               "activity": self.activity.currentData() or ""}.get(when, "")
        kind, _, name = self.then.currentData().partition(":")
        return {"when": when, "arg": arg, "then": kind, "name": name}


class RulesTab(QWidget):
    """Tab for the rules: a profile or focus mode by itself, depending on the situation."""

    def __init__(self, autohide):
        super().__init__()
        self.autohide = autohide
        self.rows = []
        self.activity_names = autohide.activities()[0]
        layout = QVBoxLayout(self)
        intro = QLabel(tr("A rule uses one of your profiles, switches focus mode on, or keeps "
                          "the night light off, for as long as something is the case. For the "
                          "profile the highest rule that applies decides. You make profiles on "
                          "the General tab."))
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.list = QVBoxLayout()
        layout.addLayout(self.list)
        self.none = QLabel(tr("No rules yet."))
        self.none.setEnabled(False)
        layout.addWidget(self.none)

        row = QHBoxLayout()
        add = QPushButton(QIcon.fromTheme("list-add"), tr("Add a rule"))
        add.clicked.connect(lambda: self.add({"when": "battery", "then": RULE_FOCUS}, True))
        row.addWidget(add)
        row.addStretch()
        layout.addLayout(row)

        form = QFormLayout()
        self.otherwise = QComboBox()
        self.otherwise.setToolTip(tr("The profile for when no rule with a profile applies."))
        form.addRow(tr("Otherwise:"), self.otherwise)
        layout.addLayout(form)

        hint = QLabel(tr("A ✓ marks the rules that apply right now. A profile is put to use at "
                         "the moment the choice changes; what you change by hand afterwards "
                         "stays until the next change, so save it in the profile to keep it. "
                         "Rules work while Tidy is running and switched on."))
        hint.setWordWrap(True)
        hint.setEnabled(False)
        layout.addWidget(hint)
        layout.addStretch()

        for rule in autohide.rules():
            self.add(rule)
        self.fill_profiles()
        self.clock = QTimer(self, interval=1500)
        self.clock.timeout.connect(self.update_marks)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_marks()
        self.clock.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.clock.stop()

    def update_marks(self):
        for row in self.rows:
            applies = self.autohide.rule_matches(row.values())
            row.mark.setText("✓" if applies else "")
            row.mark.setToolTip(tr("Applies right now") if applies else "")

    def update_programs(self):
        for row in self.rows:
            row.update_programs()

    def fill_profiles(self):
        names = sorted(self.autohide.profiles())
        for row in self.rows:
            row.fill_profiles(names)
        wanted = (self.otherwise.currentData() if self.otherwise.count()
                  else self.autohide.settings.value("rules_else", ""))
        self.otherwise.blockSignals(True)
        self.otherwise.clear()
        self.otherwise.addItem(tr("Leave everything as it is"), "")
        for name in names:
            self.otherwise.addItem(tr("Profile: {name}").format(name=name), name)
        self.otherwise.setCurrentIndex(max(0, self.otherwise.findData(wanted)))
        self.otherwise.blockSignals(False)

    def edited(self):
        self.none.setVisible(not self.rows)
        window = self.window()
        if hasattr(window, "watch_changes"):
            window.watch_changes(self)
            window.mark_changed()

    def add(self, rule, by_hand=False):
        row = RuleRow(self, rule)
        row.fill_profiles(sorted(self.autohide.profiles()))
        self.rows.append(row)
        self.list.addWidget(row)
        self.none.setVisible(False)
        if by_hand:
            self.edited()
            self.update_marks()

    def remove(self, row):
        self.rows.remove(row)
        row.setParent(None)
        row.deleteLater()
        self.edited()

    def move(self, row, step):
        index = self.rows.index(row)
        other = index + step
        if not 0 <= other < len(self.rows):
            return
        self.rows.insert(other, self.rows.pop(index))
        self.list.removeWidget(row)
        self.list.insertWidget(other, row)
        self.edited()

    def save(self):
        settings = self.autohide.settings
        settings.setValue("rules", json.dumps([row.values() for row in self.rows]))
        settings.setValue("rules_else", self.otherwise.currentData() or "")
