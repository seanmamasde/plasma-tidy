# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""The settings window."""

import json
import os

from PyQt6.QtCore import QByteArray, Qt, QTimer, QUrl
from PyQt6.QtGui import (QDesktopServices, QFont, QIcon, QKeySequence, QPainter, QPalette,
                         QPixmap)
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QDoubleSpinBox, QFileDialog, QFormLayout, QGridLayout, QGroupBox,
                             QHBoxLayout, QInputDialog, QKeySequenceEdit, QLabel, QLineEdit,
                             QMessageBox, QProgressBar, QPushButton, QSpinBox, QTabWidget,
                             QTimeEdit, QVBoxLayout, QWidget)

from .consts import (APP, APP_ICON, APP_NAME, AUTHOR, AUTOSTART, BRAND, BUGS_URL, CLICKS_DOUBLE,
                     CLICKS_SINGLE, CORNERS, DESCRIPTION, DONATE_URL, LICENSE, MODE_ACTIVITY,
                     MODE_CLICK, PANEL_AFTER_NEVER, PANEL_AFTERS, REHIDE_FIXED, REHIDE_IDLE, VERSION, WEBSITE_URL)
from .drawer_ui import DrawerTab
from .i18n import LANGUAGES, tr
from .peek import bare_key
from .plasma import widget_name
from .resources import WISPWARE_LOGO
from .rules_ui import RulesTab
from .search import SearchBox
from .tray import TrayTab


class FocusTab(QWidget):
    """Tab for focus mode: everything tucked away at once."""

    PARTS = [("icons", "Hide the desktop icons", True),
             ("drawers", "Close the panel drawers", True),
             ("tray", "Set the system tray to Minimal", True),
             ("panel", "Auto-hide the panel", False)]

    def __init__(self, autohide):
        super().__init__()
        self.autohide = autohide
        layout = QVBoxLayout(self)
        intro = QLabel(tr("Focus mode tucks everything away at once and keeps it away: nothing "
                          "comes back on mouse movement or a click on the desktop. Switching it "
                          "off puts everything back as it was."))
        intro.setWordWrap(True)
        layout.addWidget(intro)

        box = QGroupBox(tr("In focus mode"))
        box_layout = QVBoxLayout(box)
        self.boxes = {}
        for key, text, default in self.PARTS:
            check = QCheckBox(tr(text))
            check.setChecked(autohide.settings.value("focus_" + key, default, bool))
            self.boxes[key] = check
            box_layout.addWidget(check)
        layout.addWidget(box)

        row = QHBoxLayout()
        self.button = QPushButton()
        self.button.clicked.connect(self.toggle)
        row.addWidget(self.button)
        row.addStretch()
        layout.addLayout(row)

        hint = QLabel(tr("Focus mode is also in the tray menu, and you can give it a shortcut "
                         "(see the General tab). A closed drawer still opens when you click or "
                         "point at its arrow."))
        hint.setWordWrap(True)
        hint.setEnabled(False)
        layout.addWidget(hint)
        layout.addStretch()
        self.refresh()

    def refresh(self):
        self.button.setText(tr("Switch focus mode off") if self.autohide.focus
                            else tr("Save and switch focus mode on"))

    def save(self):
        for key, check in self.boxes.items():
            self.autohide.settings.setValue("focus_" + key, check.isChecked())

    def toggle(self):
        if self.autohide.focus:
            self.autohide.set_focus(False)
            self.refresh()
        else:
            # Apply the whole window first: focus mode starts from the saved settings.
            autohide = self.autohide
            self.window().accept()
            QTimer.singleShot(0, lambda: autohide.set_focus(True))


def open_donate():
    if DONATE_URL:
        QDesktopServices.openUrl(QUrl(DONATE_URL))


