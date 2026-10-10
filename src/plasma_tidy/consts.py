# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Names, places and defaults that the rest of Tidy uses."""

import os

from PyQt6.QtCore import Qt

APP = "plasma-tidy"
APP_NAME = "Tidy"
OLD_APP = "autohide-desktop-icons"  # previous name, for carrying over its settings
VERSION = "0.3.5"
AUTHOR = "Ivar"
BRAND = "Wispware"
DESCRIPTION = "Keeps your KDE Plasma desktop, panel and system tray clean."
# Where one of these is empty, the About tab shows a placeholder.
LICENSE = "GPL-3.0-or-later"
WEBSITE_URL = "https://github.com/wispware/plasma-tidy"
BUGS_URL = WEBSITE_URL + "/issues"
DONATE_URL = "https://ko-fi.com/wispware"
DBUS_NAME = "io.github.wispware.PlasmaTidy"
DATA_DIR = os.path.expanduser(f"~/.local/share/{APP}")
EMPTY_DIR = os.path.join(DATA_DIR, "empty")
EMPTY_URL = "file://" + EMPTY_DIR
KWIN_SCRIPT = os.path.join(DATA_DIR, "kwin-helper.js")
KWIN_SCRIPT_NAME = APP + "-helper"
AUTOSTART = os.path.expanduser(f"~/.config/autostart/{APP}.desktop")
CATCHER_PREFIX = "tidy-catcher:"
IDLE_STEP = 1  # seconds of stillness before swayidle reports "idle"
IDLE_LINK = os.path.join(DATA_DIR, "tidy-idle")
DRAWER_ID = "io.github.wispware.plasmatidy.drawer"
# Tidy's own icons: the application, and the two of the system tray (one colour, which
# Plasma gives the theme's text colour).
APP_ICON = "io.github.wispware.PlasmaTidy"
# (A name like "plasma-tidy-symbolic" would not do: an icon theme also tries it shortened, and
# Breeze has "plasma-symbolic", which would then be taken first.)
TRAY_ICON = f"{APP_ICON}-symbolic"
TRAY_ICON_HIDDEN = f"{APP_ICON}-hidden-symbolic"
ICON_DIR = os.path.expanduser("~/.local/share/icons/hicolor")
SYSTEM_ICON = f"/usr/share/icons/hicolor/scalable/apps/{APP_ICON}.svg"  # from the package
DRAWER_DIR = os.path.expanduser(f"~/.local/share/plasma/plasmoids/{DRAWER_ID}")
FADE_ID = "io.github.wispware.plasmatidy.fade"
FADE_DIR = os.path.expanduser(f"~/.local/share/plasma/plasmoids/{FADE_ID}")
TASK_PLUGINS = ("org.kde.plasma.icontasks", "org.kde.plasma.taskmanager")
FOLDER_PLUGIN = "org.kde.plasma.folder"   # Plasma's Folder View, for a folder in a drawer
# Widgets that never go into a drawer: separators, spacers and the drawers themselves.
DRAWER_SKIP = ("org.kde.plasma.marginsseparator", "org.kde.plasma.panelspacer", DRAWER_ID)
TASKS_ALL = "all"
TASKS_PINNED = "pinned"
OPEN_CLICK = "click"
OPEN_HOVER = "hover"
SCOPE_DRAWER = "drawer"
SCOPE_PANEL = "panel"
MARK_NONE = "none"
MARK_OPEN = "open"
MARK_COUNT = "count"
MARK_ATTENTION = "attention"
PLACE_BEFORE = "before"
PLACE_AFTER = "after"
PLACE_MANUAL = "manual"
DISPLAY_PANEL = "panel"
DISPLAY_POPUP = "popup"
# The drawer's settings and their defaults (the same as in DRAWER_CONFIG_XML).
DRAWER_DEFAULTS = {"closed": False, "paused": False, "name": "", "targets": [],
                   "taskMode": TASKS_ALL, "taskKeep": [], "taskList": "", "openOn": OPEN_CLICK,
                   "display": DISPLAY_PANEL, "popupStyle": "row", "popupPlace": "arrow",
                   "popupBackground": True,
                   "popupGap": True, "trayArrow": "open", "arrowTip": True, "arrowSlim": False,
                   "arrowSlimMark": True, "taskTips": True, "balloons": True,
                   "taskBare": False, "taskClose": True, "taskGap": False,
                   "tipGap": False,
                   "fitPanel": False,
                   "hoverDelay": 200, "autoClose": False, "closeDelay": 2000, "keepPanel": 0,
                   "closeScope": SCOPE_DRAWER, "closeOnPanelClick": False,
                   "openOnPanelClick": False, "panelClick": "left", "iconLarge": False,
                   "closeAfterUse": False, "useDelay": 400, "closeOnPanelHide": True,
                   "closeOnMaximized": False, "openOnDesktop": False,
                   "icon": "arrow", "iconCustom": "",
                   "openOnAttention": True, "reverseArrow": False,
                   "animation": "slide", "animationDuration": 250, "activePlace": "fixed", "moveStyle": "glide",
                   "indicator": MARK_OPEN,
                   "place": PLACE_BEFORE}
