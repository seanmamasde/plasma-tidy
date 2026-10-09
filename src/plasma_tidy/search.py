# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Search in the settings window: type a word, pick a setting, and the window goes there."""

from PyQt6.QtCore import QEvent, QStringListModel, Qt, QTimer
from PyQt6.QtWidgets import (QAbstractButton, QCheckBox, QComboBox, QCompleter, QFormLayout,
                             QFrame, QGroupBox, QLabel, QLineEdit, QPushButton, QRadioButton,
                             QScrollArea, QStackedWidget, QTabWidget, QWidget)

from .i18n import tr

SEPARATOR = "   —   "
MOST_CHOICES = 8   # a list with more than this (programs, icons) is not a list of settings


def clean(text):
    return text.replace("&", "").rstrip(":").strip()


def place(widget, top):
    """Where a widget sits: the names of its tabs and groups, and the tabs to open to get
    there. None for a widget on a page that is not the one in view (another drawer)."""
    trail, steps = [], []
    w = widget
    while w is not None and w is not top:
        parent = w.parentWidget()
        if isinstance(parent, QStackedWidget):
            owner = parent.parentWidget()
            if isinstance(owner, QTabWidget):
                index = owner.indexOf(w)
                trail.append(clean(owner.tabText(index)))
                steps.append((owner, index))
            elif parent.currentWidget() is not w:
                return None
        elif isinstance(w, QGroupBox) and w is not widget and w.title():
            trail.append(clean(w.title()))
        w = parent
    return list(reversed(trail)), list(reversed(steps))


def first_widget(item):
    """The first widget of a form row, which can be a widget or a row of them."""
    if isinstance(item, QWidget):
        return item
    for i in range(item.count() if item is not None else 0):
        inner = item.itemAt(i)
        found = inner.widget() or (first_widget(inner.layout()) if inner.layout() else None)
        if found is not None:
            return found
    return None


def entries(top):
    """Everything in the window that can be searched for: [(text shown, widget, steps)]."""
    found, seen = [], set()

    def add(text, widget, extra=()):
        text = clean(text)
        where = place(widget, top) if text and not widget.isHidden() else None
        if where is None:
            return
        trail, steps = where
        shown = text + SEPARATOR + " › ".join(trail + list(extra))
        if shown not in seen:
            seen.add(shown)
            found.append((shown, widget, steps))

    for form in top.findChildren(QFormLayout):
        for row in range(form.rowCount()):
            label = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
            field = form.itemAt(row, QFormLayout.ItemRole.FieldRole)
            if not label or not isinstance(label.widget(), QLabel) or not field:
                continue
            widget = first_widget(field.widget() or field.layout())
            if widget is None or not form.isRowVisible(row):
                continue
            name = label.widget().text()
            add(name, widget)
            if isinstance(widget, QComboBox) and widget.count() <= MOST_CHOICES \
                    and not widget.property("tidyNoSetting"):
                for i in range(widget.count()):
                    add(widget.itemText(i), widget, extra=[clean(name)])
    for kind in (QCheckBox, QRadioButton, QPushButton):
        for button in top.findChildren(kind):
            if isinstance(button, QAbstractButton) and not button.property("tidyNoSearch"):
                add(button.text(), button)
    return found


def reveal(widget, steps):
    """Open the tabs that lead to the widget, scroll to it and mark it for a moment."""
    for tabs, index in steps:
        tabs.setCurrentIndex(index)

    def mark():
        w = widget.parentWidget()
        while w is not None:
            if isinstance(w, QScrollArea):
                w.ensureWidgetVisible(widget, 40, 60)
            w = w.parentWidget()
        window = widget.window()
        frame = QFrame(window)
        frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        colour = window.palette().highlight().color().name()
        frame.setStyleSheet(f"QFrame {{ border: 2px solid {colour}; border-radius: 5px; }}")
        corner = widget.mapTo(window, widget.rect().topLeft())
        frame.setGeometry(corner.x() - 5, corner.y() - 4, widget.width() + 10, widget.height() + 8)
        frame.show()
        frame.raise_()
        QTimer.singleShot(1800, frame.deleteLater)
        widget.setFocus(Qt.FocusReason.OtherFocusReason)

    QTimer.singleShot(60, mark)   # after the tab has laid itself out


class SearchBox(QLineEdit):
    """The search field of the settings window."""

    def __init__(self, top):
        super().__init__()
        self.top = top
        self.found = {}
        self.setPlaceholderText(tr("Search the settings…"))
        self.setClearButtonEnabled(True)
        self.setProperty("tidyNoSetting", True)   # typing here changes no setting
        self.model = QStringListModel(self)
        completer = QCompleter(self.model, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setMaxVisibleItems(12)
        completer.activated[str].connect(self.go)
        self.setCompleter(completer)
        self.textEdited.connect(self.refresh)

    def refresh(self, _text=""):
        # Read anew each time: drawers come and go, and rows show and hide with a choice.
        self.found = {shown: (widget, steps) for shown, widget, steps in entries(self.top)}
        self.model.setStringList(sorted(self.found, key=str.lower))

    def go(self, shown):
        if shown in self.found:
            reveal(*self.found[shown])
        QTimer.singleShot(0, self.clear)

    def event(self, event):
        # Enter belongs to the search, not to the window's OK button.
        if event.type() == QEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Return,
                                                                    Qt.Key.Key_Enter):
            event.accept()
            return True
        return super().event(event)
