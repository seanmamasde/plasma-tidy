# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""The Drawers tab: the settings of the drawers."""

import json
import os

from PyQt6.QtCore import QSize, Qt, QUrl
from PyQt6.QtGui import QIcon, QKeySequence
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout,
                             QFrame, QGridLayout, QGroupBox, QHBoxLayout, QKeySequenceEdit,
                             QLabel, QLineEdit, QMenu, QMessageBox, QPushButton, QScrollArea,
                             QSizePolicy, QSpinBox, QStackedWidget, QTabWidget, QVBoxLayout,
                             QWidget)

from .consts import (ACTIVE_PLACES, ANIMATIONS, APP_NAME, DISPLAYS, DISPLAY_POPUP, DRAWER_SKIP,
                     FOLDER_PLUGIN, ICON_STYLES, MARK_ATTENTION, MARK_COUNT, MARK_NONE,
                     MARK_OPEN, MOVE_STYLES, OPEN_CLICK, OPEN_HOVER, PANEL_CLICKS, PANEL_PLACES,
                     PLACE_AFTER, PLACE_BEFORE, PLACE_MANUAL, POPUP_PLACES, POPUP_STYLES, SCOPE_DRAWER,
                     SCOPE_PANEL, TASKS_ALL, TASKS_PINNED, TASK_PLUGINS, TASK_POPUPS,
                     TRAY_ARROWS)
from .i18n import tr
from .plasma import app_icon, panel_widget_name, plasma_balloons
from .widgets import install_drawer, new_drawer


