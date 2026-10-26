# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""The window shown the first time Tidy starts."""

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QHBoxLayout, QLabel, QSpinBox, QVBoxLayout)

from .consts import APP, APP_ICON, APP_NAME, MODE_ACTIVITY, MODE_CLICK, TASK_PLUGINS
from .i18n import tr
from .tray import remember_tray, tray_app_items, tray_minimal
from .widgets import install_drawer, new_drawer


class Welcome(QDialog):
    """Shown the first time Tidy starts: the few choices that matter most."""

    def __init__(self, autohide):
        super().__init__()
        self.autohide = autohide
        settings = autohide.settings
        self.setWindowTitle(tr("Welcome to {app}").format(app=APP_NAME))
        self.setWindowIcon(QIcon.fromTheme(APP_ICON, QIcon.fromTheme("view-visible")))
        layout = QVBoxLayout(self)

        head = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(QIcon.fromTheme(APP_ICON, QIcon.fromTheme("view-visible")).pixmap(48, 48))
        head.addWidget(icon)
        title = QLabel(tr("Welcome to {app}").format(app=APP_NAME))
        font = title.font()
        font.setPointSizeF(font.pointSizeF() * 1.5)
        font.setBold(True)
        title.setFont(font)
        head.addWidget(title, 1)
        layout.addLayout(head)

        intro = QLabel(tr("{app} keeps your desktop clean. It hides the desktop icons when you "
                          "don't need them and brings them back when you do. A few choices to "
                          "start with; everything can be changed later.").format(app=APP_NAME))
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self.timeout = QSpinBox(suffix=" s", minimum=0, maximum=3600)
        self.timeout.setSpecialValueText(tr("Never"))
        self.timeout.setValue(settings.value("timeout", 10, int))
        form.addRow(tr("Hide the icons after:"), self.timeout)
        self.mode = QComboBox()
        self.mode.addItem(tr("On any mouse movement or key press"), MODE_ACTIVITY)
        self.mode.addItem(tr("On a click on the desktop"), MODE_CLICK)
        self.mode.setCurrentIndex(max(0, self.mode.findData(settings.value("mode", MODE_ACTIVITY))))
        form.addRow(tr("The icons come back:"), self.mode)
        self.autostart = QCheckBox(tr("Start at login"))
        self.autostart.setChecked(True)
        form.addRow(self.autostart)
        layout.addLayout(form)

        # The two things you would not find by yourself. They change the panel, so they are
        # offered, not done.
        also = QLabel(tr("{app} can also tidy your panel:").format(app=APP_NAME))
        layout.addWidget(also)
        self.drawer_spot = self.find_drawer_spot()
        self.drawer = QCheckBox(tr("Add a drawer for the programs in the panel"))
        self.drawer.setToolTip(tr("Puts an arrow next to the task manager. A click on it tucks "
                                  "the program icons away, and brings them back."))
        if not self.drawer_spot:
            self.drawer.setEnabled(False)
            self.drawer.setToolTip(tr("There is one already, or the panel has no task manager."))
        layout.addWidget(self.drawer)
        self.tray = QCheckBox(tr("Tidy the system tray"))
        self.tray.setToolTip(tr("Only network, volume and battery stay in view, and Tidy's own "
                                "icon; the rest goes under the ^ arrow."))
        self.tray.setEnabled(autohide.plasma.tray_config() is not None)
        layout.addWidget(self.tray)

        more = QLabel(tr("There is more in the settings: focus mode, rules, profiles and a key "
                         "to peek. {app} lives in the system tray: click its icon to open "
                         "the settings.")
                      .format(app=APP_NAME))
        more.setWordWrap(True)
        more.setEnabled(False)
        layout.addWidget(more)

        buttons = QDialogButtonBox()
        start = buttons.addButton(tr("Start"), QDialogButtonBox.ButtonRole.AcceptRole)
        start.setDefault(True)
        settings_button = buttons.addButton(tr("More settings…"),
                                            QDialogButtonBox.ButtonRole.ActionRole)
        buttons.accepted.connect(self.accept)
        settings_button.clicked.connect(self.open_settings)
        layout.addWidget(buttons)

    def find_drawer_spot(self):
        """Where a first drawer would go: (panel id, [task manager ids]) for a task manager
        that no drawer holds yet, or None."""
        plasma = self.autohide.plasma
        taken = {i for d in plasma.drawers() for i in d["config"]["targets"]}
        for panel in plasma.panel_widgets():
            targets = [str(w["id"]) for w in panel["widgets"]
                       if w["type"] in TASK_PLUGINS and str(w["id"]) not in taken]
            if targets:
                return panel["panel"], targets
        return None

    def save(self):
        a = self.autohide
        a.settings.setValue("timeout", self.timeout.value())
        a.settings.setValue("mode", self.mode.currentData())
        a.set_autostart(self.autostart.isChecked())
        if self.drawer.isChecked() and self.drawer_spot:
            panel, targets = self.drawer_spot
            a.backup_launchers()  # before a drawer may start holding them
            install_drawer()
            # Closed from the start: tidying the panel is what was asked for.
            a.plasma.add_drawer(panel, new_drawer(targets, closed=True))
        tray = a.plasma.tray_config() if self.tray.isChecked() else None
        if tray:
            remember_tray(a.settings, tray)
            extra, shown, hidden = tray_minimal(tray, tray_app_items())
            # Tidy's own icon stays in view: it is the way to the settings.
            hidden = [i for i in hidden if i != APP]
            a.plasma.set_tray_config(extra, shown + ([] if APP in shown else [APP]), hidden)
        a.after_settings(a.hidden, a.hidden_setup())

    def accept(self):
        self.save()
        super().accept()

    def open_settings(self):
        self.accept()
        QTimer.singleShot(0, self.autohide.show_settings)
