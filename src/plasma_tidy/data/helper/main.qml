// SPDX-FileCopyrightText: 2026 Ivar
// SPDX-License-Identifier: GPL-3.0-or-later
//
// Tidy's helper on the desktop: sits there unseen and does what cannot be done from outside
// Plasma. When Tidy says so it makes the desktop icons go and come, with a fade if you like,
// and the widgets on the desktop with them. While the icons are away it catches the click
// that brings them back, and it tells Tidy about a double-click on an empty spot.
//
// Tidy tells how things should be with a signal on the session bus; nothing is written to
// Plasma's settings for it. When Tidy is not running, everything is simply in view.
//
// Plasma has no public way to do these things, so this reaches into the desktop it sits on:
// it changes how see-through the layer of icons and the widgets are, puts a click area on
// the desktop while the icons are away, and listens to the desktop's own "pressed" signal.
// Nothing else is touched; when the helper goes, everything is fully visible again.

import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

PlasmoidItem {
    id: root

    readonly property string tidy: "io.github.wispware.PlasmaTidy"
    readonly property var cfg: Plasmoid.configuration
    property Item icons: null     // the desktop's layer of icons
    property Item layout: null    // what the desktop's widgets sit in
    property int tries: 0
    property var bus: null        // the link with Tidy, made when the helper starts
    property bool tidyRuns: false

    // What Tidy asked for last. Without Tidy: nothing hidden.
    property var wish: ({})
    readonly property bool skipped: Array.from(wish.skip || []).indexOf(Screen.name) >= 0
    readonly property bool away: tidyRuns && wish.hidden === true && !skipped
    readonly property bool widgetsAlong: wish.widgets === true
    readonly property var keepIds: Array.from(wish.keep || []).map(String)
    readonly property bool editing: {
        try { return Plasmoid.containment.corona.editMode === true; } catch (e) { return false; }
    }

    property real level: 1        // 1: everything in view, 0: gone
    property bool iconsTaken: false
    property var taken: []        // widgets we made invisible
    property bool widgetsTouched: false   // the widgets' see-throughness is ours right now
    property double lastPress: 0

    preferredRepresentation: fullRepresentation
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    fullRepresentation: Item {}

    // The helper itself is never seen and never in the way of a click.
    Binding {
        target: root.parent; property: "visible"; value: false
        when: root.parent !== null
        restoreMode: Binding.RestoreBindingOrValue
    }

    function find() {
        var c = root.parent, hops = 0;
        while (c && hops < 10) {
            if (c.folderViewLayer !== undefined && c.folderViewLayer) {
                icons = c.folderViewLayer;
                layout = (c.appletsLayout !== undefined && c.appletsLayout) ? c.appletsLayout : null;
                connect();
                return;
            }
            c = c.parent;
            hops++;
        }
        if (++tries < 10) look.restart();
        else connect();  // not found: Tidy hears that too (see check())
    }
    Timer { id: look; interval: 700; onTriggered: root.find() }
    onParentChanged: look.restart()
    Component.onCompleted: look.restart()

    // --- the link with Tidy ---------------------------------------------------------------

    // Made by hand, so that a Plasma without this module leaves the helper standing (it then
    // does nothing, and Tidy hides the icons its other way).
    function connect() {
        if (bus) { ready(); return; }
        try {
            bus = Qt.createQmlObject('import QtQuick; import org.kde.plasma.workspace.dbus as DBus; '
                + 'QtObject { id: link; property string name; property bool runs: watch.registered; '
                + 'signal told(string text); signal started(); '
                + 'function call(member, args) { DBus.SessionBus.asyncCall({"service": name, '
                + '"path": "/", "iface": name, "member": member, "arguments": args}); } '
                + 'property var watch: DBus.DBusServiceWatcher { busType: DBus.BusType.Session; '
                + 'watchedService: link.name } '
                + 'property var listen: DBus.SignalWatcher { busType: DBus.BusType.Session; '
                + 'service: link.name; path: "/"; iface: link.name; '
                + 'function dbusDesktopState(text) { link.told(String(text)); } '
                + 'function dbusStarted() { link.started(); } '
                // Tidy's other signals are for the drawers. A signal without a function here
                // makes Plasma write a line in the log each time it comes.
                + 'function dbusPeeking(on) {} function dbusMenuOpen(on) {} '
                + 'function dbusPanelGone(screen, edge) {} function dbusDesktopActivated() {} } }',
                root, "tidyLink");
            bus.name = tidy;
            bus.told.connect(told);
            bus.started.connect(ready);
            bus.runsChanged.connect(runsChanged);
            runsChanged();
        } catch (e) {
            console.warn("TIDYHELPER cannot reach Tidy: " + e);
        }
    }
    function runsChanged() {
        tidyRuns = bus.runs;
        if (tidyRuns) ready();
        else wish = ({});   // Tidy is gone: everything back in view
    }
    // Tell Tidy that this desktop has a helper; it answers with how things should be.
    function ready() {
        if (bus && bus.runs && icons)
            bus.call("HelperReady", [String(Plasmoid.containment.id)]);
        check();
    }
    // What the helper found of the desktop it reaches into, for Tidy's look at itself.
    function check() {
        if (!bus || !bus.runs) return;
        var has = ok => ok ? "ok" : "missing";
        bus.call("HelperCheck", [String(Plasmoid.containment.id), JSON.stringify({
            icons: has(icons !== null),
            widgets: has(layout !== null),
            view: icons ? has(icons.view !== undefined && icons.view !== null) : "unused"
        })]);
    }
    function told(text) {
        try { wish = JSON.parse(text); } catch (e) { wish = ({}); }
        if (cfg.debug === "on") reportSoon.restart();
    }
    function tell(member, args) {
        try { if (bus && bus.runs) bus.call(member, args || []); } catch (e) {}
    }

    // --- going and coming -----------------------------------------------------------------

    function isOwn(c) {
        try { return c.applet.plasmoid.pluginName === Plasmoid.pluginName; } catch (e) { return false; }
    }
    function isKept(c) {
        try { return keepIds.indexOf(String(c.applet.plasmoid.id)) >= 0; } catch (e) { return false; }
    }
    // Bring the desktop in line with "level". While you edit the desktop everything is there.
    function apply() {
        var show = editing ? 1 : level;
        if (icons) {
            icons.opacity = show;
            if (show <= 0 && icons.visible) {
                // Out of sight is out of reach too: no click lands on an icon you cannot see.
                icons.visible = false;
                iconsTaken = true;
            } else if (show > 0 && iconsTaken) {
                icons.visible = true;
                iconsTaken = false;
            }
        }
        // The widgets: only gone through while they go along, and once more to put them
        // back when they no longer do.
        if (!layout || (!widgetsAlong && !widgetsTouched)) return;
        widgetsTouched = widgetsAlong;
        var kids = layout.children, still = [];
        for (var i = 0; i < kids.length; i++) {
            var c = kids[i];
            if (!c || c === icons || c.applet === undefined || !c.applet || isOwn(c)) continue;
            var mine = (widgetsAlong && !isKept(c)) ? show : 1;
            c.opacity = mine;
            if (mine > 0) {
                if (taken.indexOf(c) >= 0) c.visible = true;
            } else if (c.visible) {
                c.visible = false;
                still.push(c);
            } else if (taken.indexOf(c) >= 0) {
                still.push(c);
            }
        }
        taken = still;
    }
    onLevelChanged: apply()
    onEditingChanged: apply()
    onWidgetsAlongChanged: apply()
    onKeepIdsChanged: apply()
    onIconsChanged: { level = away ? 0 : 1; apply(); }

    NumberAnimation {
        id: fader
        target: root
        property: "level"
        easing.type: Easing.InOutQuad
    }
    onAwayChanged: {
        var to = away ? 0 : 1, time = Math.max(0, Number(wish.duration) || 0);
        fader.stop();
        // Tidy gone, or nothing to fade: at once.
        if (!tidyRuns || time <= 0 || !icons) { level = to; apply(); return; }
        fader.duration = time;
        fader.to = to;
        fader.start();
    }

    // --- the click that brings the icons back ------------------------------------------------

    // While the icons are away, a click on the desktop goes to this area and from there to
    // Tidy. It sits under the desktop's widgets and takes only the buttons you chose; any
    // other click does what it always did. The right button is never kept from the desktop:
    // it brings the icons back and opens the desktop's menu as well.
    Component {
        id: catcherComponent
        MouseArea {
            anchors.fill: parent
            z: -1
            visible: root.away && root.level <= 0 && root.wish["catch"] === true && !root.editing
            acceptedButtons: Number(root.wish.buttons) || Qt.NoButton
            onPressed: mouse => {
                if (root.wish["double"] !== true) root.tell("DesktopClick", []);
                if (mouse.button === Qt.RightButton) mouse.accepted = false;
            }
            onDoubleClicked: mouse => {
                if (root.wish["double"] === true) root.tell("DesktopClick", []);
            }
        }
    }
    property var catcher: null
    onLayoutChanged: {
        try { if (catcher) catcher.destroy(); } catch (e) {}
        catcher = layout ? catcherComponent.createObject(layout) : null;
    }

    // A double-click on an empty spot of the desktop hides the icons. The desktop tells when
    // it is pressed and which icon is under the pointer then; two presses on nothing,
    // shortly after each other, are a double-click.
    Connections {
        target: (root.wish.doubleHides === true && !root.away && root.icons && root.icons.view)
            ? root.icons.view : null
        ignoreUnknownSignals: true
        function onPressed() {
            var item = null;
            try { item = root.icons.view.hoveredItem; } catch (e) {}
            if (item && !item.blank) { root.lastPress = 0; return; }
            var now = Date.now();
            if (now - root.lastPress <= Qt.styleHints.mouseDoubleClickInterval) {
                root.lastPress = 0;
                root.tell("DesktopDoubleClick", []);
            } else {
                root.lastPress = now;
            }
        }
    }

    // --- for testing ------------------------------------------------------------------------

    function report() {
        var kids = layout ? layout.children : [], list = [];
        for (var i = 0; i < kids.length; i++) {
            var c = kids[i];
            if (c && c !== icons && c.applet !== undefined && c.applet && !isOwn(c))
                list.push(c.applet.plasmoid.pluginName + "#" + c.applet.plasmoid.id + "/o" + c.opacity
                          + (c.visible ? "" : "/hidden") + (isKept(c) ? "/kept" : ""));
        }
        console.warn("TIDYHELPER " + JSON.stringify({desktop: Plasmoid.containment.id,
            screen: Screen.name, tidyRuns: tidyRuns, away: away, level: level,
            icons: icons ? icons.opacity + (icons.visible ? "" : "/hidden") : null,
            widgets: list, editing: editing, view: !!(icons && icons.view),
            catcher: catcher ? catcher.visible + "/buttons" + catcher.acceptedButtons : null,
            wish: wish}));
    }
    Timer { id: reportSoon; interval: 600; onTriggered: root.report() }
    Connections {
        target: root.cfg
        function onDebugChanged() {
            var debug = String(root.cfg.debug);
            if (debug === "on") root.report();
            // As if the desktop were pressed on an empty spot, or the click area were clicked.
            if (debug.indexOf("press") === 0 && root.icons && root.icons.view) root.icons.view.pressed();
            if (debug.indexOf("click") === 0 && root.catcher && root.catcher.visible)
                root.tell("DesktopClick", []);
        }
    }

    // Never leave anything invisible: not when the helper is removed, not after a restart
    // of Plasma (it starts with everything fully visible, whatever was asked last).
    function letGo() {
        fader.stop();
        wish = ({});
        level = 1;
        apply();
    }
    Connections {
        target: Plasmoid
        function onDestroyedChanged(destroyed) { if (destroyed) root.letGo(); }
    }
    Component.onDestruction: letGo()
}