class DrawerPage(QWidget):
    """The settings of one drawer, in three parts: what is in it, how it opens and closes,
    and what its arrow looks like."""

    def __init__(self, drawer, widgets, number, on_label=None, fit=False, folders=None):
        super().__init__()
        self.drawer = drawer
        self.fit = fit            # its panel is as long as its contents
        self.number = number
        self.panel_name = ""      # which panel it is in, when there are several
        self.on_label = on_label  # called when the name to show for this drawer changes
        self.targets = {}
        config = drawer["config"]
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        row = QHBoxLayout()
        row.addWidget(QLabel(tr("Name:")))
        self.name = QLineEdit(config["name"])
        self.name.setToolTip(tr("A name of your own for this drawer. Without one it is called "
                                "after what is in it."))
        self.name.textChanged.connect(self.relabel)
        row.addWidget(self.name, 1)
        outer.addLayout(row)

        if self.fit:
            note = QLabel(tr("This panel is as long as its contents: it changes size when a "
                             "drawer opens. Showing the contents in a pop-up (Appearance) keeps "
                             "the panel still."))
            note.setWordWrap(True)
            note.setEnabled(False)
            outer.addWidget(note)

        parts = QTabWidget()
        outer.addWidget(parts)

        # --- contents ---
        page = QWidget()
        form = QFormLayout(page)
        box = QGroupBox(tr("In this drawer"))
        box_layout = QVBoxLayout(box)
        for widget in widgets:
            if widget["type"] in DRAWER_SKIP:
                continue
            check = QCheckBox(panel_widget_name(widget["type"], widget.get("url", "")))
            check.setChecked(str(widget["id"]) in config["targets"])
            check.toggled.connect(self.update_enabled)
            check.toggled.connect(self.relabel)
            self.targets[widget["id"]] = (check, widget["type"])
            if widget["type"] == FOLDER_PLUGIN and folders:
                # A folder was put in the panel for a drawer: it can go from here as well.
                line = QHBoxLayout()
                line.addWidget(check, 1)
                more = QPushButton(QIcon.fromTheme("configure"), "")
                more.setFlat(True)
                more.setToolTip(tr("Settings of this folder: its icon, title, sorting and more"))
                more.clicked.connect(lambda _=False, i=widget["id"]: folders.configure_folder(self, i))
                line.addWidget(more)
                gone = QPushButton(QIcon.fromTheme("list-remove"), "")
                gone.setFlat(True)
                gone.setToolTip(tr("Take this folder out of the panel"))
                gone.clicked.connect(lambda _=False, i=widget["id"]: folders.remove_folder(self, i))
                line.addWidget(gone)
                box_layout.addLayout(line)
            else:
                box_layout.addWidget(check)
        if folders:
            add = QPushButton(QIcon.fromTheme("folder-new"), tr("Add a folder…"))
            add.setToolTip(tr("Puts a folder in the panel, in this drawer: a click on it shows "
                              "what is in the folder. It is Plasma's own Folder View widget."))
            add.clicked.connect(lambda: folders.add_folder(self))
            line = QHBoxLayout()
            line.addWidget(add)
            line.addStretch()
            box_layout.addLayout(line)
        form.addRow(box)

        self.task_mode = QComboBox()
        self.task_mode.addItem(tr("Hide all programs, open ones too"), TASKS_ALL)
        self.task_mode.addItem(tr("Hide only pinned programs that are not open"), TASKS_PINNED)
        self.task_mode.setCurrentIndex(max(0, self.task_mode.findData(config["taskMode"])))
        self.task_mode.setToolTip(tr("Open programs are windows: with the second choice they "
                                     "stay in the panel and only the pinned icons of programs "
                                     "that are not running disappear."))
        form.addRow(tr("Task manager:"), self.task_mode)

        self.active_place = QComboBox()
        for key, label in ACTIVE_PLACES:
            self.active_place.addItem(tr(label), key)
        self.active_place.setCurrentIndex(max(0, self.active_place.findData(config["activePlace"])))
        self.active_place.setToolTip(tr("A pinned program that is open normally stays on its "
                                        "pinned spot, between the others. In front or at the "
                                        "back, the open programs stand together and the pinned "
                                        "ones slide out next to them."))
        form.addRow(tr("Open programs:"), self.active_place)
        self.active_place.currentIndexChanged.connect(self.update_enabled)
        self.move_style = QComboBox()
        for key, label in MOVE_STYLES:
            self.move_style.addItem(tr(label), key)
        self.move_style.setCurrentIndex(max(0, self.move_style.findData(config["moveStyle"])))
        self.move_style.setToolTip(tr(
            "How a program that opens goes to the open programs, and back when it closes. "
            "Gliding: it slides there on top of the icons it passes. Fading over: it fades "
            "out on its old spot and comes up on the new one. The icons it passes glide a "
            "place over either way."))
        form.addRow(tr("It goes there:"), self.move_style)

        # Per program: in the drawer, or kept in the panel.
        self.programs = {}
        try:
            listed = json.loads(config["taskList"] or "[]")
        except ValueError:
            listed = []
        self.programs_box = QGroupBox(tr("Programs that go in the drawer"))
        self.programs_box.setToolTip(tr("A program without a tick stays in the panel, also "
                                        "while the drawer is closed."))
        box_layout = QVBoxLayout(self.programs_box)
        if listed:
            inner = QWidget()
            grid = QGridLayout(inner)
            grid.setContentsMargins(0, 0, 0, 0)
            for index, program in enumerate(p for p in listed if isinstance(p, dict)
                                            and p.get("id")):
                check = QCheckBox(str(program.get("name") or program["id"]))
                check.setIcon(app_icon(program["id"]))
                check.setChecked(program["id"] not in config["taskKeep"])
                self.programs[program["id"]] = check
                grid.addWidget(check, index // 2, index % 2)
            # The whole list where there is room for it; in less, three rows and scrolling.
            # The rows stay together at the top: room to spare is not spread between them.
            rows = max(1, grid.rowCount())
            tall = inner.sizeHint().height()
            grid.setRowStretch(rows, 1)
            box_layout.addWidget(TallArea(inner, least=min(tall, tall * 3 // rows + 4)))
        else:
            note = QLabel(tr("The programs of the task manager appear here a moment after the "
                             "drawer has one in it. Open this window again to see them."))
            note.setWordWrap(True)
            note.setEnabled(False)
            box_layout.addWidget(note)
        # As tall as its list and no taller: what the page has to spare stays below it.
        self.programs_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        form.addRow(self.programs_box)
        parts.addTab(page, tr("Contents"))

        # --- opening and closing ---
        page = QWidget()
        layout = QVBoxLayout(page)
        box = QGroupBox(tr("Opening"))
        form = QFormLayout(box)
        self.open_on = QComboBox()
        self.open_on.addItem(tr("A click on the arrow"), OPEN_CLICK)
        self.open_on.addItem(tr("Pointing at the arrow (a click works too)"), OPEN_HOVER)
        self.open_on.setCurrentIndex(max(0, self.open_on.findData(config["openOn"])))
        self.open_on.currentIndexChanged.connect(self.update_enabled)
        form.addRow(tr("Open with:"), self.open_on)

        self.hover_delay = QSpinBox(suffix=" ms", minimum=0, maximum=3000, singleStep=50)
        self.hover_delay.setValue(config["hoverDelay"])
        form.addRow(tr("Pointing opens after:"), self.hover_delay)

        self.shortcut = QKeySequenceEdit(QKeySequence(drawer.get("shortcut", "")))
        self.shortcut.setClearButtonEnabled(True)
        self.shortcut.setMaximumSequenceLength(1)
        self.shortcut.setToolTip(tr("A shortcut for this drawer alone. The shortcut for all "
                                    "drawers at once is set in System Settings."))
        form.addRow(tr("Shortcut:"), self.shortcut)

        self.attention = QCheckBox(tr("Open when a program asks for attention"))
        self.attention.setChecked(config["openOnAttention"])
        form.addRow(self.attention)

        self.panel_open = QCheckBox(tr("Open with a click on an empty spot in the panel"))
        self.panel_open.setChecked(config["openOnPanelClick"])
        self.panel_open.setToolTip(tr("A click where the panel is empty opens this drawer. As "
                                      "long as a drawer that opens with the same click is "
                                      "closed, the click only opens; it closes when all of "
                                      "them are open."))
        if self.fit:
            self.panel_open.setToolTip(tr("This panel is as long as its contents: it has no "
                                          "empty spot to click on."))
        form.addRow(self.panel_open)
        self.panel_open.toggled.connect(self.update_enabled)
        self.panel_kind = QComboBox()
        for key, label in PANEL_CLICKS:
            self.panel_kind.addItem(tr(label), key)
        self.panel_kind.setCurrentIndex(max(0, self.panel_kind.findData(config["panelClick"])))
        self.panel_kind.setToolTip(tr(
            "Which click on an empty spot of the panel opens this drawer, and closes it if "
            "that is ticked below. Give two drawers a different click and each opens on its "
            "own: the programs with a left click, say, and the system tray with the middle "
            "button. Drawers with the same click go together."))
        form.addRow(tr("That click is:"), self.panel_kind)

        self.on_desktop = QCheckBox(tr("Open when the desktop is shown"))
        self.on_desktop.setChecked(config["openOnDesktop"])
        self.on_desktop.setToolTip(tr("Works while Tidy is running."))
        form.addRow(self.on_desktop)
        layout.addWidget(box)

        box = QGroupBox(tr("Closing"))
        form = QFormLayout(box)
        self.auto_close = QComboBox()
        self.auto_close.addItem(tr("Never"), "")
        self.auto_close.addItem(tr("When the pointer leaves the drawer"), SCOPE_DRAWER)
        self.auto_close.addItem(tr("When the pointer leaves the panel"), SCOPE_PANEL)
        self.auto_close.setCurrentIndex(max(0, self.auto_close.findData(
            config["closeScope"] if config["autoClose"] else "")))
        self.auto_close.setToolTip(tr("The drawer is the arrow and the items it shows; empty "
                                      "panel space next to them is outside it."))
        self.auto_close.currentIndexChanged.connect(self.update_enabled)
        form.addRow(tr("Close by itself:"), self.auto_close)

        self.close_delay = QDoubleSpinBox(suffix=" s", minimum=0, maximum=60, singleStep=0.5,
                                          decimals=1)
        self.close_delay.setValue(config["closeDelay"] / 1000)
        form.addRow(tr("Closes after:"), self.close_delay)

        self.panel_click = QCheckBox(tr("Close with a click on an empty spot in the panel"))
        self.panel_click.setChecked(config["closeOnPanelClick"])
        form.addRow(self.panel_click)
        self.panel_click.toggled.connect(self.update_enabled)
        if self.fit:
            self.panel_click.setToolTip(tr("This panel is as long as its contents: it has no "
                                           "empty spot to click on."))

        self.after_use = QCheckBox(tr("Close after a click on something in the drawer"))
        self.after_use.setChecked(config["closeAfterUse"])
        form.addRow(self.after_use)
        self.after_use.toggled.connect(self.update_enabled)
        self.use_delay = QDoubleSpinBox(suffix=" s", minimum=0, maximum=60, singleStep=0.5,
                                        decimals=1)
        self.use_delay.setValue(config["useDelay"] / 1000)
        self.use_delay.setToolTip(tr(
            "After a click on a program in the drawer the drawer stays this long before it "
            "closes, so you see where the program went. With the programs in the middle of "
            "the panel a longer time is calmer. It never closes under the pointer: it waits "
            "until the pointer has left the drawer."))
        form.addRow(tr("Stays open after that click:"), self.use_delay)

        self.keep_panel = QDoubleSpinBox(suffix=" s", minimum=0, maximum=60, singleStep=0.5,
                                         decimals=1)
        self.keep_panel.setValue(config["keepPanel"] / 1000)
        self.keep_panel.setToolTip(tr(
            "A panel that hides itself or dodges windows goes the moment the window of a "
            "program you start from the drawer opens. With a time here it stays that long, "
            "so you can go on in the panel. 0: it goes at once."))
        form.addRow(tr("Panel stays after starting a program:"), self.keep_panel)

        self.on_maximized = QCheckBox(tr("Close when a window that fills the screen comes to "
                                         "the front"))
        self.on_maximized.setChecked(config["closeOnMaximized"])
        form.addRow(self.on_maximized)

        self.on_panel_hide = QCheckBox(tr("Close when the panel slides out of view"))
        self.on_panel_hide.setChecked(config["closeOnPanelHide"])
        self.on_panel_hide.setToolTip(tr(
            "When the panel hides (auto-hide, dodging a window, or hidden together with the "
            "desktop icons) the drawer closes, so the panel comes back tidy. It does not open "
            "again by itself."))
        form.addRow(self.on_panel_hide)
        layout.addWidget(box)
        layout.addStretch()
        parts.addTab(page, tr("Opening and closing"))

        # --- the arrow ---
        page = QWidget()
        form = QFormLayout(page)
        self.icon = QComboBox()
        for key, label in ICON_STYLES:
            self.icon.addItem(tr(label), key)
        self.icon.setCurrentIndex(max(0, self.icon.findData(config["icon"])))
        self.icon.setToolTip(tr("Without an icon the spot stays clickable and lights up under "
                                "the pointer."))
        self.icon.currentIndexChanged.connect(self.update_enabled)
        form.addRow(tr("Icon:"), self.icon)

        self.icon_custom = QLineEdit(config["iconCustom"])
        self.icon_custom.setPlaceholderText(tr("Icon name or image file"))
        self.icon_choose = QPushButton(tr("Choose…"))
        self.icon_choose.clicked.connect(self.choose_icon)
        row = QHBoxLayout()
        row.addWidget(self.icon_custom, 1)
        row.addWidget(self.icon_choose)
        form.addRow("", row)

        self.arrow_slim = QCheckBox(tr("Without an icon the arrow takes no room in the panel"))
        self.arrow_slim.setChecked(config["arrowSlim"])
        self.arrow_slim.setToolTip(tr(
            "The empty spot goes, and with it pointing at it and clicking it. Only while the "
            "drawer can be opened another way: a click on an empty spot of the panel, a "
            "shortcut, or when the desktop is shown. The room is back while you edit the "
            "panel and while the drawer is paused."))
        self.arrow_slim.toggled.connect(self.update_enabled)
        form.addRow(self.arrow_slim)
        self.arrow_slim_mark = QCheckBox(tr("Its room comes back while the mark has something to tell"))
        self.arrow_slim_mark.setChecked(config["arrowSlimMark"])
        self.arrow_slim_mark.setToolTip(tr(
            "On: the spot returns to show the mark, so the panel shifts a little at that "
            "moment. Off: the mark is not shown."))
        form.addRow(self.arrow_slim_mark)

        self.mark = QComboBox()
        self.mark.addItem(tr("None"), MARK_NONE)
        self.mark.addItem(tr("A dot when programs are open"), MARK_OPEN)
        self.mark.addItem(tr("The number of open programs"), MARK_COUNT)
        self.mark.addItem(tr("A dot only when a program asks for attention"), MARK_ATTENTION)
        self.mark.setCurrentIndex(max(0, self.mark.findData(config["indicator"])))
        self.mark.setToolTip(tr("Shown on the arrow while the drawer is closed and hides a task "
                                "manager with all its programs. The dot changes colour when a "
                                "program asks for attention."))
        form.addRow(tr("Mark on the closed drawer:"), self.mark)

        self.place = QComboBox()
        self.place.addItem(tr("Just before the items it hides"), PLACE_BEFORE)
        self.place.addItem(tr("Just after the items it hides"), PLACE_AFTER)
        self.place.addItem(tr("Where I put it myself"), PLACE_MANUAL)
        self.place.setCurrentIndex(max(0, self.place.findData(config["place"])))
        self.place.setToolTip(tr("After a task manager the arrow sits right behind the last "
                                 "program. The task manager then no longer fills the panel; "
                                 "the drawer does that instead."))
        form.addRow(tr("Place of the arrow:"), self.place)

        self.reverse = QCheckBox(tr("Arrow points the other way"))
        self.reverse.setChecked(config["reverseArrow"])
        form.addRow(self.reverse)

        self.display = QComboBox()
        for key, label in DISPLAYS:
            self.display.addItem(tr(label), key)
        self.display.setCurrentIndex(max(0, self.display.findData(config["display"])))
        self.display.setToolTip(tr(
            "In the panel: what is in the drawer slides out next to the arrow. In a pop-up: "
            "it stays out of the panel and comes up in a small window above the arrow, so the "
            "panel never changes size; made for a panel that is as long as its contents. "
            "Programs are shown as icons you can click; any other widget, such as the system "
            "tray, is moved into the pop-up as it is and keeps its own shape."))
        self.display.currentIndexChanged.connect(self.update_enabled)
        form.addRow(tr("Shows its contents:"), self.display)

        self.popup_style = QComboBox()
        for key, label in POPUP_STYLES:
            self.popup_style.addItem(tr(label), key)
        self.popup_style.setCurrentIndex(max(0, self.popup_style.findData(config["popupStyle"])))
        form.addRow(tr("Pop-up:"), self.popup_style)

        self.popup_place = QComboBox()
        for key, label in POPUP_PLACES:
            self.popup_place.addItem(tr(label), key)
        self.popup_place.setCurrentIndex(max(0, self.popup_place.findData(config["popupPlace"])))
        self.popup_place.setToolTip(tr(
            "Above the arrow, or at a fixed spot of the panel, wherever the arrow is. The "
            "pop-up ends where the panel ends. Is that at the edge of the screen, then a "
            "pointer pushed against that edge is on the icons."))
        form.addRow(tr("Place of the pop-up:"), self.popup_place)

        self.popup_background = QCheckBox(tr("Pop-up has a background, like the panel"))
        self.popup_background.setChecked(config["popupBackground"])
        self.popup_background.setToolTip(tr("On: the pop-up looks like a piece of your panel. "
                                            "Off: only the icons, on whatever is behind them."))
        form.addRow(self.popup_background)

        self.popup_gap = QCheckBox(tr("Pop-up floats above the panel, like Plasma's own pop-ups"))
        self.popup_gap.setChecked(config["popupGap"])
        self.popup_gap.setToolTip(tr("On: the pop-up keeps the same distance from the panel as "
                                     "the system tray's own pop-up and the start menu, so "
                                     "they all line up. Off: it stands on the panel's edge. "
                                     "Only a floating panel shows the difference."))
        form.addRow(self.popup_gap)

        self.arrow_tip = QCheckBox(tr("The arrow shows a balloon when you point at it"))
        self.arrow_tip.setChecked(config["arrowTip"])
        form.addRow(self.arrow_tip)

        self.tray_arrow = QComboBox()
        for key, label in TRAY_ARROWS:
            self.tray_arrow.addItem(tr(label), key)
        self.tray_arrow.setCurrentIndex(max(0, self.tray_arrow.findData(config["trayArrow"])))
        self.tray_arrow.setToolTip(tr(
            "With the system tray in a pop-up, only its icons go there. The tray's own arrow, "
            "for the icons it keeps hidden, can stay in the panel, show there only while the "
            "pop-up is open, or go altogether. Without it, the icons under it can only be "
            "reached by setting them to Show on the System tray tab."))
        form.addRow(tr("The system tray's own arrow (^):"), self.tray_arrow)

        self.animation = QComboBox()
        for key, label in ANIMATIONS:
            self.animation.addItem(tr(label), key)
        self.animation.setCurrentIndex(max(0, self.animation.findData(config["animation"])))
        self.animation.setToolTip(tr("Slide: the icons slide out from under the arrow at their "
                                     "normal size, like a drawer. Grow: they grow from small to "
                                     "their normal size. One by one: they come and go one after "
                                     "the other. Fade: they fade together and the rest closes "
                                     "up."))
        form.addRow(tr("Animation:"), self.animation)
        if self.fit:
            self.animation.setToolTip(tr(
                "This panel is as long as its contents, so it jumps to its new size when the "
                "drawer opens. Sliding inside it adds nothing then: the icons fade, whatever "
                "is chosen here."))

        self.duration = QSpinBox(suffix=" ms", minimum=50, maximum=2000, singleStep=50)
        self.duration.setValue(config["animationDuration"])
        self.duration.setToolTip(tr("How long the movement takes; one by one, how long each "
                                    "icon takes."))
        form.addRow(tr("Speed:"), self.duration)

        hint = QLabel(tr("The arrow sits next to the items it hides. To place it yourself, "
                         "choose \"Where I put it myself\", right-click the panel, choose "
                         "Enter Edit Mode and drag it."))
        hint.setWordWrap(True)
        hint.setEnabled(False)
        form.addRow(hint)
        parts.addTab(page, tr("Appearance"))

        self.update_enabled()
        self.relabel()

    def auto_name(self):
        """What the drawer is called without a name of its own: after its contents."""
        inside = [check.text() for check, _ in self.targets.values() if check.isChecked()]
        return ", ".join(inside) or tr("Drawer {n}").format(n=self.number)

    def label(self):
        return self.name.text().strip() or self.auto_name()

    def relabel(self, *_):
        self.name.setPlaceholderText(self.auto_name())
        if self.on_label:
            self.on_label(self)

    def update_enabled(self):
        tasks = any(check.isChecked() and plugin in TASK_PLUGINS
                    for check, plugin in self.targets.values())
        self.task_mode.setEnabled(tasks)
        self.active_place.setEnabled(tasks)
        self.move_style.setEnabled(tasks and self.active_place.currentData() != "fixed")
        self.programs_box.setEnabled(tasks)
        popup = self.display.currentData() == DISPLAY_POPUP
        self.popup_style.setEnabled(popup)
        self.popup_place.setEnabled(popup)
        self.popup_background.setEnabled(popup)
        self.popup_gap.setEnabled(popup)
        self.tray_arrow.setEnabled(popup and any(
            check.isChecked() and plugin == "org.kde.plasma.systemtray"
            for check, plugin in self.targets.values()))
        self.animation.setEnabled(not popup and not self.fit)
        # A panel as long as its contents has no empty spot to click on.
        for box in (self.panel_click, self.panel_open):
            box.setEnabled(not self.fit)
        self.panel_kind.setEnabled(not self.fit and (self.panel_click.isChecked()
                                                     or self.panel_open.isChecked()))
        self.hover_delay.setEnabled(self.open_on.currentData() == OPEN_HOVER)
        self.close_delay.setEnabled(bool(self.auto_close.currentData()))
        self.use_delay.setEnabled(self.after_use.isChecked())
        custom = self.icon.currentData() == "custom"
        self.icon_custom.setEnabled(custom)
        self.icon_choose.setEnabled(custom)
        bare = self.icon.currentData() == "none"
        self.arrow_slim.setEnabled(bare)
        self.arrow_slim_mark.setEnabled(bare and self.arrow_slim.isChecked())

    def choose_icon(self):
        name, _ = QFileDialog.getOpenFileName(
            self, tr("Choose an image"), os.path.dirname(self.icon_custom.text()),
            "(*.svg *.svgz *.png *.jpg *.jpeg *.webp)")
        if name:
            self.icon_custom.setText(name)

    def values(self):
        return {"name": self.name.text().strip(),
                "targets": [str(i) for i, (check, _) in self.targets.items()
                            if check.isChecked()],
                "taskMode": self.task_mode.currentData(),
                "taskKeep": [i for i in self.drawer["config"]["taskKeep"]
                             if i not in self.programs]
                            + [i for i, check in self.programs.items() if not check.isChecked()],
                "activePlace": self.active_place.currentData(),
                "moveStyle": self.move_style.currentData(),
                "openOn": self.open_on.currentData(),
                "hoverDelay": self.hover_delay.value(),
                "openOnAttention": self.attention.isChecked(),
                "openOnDesktop": self.on_desktop.isChecked(),
                "autoClose": bool(self.auto_close.currentData()),
                "closeScope": self.auto_close.currentData() or self.drawer["config"]["closeScope"],
                "closeDelay": round(self.close_delay.value() * 1000),
                "keepPanel": round(self.keep_panel.value() * 1000),
                "closeOnPanelClick": self.panel_click.isChecked(),
                "openOnPanelClick": self.panel_open.isChecked(),
                "panelClick": self.panel_kind.currentData(),
                "closeAfterUse": self.after_use.isChecked(),
                "useDelay": round(self.use_delay.value() * 1000),
                "closeOnPanelHide": self.on_panel_hide.isChecked(),
                "closeOnMaximized": self.on_maximized.isChecked(),
                "icon": self.icon.currentData(),
                "iconCustom": self.icon_custom.text().strip(),
                "indicator": self.mark.currentData(),
                "place": self.place.currentData(),
                "reverseArrow": self.reverse.isChecked(),
                "display": self.display.currentData(),
                "popupStyle": self.popup_style.currentData(),
                "popupPlace": self.popup_place.currentData(),
                "popupBackground": self.popup_background.isChecked(),
                "popupGap": self.popup_gap.isChecked(),
                "trayArrow": self.tray_arrow.currentData(),
                "arrowTip": self.arrow_tip.isChecked(),
                "arrowSlim": self.arrow_slim.isChecked(),
                "arrowSlimMark": self.arrow_slim_mark.isChecked(),
                "animation": self.animation.currentData(),
                "animationDuration": self.duration.value()}

    def apply(self, plasma):
        config = self.drawer["config"]
        changed = {k: v for k, v in self.values().items() if v != config[k]}
        if changed:
            plasma.set_drawer_config(self.drawer["id"], changed)
            config.update(changed)
        if "targets" in changed or "place" in changed:
            # The arrow belongs next to what it hides.
            plasma.place_drawer(self.drawer["id"], config["targets"], config["place"])
        shortcut = self.shortcut.keySequence().toString(QKeySequence.SequenceFormat.PortableText)
        if shortcut != self.drawer.get("shortcut", ""):
            plasma.set_drawer_shortcut(self.drawer["id"], shortcut)
            self.drawer["shortcut"] = shortcut


class TallArea(QScrollArea):
    """Asks for the room its contents take, and scrolls them in a window that has less."""

    def __init__(self, inside, least=240):
        super().__init__(widgetResizable=True)
        self.least = least
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(inside)
        self.viewport().setAutoFillBackground(False)
        inside.setAutoFillBackground(False)

    def sizeHint(self):
        return self.widget().sizeHint()

    def minimumSizeHint(self):
        bar = self.verticalScrollBar().sizeHint().width()
        return QSize(self.widget().minimumSizeHint().width() + bar, self.least)


class DrawerTab(QWidget):
    """Tab for the panel drawers: arrows that tuck panel widgets away."""

    def __init__(self, autohide):
        super().__init__()
        self.plasma = autohide.plasma
        self.pages = []
        self.panels = []
        # The tab is the tallest of all: on a low screen it scrolls rather than pushing the
        # window's buttons out of view.
        inside = QWidget()
        layout = QVBoxLayout(inside)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(TallArea(inside))

        intro = QLabel(tr("A drawer is an arrow in the panel. It tucks the widgets you choose "
                          "away and brings them back when you click or point at the arrow."))
        intro.setWordWrap(True)
        layout.addWidget(intro)

        row = QHBoxLayout()
        row.addWidget(QLabel(tr("Drawer:")))
        self.selector = QComboBox()
        self.selector.setProperty("tidyNoSetting", True)
        self.rebuilt = None  # called with this tab when its pages have been made anew
        row.addWidget(self.selector, 1)
        self.add_button = QPushButton(QIcon.fromTheme("list-add"), tr("Add a drawer"))
        self.add_button.clicked.connect(self.add)
        row.addWidget(self.add_button)
        self.remove_button = QPushButton(QIcon.fromTheme("list-remove"), tr("Remove"))
        self.remove_button.clicked.connect(self.remove)
        row.addWidget(self.remove_button)
        layout.addLayout(row)

        self.stack = QStackedWidget()
        self.selector.currentIndexChanged.connect(self.stack.setCurrentIndex)
        layout.addWidget(self.stack)

        box = QGroupBox(tr("All drawers"))
        box_layout = QVBoxLayout(box)
        self.follow = QCheckBox(tr("Close and open together with the desktop icons"))
        self.follow.setChecked(autohide.settings.value("drawer_follow", False, bool))
        box_layout.addWidget(self.follow)
        layout.addWidget(box)

        # Plasma's own balloons and pop-ups: shown as they are now, not as Tidy last set them.
        box = QGroupBox(tr("Balloons and previews"))
        form = QFormLayout(box)
        self.balloons = QCheckBox(tr("Plasma shows a balloon with text when you point at something"))
        # With Tidy switched off Plasma is as it is without Tidy: then what Tidy will set.
        off = autohide.settings.value("suspended", False, bool)
        self.balloons.setChecked(autohide.settings.value("balloons", True, bool) if off
                                 else plasma_balloons())
        self.balloons.setToolTip(tr(
            "Plasma's own setting, for every balloon in the panel, the system tray and on the "
            "desktop. Off: none of them appear. The pop-up of a program in the panel is "
            "chosen below, and can stay."))
        form.addRow(self.balloons)
        self.balloon_gap = QCheckBox(tr("Balloons float above the panel, like Plasma's own pop-ups"))
        self.balloon_gap.setChecked(autohide.settings.value("balloon_gap", False, bool))
        self.balloon_gap.setToolTip(tr(
            "On: the same distance from the panel as the start menu and the system tray's "
            "own pop-up. Off: against the panel, as Plasma puts it. Only a floating panel "
            "shows the difference. Works in a panel that has a drawer."))
        form.addRow(self.balloon_gap)
        self.balloons.toggled.connect(self.update_tips)
        self.task_popup = QComboBox()
        for key, label in TASK_POPUPS:
            self.task_popup.addItem(tr(label), key)
        previews = self.plasma.task_previews()
        shown = autohide.settings.value("task_popup", "preview")
        if shown != "none" and not off:
            if not all(previews.values()):
                shown = "text"
            elif shown != "only":
                shown = "preview"
        self.task_popup.setCurrentIndex(max(0, self.task_popup.findData(shown)))
        self.task_popup.setToolTip(tr(
            "What comes up when you point at a program in the panel. With or without the "
            "preview is the task manager's own setting. Only the preview, none at all, and a "
            "pop-up while Plasma's balloons are off, are done by a drawer: they work for a "
            "task manager that is in a drawer. Only the preview leaves out the title and the "
            "text. A program that is not open shows its name, as long as Plasma's balloons "
            "are on."))
        form.addRow(tr("Pop-up of a program in the panel:"), self.task_popup)
        self.task_close = QCheckBox(tr("With only the preview: keep the close button, above it"))
        self.task_close.setChecked(autohide.settings.value("task_close", True, bool))
        self.task_close.setToolTip(tr(
            "The pop-up's close button sits next to the title and the text. On: it stays "
            "where it is, above the preview. Off: it goes with them."))
        form.addRow(self.task_close)
        self.task_gap = QCheckBox(tr("This pop-up floats above the panel, like Plasma's own pop-ups"))
        self.task_gap.setChecked(autohide.settings.value("task_gap", False, bool))
        self.task_gap.setToolTip(tr(
            "On: the same distance from the panel as the start menu and the system tray's "
            "own pop-up. Off: against the panel, as Plasma puts it. Only a floating panel "
            "shows the difference. Works in a panel that has a drawer."))
        form.addRow(self.task_gap)
        self.task_popup.currentIndexChanged.connect(self.update_tips)
        self.update_tips()
        # About the panel as a whole, not about drawers: the window shows it on its Panel tab.
        self.tips_box = box
        layout.addStretch()
        self.rebuild()

    def update_tips(self):
        self.task_close.setEnabled(self.task_popup.currentData() == "only")
        self.task_gap.setEnabled(self.task_popup.currentData() != "none")
        self.balloon_gap.setEnabled(self.balloons.isChecked())

    def rebuild(self, select=None):
        """Read the drawers from the panels again and show a page for each."""
        self.selector.blockSignals(True)
        self.selector.clear()
        while self.stack.count():
            page = self.stack.widget(0)
            self.stack.removeWidget(page)
            page.deleteLater()
        self.pages = []
        self.panels = self.plasma.panel_widgets()
        by_id = {panel["panel"]: panel for panel in self.panels}
        for number, drawer in enumerate(self.plasma.drawers(), 1):
            panel = by_id.get(drawer["panel"])
            if not panel:
                continue
            page = DrawerPage(drawer, panel["widgets"], number, self.relabel,
                              fit=bool(panel.get("fit")), folders=self)
            # Which panel only matters when there is more than one.
            page.panel_name = (tr(PANEL_PLACES.get(panel["location"], "Panel"))
                               if len(self.panels) > 1 else "")
            self.pages.append(page)
            self.stack.addWidget(page)
            self.selector.addItem(self.label(page), drawer["id"])
        if not self.pages:
            empty = QLabel(tr("No drawer yet. Add one to hide panel icons behind an arrow."))
            empty.setWordWrap(True)
            empty.setEnabled(False)
            self.stack.addWidget(empty)
        self.selector.blockSignals(False)
        self.selector.setEnabled(bool(self.pages))
        self.remove_button.setEnabled(bool(self.pages))
        index = max(0, self.selector.findData(select)) if select is not None else 0
        self.selector.setCurrentIndex(index)
        self.stack.setCurrentIndex(index)
        if self.rebuilt:
            self.rebuilt(self)

    @staticmethod
    def label(page):
        return f"{page.label()} — {page.panel_name}" if page.panel_name else page.label()

    def relabel(self, page):
        if page in self.pages:
            self.selector.setItemText(self.pages.index(page), self.label(page))

    def add(self):
        if not self.panels:
            QMessageBox.warning(self, APP_NAME, tr("No panel found."))
            return
        panel = self.panels[0]
        if len(self.panels) > 1:
            # Several panels: ask which one.
            menu = QMenu(self)
            for candidate in self.panels:
                action = menu.addAction(tr(PANEL_PLACES.get(candidate["location"], "Panel")))
                action.setData(candidate["panel"])
            chosen = menu.exec(self.add_button.mapToGlobal(self.add_button.rect().bottomLeft()))
            if not chosen:
                return
            panel = next(p for p in self.panels if p["panel"] == chosen.data())
        # A new drawer starts with the task manager in it. If another drawer has that
        # already, with the system tray; failing that, empty. Its arrow sits next to them.
        self.apply()
        taken = {i for page in self.pages for i in page.drawer["config"]["targets"]}
        targets = []
        for plugins in (TASK_PLUGINS, ("org.kde.plasma.systemtray",)):
            targets = [str(w["id"]) for w in panel["widgets"]
                       if w["type"] in plugins and str(w["id"]) not in taken]
            if targets:
                break
        config = new_drawer(targets)
        install_drawer()
        new_id = self.plasma.add_drawer(panel["panel"], config)
        if new_id is None:
            QMessageBox.warning(self, APP_NAME, tr("The drawer could not be added to the panel."))
        self.rebuild(select=new_id)

    def add_folder(self, page):
        """A folder for quick access, in this drawer: asked for, put in the panel next to the
        drawer's arrow, and ticked."""
        path = QFileDialog.getExistingDirectory(self, tr("Choose a folder for the drawer"),
                                                os.path.expanduser("~"))
        if not path:
            return
        self.apply()   # what was changed in the window is not lost when the pages are rebuilt
        drawer = page.drawer
        new_id = self.plasma.add_folder(drawer["id"], QUrl.fromLocalFile(path).toString())
        if new_id is None:
            QMessageBox.warning(self, APP_NAME, tr("The folder could not be added to the panel."))
            return
        targets = list(drawer["config"]["targets"]) + [str(new_id)]
        self.plasma.set_drawer_config(drawer["id"], {"targets": targets})
        self.plasma.place_drawer(drawer["id"], targets, drawer["config"]["place"])
        self.rebuild(select=drawer["id"])

    def configure_folder(self, page, widget_id):
        self.plasma.configure_folder(page.drawer["id"], widget_id)

    def remove_folder(self, page, widget_id):
        self.apply()
        drawer = page.drawer
        targets = [t for t in drawer["config"]["targets"] if t != str(widget_id)]
        if targets != list(drawer["config"]["targets"]):
            self.plasma.set_drawer_config(drawer["id"], {"targets": targets})
        self.plasma.remove_folder(widget_id)
        self.rebuild(select=drawer["id"])

    def remove(self):
        drawer_id = self.selector.currentData()
        if drawer_id is None:
            return
        self.apply()
        self.plasma.remove_drawer(drawer_id)
        self.rebuild()

    def apply(self):
        for page in self.pages:
            page.apply(self.plasma)