MODE_ACTIVITY = "activity"
MODE_CLICK = "click"
REHIDE_IDLE = "idle"
REHIDE_FIXED = "fixed"
BUTTONS = {"left": Qt.MouseButton.LeftButton,
           "right": Qt.MouseButton.RightButton,
           "middle": Qt.MouseButton.MiddleButton}
# The texts in these tables are English (the source language); tr() translates them on display.
CORNERS = [("none", "None", None),
           ("topleft", "Top left", "KWin.ElectricTopLeft"),
           ("topright", "Top right", "KWin.ElectricTopRight"),
           ("bottomleft", "Bottom left", "KWin.ElectricBottomLeft"),
           ("bottomright", "Bottom right", "KWin.ElectricBottomRight")]
PANEL_NAMES = {
    "org.kde.plasma.kickoff": "Application launcher",
    "org.kde.plasma.kicker": "Application menu",
    "org.kde.plasma.kickerdash": "Application dashboard",
    "org.kde.plasma.pager": "Virtual desktops",
    "org.kde.plasma.icontasks": "Task manager (icons)",
    "org.kde.plasma.taskmanager": "Task manager",
    "org.kde.plasma.systemtray": "System tray",
    "org.kde.plasma.digitalclock": "Clock",
    "org.kde.plasma.showdesktop": "Show desktop",
    "org.kde.plasma.minimizeall": "Minimize all",
    "org.kde.plasma.quicklaunch": "Quick launch",
    "org.kde.plasma.icon": "Program icon",
    "org.kde.plasma.trash": "Trash",
    "org.kde.plasma.folder": "Folder",
    "org.kde.plasma.appmenu": "Global menu",
    "org.kde.plasma.mediacontroller": "Media controls",
    "org.kde.plasma.keyboardlayout": "Keyboard layout",
    "org.kde.plasma.weather": "Weather",
}
ANIMATIONS = [("slide", "Slide"), ("grow", "Grow"), ("cascade", "One by one"), ("fade", "Fade")]
DISPLAYS = [(DISPLAY_PANEL, "In the panel"), (DISPLAY_POPUP, "In a pop-up above the arrow")]
TASK_POPUPS = [("preview", "With a preview of the window"),
               ("only", "Only the preview of the window"), ("text", "Title and text only"),
               ("none", "None")]
TASK_POPUPS_PREVIEW = ("preview", "only")  # the ones the task manager shows a preview for
TRAY_ARROWS = [("open", "In the panel while the pop-up is open"),
               ("always", "Always in the panel"), ("never", "Never")]
POPUP_STYLES = [("row", "A row of icons"), ("column", "A column of icons"),
                ("grid", "A grid with names"), ("list", "A list with names"),
                ("stack", "A fan out of the arrow, with names")]