def brand_logo(widget, height):
    """The Wispware logo as a picture, in the text colour of the theme and sharp on the
    screen it is shown on; None if it cannot be drawn (Qt's SVG part is missing)."""
    try:
        from PyQt6.QtSvg import QSvgRenderer
    except ImportError:
        return None
    colour = widget.palette().color(QPalette.ColorRole.WindowText).name()
    renderer = QSvgRenderer(QByteArray(WISPWARE_LOGO.replace("#111111", colour).encode()))
    if not renderer.isValid():
        return None
    size = renderer.defaultSize()
    ratio = widget.devicePixelRatioF()
    width = round(height * size.width() / size.height())
    picture = QPixmap(round(width * ratio), round(height * ratio))
    picture.fill(Qt.GlobalColor.transparent)
    painter = QPainter(picture)
    renderer.render(painter)
    painter.end()
    picture.setDevicePixelRatio(ratio)
    return picture


class AboutTab(QWidget):
    """About Tidy: version, author, license, links and the donate button."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        head = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(QIcon.fromTheme(APP_ICON, QIcon.fromTheme("view-visible")).pixmap(64, 64))
        head.addWidget(icon)
        title = QLabel(f"<span style='font-size:20pt; font-weight:600'>{APP_NAME}</span><br>"
                       + tr("Version {version}").format(version=VERSION))
        head.addWidget(title, 1)
        layout.addLayout(head)

        about = QLabel(tr(DESCRIPTION) + "<br><br>"
                       + tr("Hides your desktop icons when you don't need them, tucks the "
                            "programs and icons in your panel away behind an arrow, and lets "
                            "you choose per icon what shows in the system tray."))
        about.setWordWrap(True)
        layout.addWidget(about)

        later = tr("coming with the first release")

        def link(url, text):
            return f"<a href='{url}'>{text}</a>" if url else f"{text} <i>({later})</i>"

        # Who made it, with the maker's mark next to it.
        maker = QHBoxLayout()
        maker.setSpacing(8)
        maker.addWidget(QLabel(tr("Made by {author}").format(author=AUTHOR) + "  ·"))
        logo = brand_logo(self, 18)
        if logo:
            mark = QLabel()
            mark.setPixmap(logo)
            mark.setToolTip(BRAND)
            mark.setAccessibleName(BRAND)
            maker.addWidget(mark)
        else:
            maker.addWidget(QLabel(BRAND))
        maker.addStretch()
        layout.addLayout(maker)

        info = QLabel(tr("License: {license}").format(license=LICENSE or f"<i>{later}</i>")
                      + "<br><br>"
                      + link(WEBSITE_URL, tr("Website and source code")) + "<br>"
                      + link(BUGS_URL, tr("Report a problem or share an idea")))
        info.setOpenExternalLinks(True)
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()

        donate_box = QGroupBox(tr("Support {app}").format(app=APP_NAME))
        donate_layout = QVBoxLayout(donate_box)
        text = QLabel(tr("{app} is free and open source. Find it useful? "
                         "A small donation helps further development.").format(app=APP_NAME))
        text.setWordWrap(True)
        donate_layout.addWidget(text)
        self.donate = QPushButton(tr("♥  Donate"))
        font = QFont(self.donate.font())
        font.setBold(True)
        self.donate.setFont(font)
        self.donate.setMinimumHeight(36)
        self.donate.clicked.connect(open_donate)
        if not DONATE_URL:
            self.donate.setEnabled(False)
            self.donate.setToolTip(tr("The donation page is coming with the first release."))
        donate_layout.addWidget(self.donate)
        layout.addWidget(donate_box)


class SettingsDialog(QDialog):
    def __init__(self, autohide):
        super().__init__()
        self.autohide = autohide
        settings = autohide.settings
        self.setWindowTitle(tr("{app} — settings").format(app=APP_NAME))
        self.setWindowIcon(QIcon.fromTheme(APP_ICON, QIcon.fromTheme("view-visible")))
        outer = QVBoxLayout(self)
        tabs = QTabWidget()
        # All tabs in view at once: the window is made wide enough rather than the tab bar
        # getting arrows to scroll with.
        tabs.setUsesScrollButtons(False)
        find = QHBoxLayout()
        find.addStretch()
        self.search = SearchBox(self)
        self.search.setMinimumWidth(300)
        find.addWidget(self.search)
        outer.addLayout(find)
        outer.addWidget(tabs)
        desktop_tab = QWidget()
        layout = QVBoxLayout(desktop_tab)
        tabs.addTab(desktop_tab, QIcon.fromTheme("user-desktop"), tr("Desktop"))
        self.drawer_tab = DrawerTab(autohide)
        tabs.addTab(self.drawer_tab,
                    QIcon.fromTheme("sidebar-collapse-left", QIcon.fromTheme("arrow-left")),
                    tr("Drawers"))
        panel_tab = QWidget()
        tabs.addTab(panel_tab, QIcon.fromTheme("show-menu", QIcon.fromTheme("view-list-icons")),
                    tr("Panel"))
        self.tray_tab = TrayTab(autohide.plasma, settings)
        tabs.addTab(self.tray_tab, QIcon.fromTheme("preferences-desktop-notification"),
                    tr("System tray"))
        self.focus_tab = FocusTab(autohide)
        tabs.addTab(self.focus_tab, QIcon.fromTheme("mode-focus", QIcon.fromTheme("view-hidden")),
                    tr("Focus mode"))
        self.rules_tab = RulesTab(autohide)
        tabs.addTab(self.rules_tab, QIcon.fromTheme("preferences-system-time",
                                                    QIcon.fromTheme("view-calendar")),
                    tr("Rules"))
        general_tab = QWidget()
        tabs.addTab(general_tab, QIcon.fromTheme("configure"), tr("General"))
        self.about_tab = AboutTab()
        tabs.addTab(self.about_tab, QIcon.fromTheme("help-about"),
                    tr("About {app}").format(app=APP_NAME))
        self.tabs = tabs

        # --- live status ---
        status = QGroupBox("Status")
        status_layout = QVBoxLayout(status)
        self.status_label = QLabel()
        self.bar = QProgressBar(minimum=0, maximum=1000)
        row = QHBoxLayout()
        row.addWidget(self.bar, 1)
        hide_now = QPushButton(QIcon.fromTheme("view-hidden"), tr("Hide now"))
        hide_now.clicked.connect(autohide.hide)
        row.addWidget(hide_now)
        status_layout.addWidget(self.status_label)
        status_layout.addLayout(row)
        layout.addWidget(status)

        # --- settings, in the order of the story: when they go, how they come back, what
        # goes along, and how it is done ---
        box = QGroupBox(tr("When the icons hide"))
        form = QFormLayout(box)
        layout.addWidget(box)

        self.timeout = QSpinBox(suffix=" s", minimum=3, maximum=3600)
        self.timeout.setValue(settings.value("timeout", 10, int))
        form.addRow(tr("Hide after:"), self.timeout)

        self.only_desktop = QCheckBox(tr("Activity in other windows doesn't count"))
        self.only_desktop.setChecked(settings.value("only_desktop", True, bool))
        self.only_desktop.setToolTip(tr("On: while you work in another window the timer keeps "
                                        "running and the icons disappear behind your window. "
                                        "Moving the mouse over the desktop itself always "
                                        "counts.\n"
                                        "Off: every mouse movement or key press, anywhere, "
                                        "counts."))
        form.addRow(self.only_desktop)

        self.panel_counts = QCheckBox(tr("Moving over the panel does count"))
        self.panel_counts.setChecked(settings.value("panel_counts", True, bool))
        self.panel_counts.setToolTip(tr("On: moving the mouse over the panel (taskbar) keeps "
                                        "the icons, like moving over the desktop.\n"
                                        "Off: only the desktop itself counts."))
        row = QHBoxLayout()
        row.addSpacing(24)
        row.addWidget(self.panel_counts)
        form.addRow(row)
        self.only_desktop.toggled.connect(self.update_enabled)

        self.double_hides = QCheckBox(tr("A double-click on an empty spot of the desktop hides "
                                         "the icons"))
        self.double_hides.setChecked(settings.value("double_hides", False, bool))
        self.double_hides.setToolTip(tr("Needs the helper widget on the desktop."))
        form.addRow(self.double_hides)

        box = QGroupBox(tr("How they come back"))
        form = QFormLayout(box)
        layout.addWidget(box)
        self.back_form = form

        # One choice for how they come back; kept as two settings (mode and clicks).
        self.back = QComboBox()
        self.back.addItem(tr("On any mouse movement or key press"), f"{MODE_ACTIVITY}:{CLICKS_SINGLE}")
        self.back.addItem(tr("On a click on the desktop"), f"{MODE_CLICK}:{CLICKS_SINGLE}")
        self.back.addItem(tr("On a double-click on the desktop"), f"{MODE_CLICK}:{CLICKS_DOUBLE}")
        mode = settings.value("mode", MODE_ACTIVITY)
        clicks = settings.value("clicks", CLICKS_SINGLE) if mode == MODE_CLICK else CLICKS_SINGLE
        self.back.setCurrentIndex(max(0, self.back.findData(f"{mode}:{clicks}")))
        form.addRow(tr("The icons come back:"), self.back)

        chosen = settings.value("buttons", "left,right,middle").split(",")
        self.buttons = {}
        row = QHBoxLayout()
        for key, label in (("left", tr("Left")), ("middle", tr("Middle")),
                           ("right", tr("Right"))):
            box = QCheckBox(label)
            box.setChecked(key in chosen)
            box.toggled.connect(self.update_enabled)
            self.buttons[key] = box
            row.addWidget(box)
        self.buttons_row = row
        form.addRow(tr("With mouse button:"), row)

        self.rehide = QComboBox()
        self.rehide.addItem(tr("After that time without movement (moving postpones)"),
                            REHIDE_IDLE)
        self.rehide.addItem(tr("After that time, even while you move"), REHIDE_FIXED)
        self.rehide.setCurrentIndex(self.rehide.findData(settings.value("rehide", REHIDE_IDLE)))
        self.rehide.setToolTip(tr("With a fixed time the icons can disappear just as you are "
                                  "about to click something; 10 s or more works well."))
        form.addRow(tr("After that they hide:"), self.rehide)

        self.corner = QComboBox()
        for key, label, _js in CORNERS:
            self.corner.addItem(tr(label), key)
        self.corner.setCurrentIndex(self.corner.findData(settings.value("corner", "none")))
        self.corner.setToolTip(tr("Moving the mouse into this screen corner brings the icons "
                                  "back.\n"
                                  "Note: KDE may already have an action on that corner "
                                  "(System Settings → Screen Edges)."))
        form.addRow(tr("Screen corner shows:"), self.corner)

        box = QGroupBox(tr("What hides along"))
        form = QFormLayout(box)
        layout.addWidget(box)

        self.panel = QCheckBox(tr("Also hide the panel (taskbar)"))
        self.panel.setChecked(settings.value("hide_panel", False, bool))
        form.addRow(self.panel)

        self.hide_widgets = QCheckBox(tr("Also hide the widgets on the desktop"))
        self.hide_widgets.setChecked(settings.value("hide_widgets", False, bool))
        self.hide_widgets.setToolTip(tr("Clocks, notes and other widgets on the desktop go and "
                                        "come with the icons. Needs the helper widget on "
                                        "the desktop."))
        form.addRow(self.hide_widgets)

        # Per widget, when there are any: with a tick it goes along, without it stays.
        kept = [i for i in settings.value("widgets_keep", "").split(",") if i]
        self.widget_boxes = {}
        self.widgets_gone = kept  # choices for widgets that are not there now are kept
        found = autohide.plasma.desktop_widgets()
        if found:
            inner = QWidget()
            grid = QGridLayout(inner)
            grid.setContentsMargins(24, 0, 0, 0)
            names = [widget_name(w["type"]) for w in found]
            for index, (widget, name) in enumerate(zip(found, names)):
                if names.count(name) > 1:
                    name += f" ({names[:index + 1].count(name)})"
                box = QCheckBox(name)
                box.setChecked(str(widget["id"]) not in kept)
                box.setToolTip(tr("Without a tick this widget stays in view."))
                self.widget_boxes[str(widget["id"])] = box
                grid.addWidget(box, index // 3, index % 3)
            form.addRow(inner)
            self.hide_widgets.toggled.connect(self.update_enabled)

        # Per screen, only when there is a choice to make.
        self.skipped = [name for name in settings.value("skip_screens", "").split(",") if name]
        self.screens = {}
        screens = QApplication.screens()
        if len(screens) > 1 or self.skipped:
            row = QVBoxLayout()
            for screen in screens:
                box = QCheckBox(f"{screen.name()} ({screen.model()})" if screen.model()
                                else screen.name())
                box.setChecked(screen.name() not in self.skipped)
                self.screens[screen.name()] = box
                row.addWidget(box)
            form.addRow(tr("Hide the icons on:"), row)

        box = QGroupBox(tr("How it is done"))
        form = QFormLayout(box)
        layout.addWidget(box)

        self.use_helper = QCheckBox(tr("Hide with a helper widget on the desktop (lighter)"))
        self.use_helper.setChecked(settings.value("use_helper", True, bool))
        self.use_helper.setToolTip(tr(
            "On: an invisible widget on the desktop makes the icons go and come. That is at "
            "once, costs no memory and writes nothing to disk; fading, hiding widgets and the "
            "double-click need it.\n"
            "Off: Tidy swaps the desktop's folder for an empty one and lays an invisible "
            "window over the desktop for your click. That needs nothing inside Plasma.\n"
            "Tidy also falls back on the second way by itself when the helper does not work."))
        self.use_helper.toggled.connect(self.update_enabled)
        form.addRow(self.use_helper)

        self.fade_icons = QCheckBox(tr("Fade the icons in and out"))
        self.fade_icons.setChecked(settings.value("fade_icons", False, bool))
        self.fade_icons.setToolTip(tr("Needs the helper widget on the desktop."))
        self.fade_icons.toggled.connect(self.update_enabled)
        self.fade_duration = QSpinBox(suffix=" ms", minimum=50, maximum=3000, singleStep=50)
        self.fade_duration.setValue(settings.value("fade_duration", 300, int))
        row = QHBoxLayout()
        row.addWidget(self.fade_icons)
        row.addWidget(self.fade_duration)
        row.addStretch()
        form.addRow(row)

        layout.addStretch()

        # --- panel: what is about the panel as a whole ---
        panel_layout = QVBoxLayout(panel_tab)
        box = QGroupBox(tr("A panel that hides"))
        form = QFormLayout(box)
        panel_layout.addWidget(box)
        self.panel_after = QComboBox()
        for key, label in PANEL_AFTERS:
            self.panel_after.addItem(tr(label), key)
        self.panel_after.setCurrentIndex(max(0, self.panel_after.findData(
            settings.value("panel_after", PANEL_AFTER_NEVER))))
        self.panel_after.setToolTip(tr(
            "A panel that is hidden, by Tidy or by itself, comes into view when you put a "
            "window away, so you can go straight to the next program. It goes again after "
            "the time on the Desktop tab, and stays while the pointer is on it."))
        form.addRow(tr("Show the panel again:"), self.panel_after)

        panel_layout.addWidget(self.drawer_tab.tips_box)
        panel_layout.addStretch()

        # --- general ---
        form = QFormLayout(general_tab)
        self.autostart = QCheckBox(tr("Start at login"))
        self.autostart.setChecked(os.path.exists(AUTOSTART))
        form.addRow(self.autostart)

        self.language = QComboBox()
        for key, label in LANGUAGES:
            self.language.addItem(tr(label), key)
        self.language.setCurrentIndex(
            max(0, self.language.findData(settings.value("language", "auto"))))
        form.addRow(tr("Language:"), self.language)

        self.peek_key = QKeySequenceEdit(QKeySequence(settings.value("peek_key", "")))
        self.peek_key.setClearButtonEnabled(True)
        self.peek_key.setMaximumSequenceLength(1)
        self.peek_key.setToolTip(tr("While you hold this key, the desktop icons and everything "
                                    "in the drawers are shown; let go and they are away again. "
                                    "Works in focus mode too."))
        form.addRow(tr("Hold to peek:"), self.peek_key)
        self.peek_warning = QLabel(tr("This key has no Ctrl, Alt or Meta with it. While Tidy "
                                      "runs it would no longer work in any program, not for "
                                      "typing or moving either. Better choose a combination, "
                                      "such as Meta+Z."))
        self.peek_warning.setWordWrap(True)
        self.peek_warning.setStyleSheet("color: #da4453;")
        self.general_form = form
        form.addRow("", self.peek_warning)
        self.peek_key.keySequenceChanged.connect(self.update_enabled)
        self.peek_panel = QCheckBox(tr("A peek also shows the panel, on top of your windows"))
        self.peek_panel.setChecked(settings.value("peek_panel", True, bool))
        self.peek_panel.setToolTip(tr("A panel that hides by itself or sits behind a window "
                                      "comes into view while you hold the key. Your windows "
                                      "keep their size. A program in full screen stays on top "
                                      "of the panel."))
        form.addRow(self.peek_panel)

        hint = QLabel(tr("Shortcuts: System Settings → Keyboard → Shortcuts → Add New → "
                         "Application… → Tidy. There you can give a key to showing and hiding "
                         "the icons, switching Tidy on or off, focus mode, opening or closing "
                         "the drawers, and restoring everything."))
        hint.setWordWrap(True)
        hint.setEnabled(False)
        form.addRow(hint)

        box = QGroupBox(tr("Profiles"))
        box_layout = QVBoxLayout(box)
        note = QLabel(tr("A profile keeps all settings together: desktop, drawers, system tray "
                         "and focus mode. Switch between them here or in the tray menu."))
        note.setWordWrap(True)
        box_layout.addWidget(note)
        row = QHBoxLayout()
        self.profile = QComboBox()
        self.profile.setProperty("tidyNoSetting", True)
        self.profile.addItems(sorted(autohide.profiles()))
        row.addWidget(self.profile, 1)
        self.profile_apply = QPushButton(tr("Apply"))
        self.profile_apply.clicked.connect(
            lambda: autohide.apply_profile(self.profile.currentText()))
        row.addWidget(self.profile_apply)
        save = QPushButton(QIcon.fromTheme("document-save"), tr("Save current as…"))
        save.clicked.connect(self.save_profile)
        row.addWidget(save)
        self.profile_delete = QPushButton(QIcon.fromTheme("edit-delete"), tr("Delete"))
        self.profile_delete.clicked.connect(self.delete_profile)
        row.addWidget(self.profile_delete)
        box_layout.addLayout(row)
        form.addRow(box)
        self.update_profiles()

        box = QGroupBox(tr("All settings"))
        row = QHBoxLayout(box)
        export = QPushButton(QIcon.fromTheme("document-export"), tr("Export…"))
        export.setToolTip(tr("Saves all settings and profiles in a file."))
        export.clicked.connect(self.export_settings)
        row.addWidget(export)
        import_ = QPushButton(QIcon.fromTheme("document-import"), tr("Import…"))
        import_.setToolTip(tr("Reads settings and profiles from a file and applies them."))
        import_.clicked.connect(self.import_settings)
        row.addWidget(import_)
        defaults = QPushButton(QIcon.fromTheme("edit-reset"), tr("Defaults…"))
        defaults.setToolTip(tr("Puts every setting back to how Tidy comes. Your drawers stay, "
                               "with what is in them; the system tray is left alone."))
        defaults.clicked.connect(self.reset_defaults)
        row.addWidget(defaults)
        row.addStretch()
        welcome = QPushButton(tr("Welcome window…"))
        welcome.setToolTip(tr("Shows the window from the first start again, with the choices "
                              "to begin with."))
        welcome.clicked.connect(autohide.welcome)
        row.addWidget(welcome)
        restore = QPushButton(QIcon.fromTheme("edit-undo"), tr("Restore everything…"))
        restore.setToolTip(tr("Shows everything again, puts back the Plasma settings that Tidy "
                              "changed, and switches Tidy off."))
        restore.clicked.connect(lambda: autohide.ask_restore(self))
        row.addWidget(restore)
        form.addRow(box)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                           | QDialogButtonBox.StandardButton.Apply
                                           | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        # Apply: use the settings without closing the window. Available once something changed.
        self.changed = False
        self.apply_button = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        self.apply_button.clicked.connect(lambda: autohide.apply_settings(self))
        self.apply_button.setText(tr("Apply"))
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        footer = QHBoxLayout()
        support = QLabel("<a href='#'>" + tr("♥ Support {app}").format(app=APP_NAME) + "</a>")
        support.setToolTip(tr("Donate or more information"))
        support.linkActivated.connect(self.on_support)
        footer.addWidget(support)
        footer.addStretch()
        footer.addWidget(self.button_box)
        outer.addLayout(footer)

        self.back.currentIndexChanged.connect(self.update_enabled)
        self.update_enabled()

        # The countdown on the Desktop tab: only kept up while that tab is in view. (It asks
        # Plasma each time whether you are editing the desktop.)
        self.ticker = QTimer(self, interval=200)
        self.ticker.timeout.connect(self.update_status)
        self.tabs.currentChanged.connect(self.update_ticker)
        self.update_ticker()

        self.drawer_tab.rebuilt = self.watch_changes
        self.watch_changes(self)
        self.update_enabled()

        # As tall as the tallest tab asks for, as far as the screen has room: in less the
        # Drawers tab scrolls. (Left to itself Qt opens a window at two thirds of the screen.)
        wanted = self.sizeHint()
        screen = QApplication.primaryScreen()
        room = screen.availableGeometry().height() - 80 if screen else wanted.height()
        self.resize(wanted.width(), min(wanted.height(), room))

    def watch_changes(self, root):
        """Notice every change to a setting below this widget; called again for the drawer
        pages when they are rebuilt."""
        for widget in root.findChildren(QWidget):
            if widget.property("tidyWatched") or widget.property("tidyNoSetting"):
                continue
            if isinstance(widget, QComboBox):
                signal = widget.currentIndexChanged
                if widget.isEditable():
                    widget.editTextChanged.connect(self.mark_changed)
            elif isinstance(widget, QTimeEdit):
                signal = widget.timeChanged
            elif isinstance(widget, QCheckBox):
                signal = widget.toggled
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                signal = widget.valueChanged
            elif isinstance(widget, QKeySequenceEdit):
                signal = widget.keySequenceChanged
            elif isinstance(widget, QLineEdit):
                signal = widget.textEdited
            else:
                continue
            signal.connect(self.mark_changed)
            widget.setProperty("tidyWatched", True)

    def mark_changed(self, *_):
        self.changed = True
        self.update_enabled()

    def applied(self):
        """The settings in the window are the ones in use now."""
        self.changed = False
        self.update_enabled()

    def on_support(self, _link):
        # With a donation page: go straight there. Otherwise to the About tab.
        if DONATE_URL:
            open_donate()
        else:
            self.tabs.setCurrentWidget(self.about_tab)

    def update_enabled(self):
        # What only goes with a click is out of sight for the other choice.
        click = self.chosen_mode() == MODE_CLICK
        self.back_form.setRowVisible(self.buttons_row, click)
        self.back_form.setRowVisible(self.rehide, click)
        # In click mode at least one button must be chosen.
        valid = not click or any(b.isChecked() for b in self.buttons.values())
        helper = self.use_helper.isChecked()
        for box in (self.double_hides, self.hide_widgets, self.fade_icons):
            box.setEnabled(helper)
        self.fade_duration.setEnabled(helper and self.fade_icons.isChecked())
        self.panel_counts.setEnabled(self.only_desktop.isChecked())
        self.general_form.setRowVisible(self.peek_warning, bare_key(self.peek_key.keySequence()))
        for box in self.widget_boxes.values():
            box.setEnabled(helper and self.hide_widgets.isChecked())
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(valid)
        self.apply_button.setEnabled(valid and self.changed)

    def update_ticker(self, *_):
        if self.tabs.currentIndex() == 0:
            self.update_status()
            self.ticker.start()
        else:
            self.ticker.stop()

    def update_status(self):
        a = self.autohide
        remaining = a.remaining()
        total = a.settings.value("timeout", 10, int)
        if a.focus:
            self.status_label.setText(tr("Focus mode — everything stays away until you switch "
                                         "it off"))
            self.bar.setValue(0)
            self.bar.setFormat("—")
        elif not a.enabled_action.isChecked():
            self.status_label.setText(tr("Disabled"))
            self.bar.setValue(0)
            self.bar.setFormat("—")
        elif a.hidden:
            self.status_label.setText(
                tr("Hidden — waiting for a click on the desktop") if a.mode() == MODE_CLICK
                else tr("Hidden — waiting for mouse movement or a key press"))
            self.bar.setValue(0)
            self.bar.setFormat("0 s")
        elif a.busy():
            self.status_label.setText(tr("Paused — menu open or Plasma in edit mode"))
            self.bar.setValue(1000)
            self.bar.setFormat(tr("paused"))
        else:
            self.status_label.setText(tr("Visible — hiding in:"))
            self.bar.setValue(int(1000 * remaining / total))
            self.bar.setFormat(f"{remaining:.0f} s")

    def chosen_mode(self):
        return self.back.currentData().split(":")[0]

    def chosen_clicks(self):
        return self.back.currentData().split(":")[1]

    def chosen_buttons(self):
        return ",".join(k for k, b in self.buttons.items() if b.isChecked())

    # --- profiles, export and import (General tab) ---

    def update_profiles(self):
        some = self.profile.count() > 0
        self.profile.setEnabled(some)
        self.profile_apply.setEnabled(some)
        self.profile_delete.setEnabled(some)

    def save_profile(self):
        name, ok = QInputDialog.getText(self, APP_NAME, tr("Name of the profile:"),
                                        text=self.profile.currentText())
        name = name.strip()
        if not ok or not name:
            return
        # What is in the window now is what gets saved.
        self.autohide.apply_settings(self)
        self.autohide.save_profile(name)
        if self.profile.findText(name) < 0:
            self.profile.addItem(name)
        self.profile.setCurrentText(name)
        self.update_profiles()
        self.rules_tab.fill_profiles()

    def delete_profile(self):
        self.autohide.delete_profile(self.profile.currentText())
        self.profile.removeItem(self.profile.currentIndex())
        self.update_profiles()
        self.rules_tab.fill_profiles()

    def export_settings(self):
        name, _ = QFileDialog.getSaveFileName(
            self, tr("Export settings"), os.path.expanduser(f"~/{APP}-settings.json"),
            "(*.json)")
        if not name:
            return
        self.autohide.apply_settings(self)
        data = self.autohide.export_data()
        try:
            with open(name, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as error:
            QMessageBox.warning(self, APP_NAME, str(error))

    def import_settings(self):
        name, _ = QFileDialog.getOpenFileName(
            self, tr("Import settings"), os.path.expanduser("~"), "(*.json)")
        if not name:
            return
        try:
            with open(name) as f:
                data = json.load(f)
            if not isinstance(data, dict) or data.get("app") != APP:
                raise ValueError
        except (OSError, ValueError):
            QMessageBox.warning(self, APP_NAME, tr("This is not a file with Tidy settings."))
            return
        self.autohide.import_snapshot(data)

    def reset_defaults(self):
        answer = QMessageBox.question(
            self, APP_NAME, tr("Put every setting back to how Tidy comes?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        if answer == QMessageBox.StandardButton.Yes:
            self.autohide.reset_defaults()

    def skipped_screens(self):
        """Screens whose icons stay; one that is not connected now keeps its choice."""
        names = [n for n in self.skipped if n not in self.screens]
        names += [n for n, box in self.screens.items() if not box.isChecked()]
        return ",".join(names)
