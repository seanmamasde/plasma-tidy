# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tidy's commands on D-Bus: for shortcuts, the helpers and a second invocation."""

import json

from PyQt6.QtCore import QTimer, pyqtClassInfo, pyqtSignal, pyqtSlot
from PyQt6.QtDBus import QDBusAbstractAdaptor

from .consts import DBUS_NAME


@pyqtClassInfo("D-Bus Interface", DBUS_NAME)
class DBusAdaptor(QDBusAbstractAdaptor):
    """Commands from outside: shortcuts, the screen corner, a second invocation. And what
    Tidy tells its widgets in Plasma, as signals: they listen, nothing is written anywhere."""

    # How the desktop should be, as JSON: for the helpers on the desktops.
    DesktopState = pyqtSignal(str)
    # Tidy has started and listens: the helpers answer by reporting themselves.
    Started = pyqtSignal()
    # A peek starts or ends: for the drawers.
    Peeking = pyqtSignal(bool)
    # The desktop came to the front: for the drawers that open then.
    DesktopActivated = pyqtSignal()
    # A menu or pop-up opens somewhere, or the last one closes: a drawer stays open with it.
    MenuOpen = pyqtSignal(bool)
    # A panel slid out of view, on this screen and this edge: a drawer in it may close.
    PanelGone = pyqtSignal(str, str)

    def __init__(self, autohide):
        super().__init__(autohide)
        self.autohide = autohide

    @pyqtSlot()
    def Show(self):
        if not self.autohide.hold_icons:  # in focus mode the icons stay away
            self.autohide.show()

    @pyqtSlot()
    def Hide(self):
        self.autohide.hide()

    @pyqtSlot(bool)
    def DesktopActive(self, active):
        self.autohide.on_desktop_active(active)

    @pyqtSlot()
    def DesktopMotion(self):
        self.autohide.on_desktop_motion()

    @pyqtSlot(bool)
    def PopupOpen(self, open_):
        self.autohide.popup_open = open_
        self.MenuOpen.emit(open_)

    @pyqtSlot(str)
    def WindowGone(self, how):
        self.autohide.on_window_gone(how)

    @pyqtSlot(bool)
    def PanelPointer(self, on):
        self.autohide.on_panel_pointer(on)

    @pyqtSlot(str, str)
    def PanelHidden(self, screen, edge):
        self.PanelGone.emit(screen, edge)

    # What the widgets and the KWin script find of what they reach into.
    @pyqtSlot(str, str)
    def DrawerCheck(self, drawer, found):
        self.autohide.on_check("drawer", drawer, found)

    @pyqtSlot(str, str)
    def HelperCheck(self, desktop, found):
        self.autohide.on_check("helper", desktop, found)

    @pyqtSlot(str)
    def KWinCheck(self, found):
        self.autohide.on_check("kwin", "", found)

    # For a program that keeps Tidy's settings along with a desktop (Modish): every choice as
    # one piece of JSON, what Export in the settings window writes, and the way back in.
    @pyqtSlot(result=str)
    def ExportSettings(self):
        return json.dumps(self.autohide.export_data(), ensure_ascii=False)

    @pyqtSlot(str, result=str)
    def ImportSettings(self, text):
        return self.autohide.import_text(text)

    @pyqtSlot(result=str)
    def Check(self):
        return self.autohide.check_report()

    @pyqtSlot(str, bool)
    def ActiveWindow(self, name, fullscreen):
        self.autohide.on_active_window(name, fullscreen)

    @pyqtSlot(str)
    def WindowClasses(self, names):
        self.autohide.on_window_classes([n for n in names.split("\n") if n])

    @pyqtSlot(int, str)
    def VirtualDesktop(self, number, names):
        self.autohide.on_virtual_desktop(number, names.split("\n") if names else [])

    @pyqtSlot(str)
    def HelperReady(self, desktop):
        self.autohide.on_helper_ready(desktop)

    @pyqtSlot()
    def DesktopClick(self):
        self.autohide.on_desktop_click()

    @pyqtSlot()
    def DesktopDoubleClick(self):
        self.autohide.on_desktop_double_click()

    @pyqtSlot()
    def Welcome(self):
        QTimer.singleShot(0, self.autohide.welcome)

    @pyqtSlot()
    def Peek(self):
        self.autohide.peek(None)

    @pyqtSlot()
    def Toggle(self):
        self.autohide.enabled_action.toggle()

    @pyqtSlot()
    def Settings(self):
        # Through the event loop, so the D-Bus call doesn't wait until the window closes.
        QTimer.singleShot(0, self.autohide.show_settings)

    @pyqtSlot()
    def DrawerOpen(self):
        self.autohide.plasma.set_drawers_closed(False)

    @pyqtSlot()
    def DrawerClose(self):
        self.autohide.plasma.set_drawers_closed(True)

    @pyqtSlot()
    def DrawerToggle(self):
        self.autohide.plasma.set_drawers_closed(None)

    @pyqtSlot()
    def Restore(self):
        self.autohide.restore_everything()

    @pyqtSlot()
    def Focus(self):
        self.autohide.focus_action.toggle()