# ms the desktop is given to lay out its icons after a panel changes, before they fade in.
# Short: the fade starts from nothing, so what is left of the moving is not seen, and the
# panel and the icons come in together.
PANEL_SETTLE = 100
# The panel comes into view by itself, for the time it takes the icons to hide.
PANEL_AFTER_NEVER = "never"
PANEL_AFTER_MINIMIZE = "minimize"
PANEL_AFTER_CLOSE = "close"
PANEL_AFTERS = [(PANEL_AFTER_NEVER, "Never"), (PANEL_AFTER_MINIMIZE, "After minimising a window"),
                (PANEL_AFTER_CLOSE, "After minimising or closing a window")]
POPUP_PLACES = [("arrow", "Above the arrow"), ("start", "At the start of the panel"),
                ("middle", "In the middle of the panel"), ("end", "At the end of the panel")]
ACTIVE_PLACES = [("fixed", "On their pinned spot"), ("start", "All in front"),
                 ("end", "All at the back")]
MOVE_STYLES = [("glide", "Gliding"), ("fade", "Fading over")]
PANEL_CLICKS = [("left", "Left click"), ("middle", "Middle click"), ("ctrl", "Ctrl + click"),
                ("shift", "Shift + click"), ("alt", "Alt + click")]
ICON_STYLES = [("arrow", "Arrow"), ("double", "Double arrow"), ("triangle", "Triangle"),
               ("dots", "Dots"), ("menu", "Menu lines"), ("handle", "Grip"),
               ("custom", "My own icon"), ("none", "No icon")]
# Texts of the drawer's own settings page (DRAWER_CONFIG_QML); it gets them translated.
DRAWER_PAGE_TEXTS = [
    "Name:", "In this drawer", "Task manager:", "Hide all programs, open ones too",
    "Hide only pinned programs that are not open", "Opening and closing", "Open with:",
    "A click on the arrow", "Pointing at the arrow (a click works too)", "Pointing opens after:",
    "Open when a program asks for attention", "Open when the desktop is shown",
    "Works while Tidy is running.", "Close by itself:", "Never",
    "When the pointer leaves the drawer", "When the pointer leaves the panel", "Closes after:",
    "Close with a click on an empty spot in the panel",
    "Open with a click on an empty spot in the panel", "That click is:", "Left click",
    "Middle click", "Ctrl + click", "Shift + click", "Alt + click",
    "Shows its contents:", "In the panel", "In a pop-up above the arrow", "Pop-up:",
    "A row of icons", "A column of icons", "A grid with names", "A list with names",
    "A fan out of the arrow, with names", "As large as the icons of the panel",
    "Place of the pop-up:", "Above the arrow", "At the start of the panel",
    "In the middle of the panel", "At the end of the panel",
    "Pop-up has a background, like the panel",
    "Pop-up floats above the panel, like Plasma's own pop-ups",
    "The arrow shows a balloon when you point at it",
    "Without an icon the arrow takes no room in the panel",
    "Its room comes back while the mark has something to tell",
    "The system tray's own arrow (^):", "In the panel while the pop-up is open",
    "Always in the panel", "Never",
    "Close after a click on something in the drawer",
    "Panel stays after starting a program:", "Stays open after that click:",
    "Close when a window that fills the screen comes to the front",
    "Close when the panel slides out of view", "Appearance", "Icon:",
    "Open programs:", "On their pinned spot", "All in front", "All at the back", "Animation:",
    "It goes there:", "Gliding", "Fading over",
    "Slide", "Grow", "One by one", "Fade", "Speed:",
    "Double arrow", "Triangle", "Dots", "Menu lines", "Grip", "My own icon", "No icon",
    "Icon name or image file", "Mark on the closed drawer:", "None",
    "A dot when programs are open", "The number of open programs",
    "A dot only when a program asks for attention", "Arrow points the other way",
    "The place of the arrow is set in Tidy."]
PANEL_PLACES = {"top": "Top panel", "bottom": "Bottom panel", "left": "Left panel",
                "right": "Right panel"}
# Tidy's own settings that belong to a profile or an export, with their defaults.
PROFILE_SETTINGS = {"timeout": 10, "mode": "activity", "buttons": "left,right,middle",
                    "rehide": "idle", "corner": "none", "only_desktop": True,
                    "panel_counts": True, "clicks": "single", "double_hides": False,
                    "hide_widgets": False, "widgets_keep": "", "use_helper": True,
                    "hide_panel": False, "panel_after": "never", "skip_screens": "",
                    "fade_icons": False,
                    "fade_duration": 300, "drawer_follow": False,
                    "focus_icons": True, "focus_drawers": True, "focus_tray": True,
                    "focus_panel": False, "tray_hide_new": False, "tray_rules": "",
                    "peek_key": "", "peek_panel": True, "balloons": True,
                    "task_popup": "preview", "task_close": True,
                    "task_gap": False, "balloon_gap": False}
# What a drawer is doing right now; not part of a profile.
DRAWER_STATE = ("closed", "paused", "taskList", "fitPanel", "taskTips", "balloons", "taskBare",
                "taskClose", "taskGap", "tipGap")
# Rules: when something is the case, use a profile or switch focus mode on.
RULE_WHEN = [("battery", "On battery"), ("mains", "On mains power"),
             ("external", "An external screen is connected"),
             ("time", "Between these times"),
             ("app", "This program is in front"),
             ("fullscreen", "A program fills the whole screen"),
             ("vdesktop", "On this virtual desktop"),
             ("activity", "In this activity")]
RULE_FOCUS = "focus"
RULE_PROFILE = "profile"
RULE_NIGHT_LIGHT = "nightlight"
CLICKS_SINGLE = "single"
CLICKS_DOUBLE = "double"
PEEK_ACTION = [APP, "peek", APP_NAME, "Peek: show everything while held"]
TRAY_AUTO = "auto"
TRAY_SHOWN = "shown"
TRAY_HIDDEN = "hidden"
TRAY_DISABLED = "disabled"
TRAY_MODES = [(TRAY_AUTO, "Automatic", "Only visible when relevant"),
              (TRAY_SHOWN, "Show", "Always visible in the panel"),
              (TRAY_HIDDEN, "Hide", "Only reachable through the ^ arrow"),
              (TRAY_DISABLED, "Off", "Switched off completely")]
TRAY_NAMES = {
    "org.kde.plasma.battery": "Battery",
    "org.kde.plasma.bluetooth": "Bluetooth",
    "org.kde.plasma.brightness": "Brightness",
    "org.kde.plasma.cameraindicator": "Camera indicator",
    "org.kde.plasma.clipboard": "Clipboard",
    "org.kde.plasma.devicenotifier": "Devices (USB)",
    "org.kde.plasma.keyboardindicator": "Caps Lock indicator",
    "org.kde.plasma.keyboardlayout": "Keyboard layout",
    "org.kde.plasma.manage-inputmethod": "Input method",
    "org.kde.plasma.networkmanagement": "Network (Wi-Fi)",
    "org.kde.plasma.notifications": "Notifications",
    "org.kde.plasma.printmanager": "Printers",
    "org.kde.plasma.vault": "Vaults",
    "org.kde.plasma.weather": "Weather",
    "org.kde.kscreen": "Displays",
    "org.kde.plasma.mediacontroller": "Media controls",
    "org.kde.plasma.volume": "Volume",
    "org.kde.kdeconnect": "KDE Connect",
    "Discover Notifier_org.kde.DiscoverNotifier": "Discover (updates)",
    "Xwayland Video Bridge": "Xwayland screen sharing",
    "spotify-client": "Spotify",
    APP: "Tidy (this program)",
}
# "Minimal" preset: only the essentials visible, the rest under ^.
TRAY_MINIMAL_SHOWN = ["org.kde.plasma.networkmanagement", "org.kde.plasma.volume",
                      "org.kde.plasma.battery"]
TRAY_MINIMAL_AUTO = ["org.kde.plasma.notifications", "org.kde.plasma.devicenotifier",
                     "org.kde.plasma.cameraindicator", "org.kde.plasma.keyboardindicator"]
