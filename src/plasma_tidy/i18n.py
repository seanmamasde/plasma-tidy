# SPDX-FileCopyrightText: 2026 Ivar
# SPDX-License-Identifier: GPL-3.0-or-later
"""Translations: the texts are English in the code; this holds the other languages."""

from PyQt6.QtCore import QLocale, QSettings

from .consts import APP

# Translations. The texts in the code are English; to add a language, add a table here
# and a line in LANGUAGES. A text missing from a table stays English.
TRANSLATIONS = {
    "nl": {
        "Keeps your KDE Plasma desktop, panel and system tray clean.":
            "Houdt je KDE Plasma-bureaublad, paneel en systeemvak opgeruimd.",
        # screen corners
        "None": "Geen",
        "Top left": "Linksboven",
        "Top right": "Rechtsboven",
        "Bottom left": "Linksonder",
        "Bottom right": "Rechtsonder",
        # system tray
        "Automatic": "Automatisch",
        "Only visible when relevant": "Alleen zichtbaar als het relevant is",
        "Show": "Tonen",
        "Always visible in the panel": "Altijd zichtbaar in de taakbalk",
        "Hide": "Verbergen",
        "Only reachable through the ^ arrow": "Alleen bereikbaar via het pijltje ^",
        "Off": "Uit",
        "Switched off completely": "Helemaal uitgeschakeld",
        "Battery": "Batterij",
        "Brightness": "Helderheid",
        "Camera indicator": "Camera-indicator",
        "Clipboard": "Klembord",
        "Devices (USB)": "Apparaten (usb)",
        "Caps Lock indicator": "Caps Lock-indicator",
        "Keyboard layout": "Toetsenbordindeling",
        "Input method": "Invoermethode",
        "Network (Wi-Fi)": "Netwerk (wifi)",
        "Notifications": "Meldingen",
        "Vaults": "Kluizen",
        "Weather": "Weer",
        "Displays": "Beeldschermen",
        "Media controls": "Mediabediening",
        "Xwayland screen sharing": "Xwayland-schermdelen",
        "Tidy (this program)": "Tidy (dit programma)",
        "No system tray found in the panel.": "Geen systeemvak gevonden in het paneel.",
        "Choose for each icon how it appears in the system tray.\n"
        "Automatic: only when relevant · Hide: under the ^ arrow":
            "Kies per pictogram hoe het rechts in de taakbalk staat.\n"
            "Automatisch: alleen als het relevant is · Verbergen: onder het pijltje ^",
        "System items": "Systeemonderdelen",
        "Applications": "Programma's",
        "Minimal": "Minimaal",
        "Show all": "Alles tonen",
        "Every icon always visible in the panel; what is switched off stays off.":
            "Elk pictogram altijd zichtbaar in de taakbalk; wat uit staat blijft uit.",
        "Hide all": "Alles verbergen",
        "Every icon under the ^ arrow; what is switched off stays off.":
            "Elk pictogram onder het pijltje ^; wat uit staat blijft uit.",
        "Only network, volume and battery visible; notifications and devices when relevant; "
        "the rest under ^.":
            "Alleen netwerk, volume en batterij in beeld; meldingen en "
            "apparaten als ze relevant zijn; de rest onder ^.",
        # panel drawers
        "Application launcher": "Startmenu",
        "Application menu": "Toepassingenmenu",
        "Application dashboard": "Toepassingendashboard",
        "Virtual desktops": "Virtuele bureaubladen",
        "Task manager (icons)": "Taakbeheer (pictogrammen)",
        "Task manager": "Taakbeheer",
        "Clock": "Klok",
        "Show desktop": "Bureaublad tonen",
        "Minimize all": "Alles minimaliseren",
        "Quick launch": "Snelstarter",
        "Program icon": "Programmapictogram",
        "Trash": "Prullenbak",
        "Global menu": "Globaal menu",
        "Top panel": "Paneel boven",
        "Bottom panel": "Paneel onder",
        "Left panel": "Paneel links",
        "Right panel": "Paneel rechts",
        "Panel": "Paneel",
        "A drawer is an arrow in the panel. It tucks the widgets you choose away and "
        "brings them back when you click or point at the arrow.":
            "Een la is een pijltje in het paneel. Die bergt de onderdelen op die je kiest "
            "en haalt ze terug als je op het pijltje klikt of het aanwijst.",
        "Drawer:": "La:",
        "Drawers": "Laden",
        "Settings of this folder: its icon, title, sorting and more":
            "Instellingen van deze map: pictogram, titel, sortering en meer",
        "Search the settings…": "Zoek in de instellingen…",
        "A panel that hides": "Een paneel dat zich verbergt",
        "Drawer {n}": "La {n}",
        "Name:": "Naam:",
        "A name of your own for this drawer. Without one it is called after what is in it.":
            "Een eigen naam voor deze la. Zonder naam heet hij naar wat erin zit.",
        "Add a drawer": "La toevoegen",
        "Add a folder…": "Map toevoegen…",
        "Puts a folder in the panel, in this drawer: a click on it shows what is in the "
        "folder. It is Plasma's own Folder View widget.":
            "Zet een map in het paneel, in deze la: een klik erop laat zien wat er in de map "
            "zit. Het is Plasma's eigen widget Mapweergave.",
        "Take this folder out of the panel": "Deze map uit het paneel halen",
        "Choose a folder for the drawer": "Kies een map voor de la",
        "The folder could not be added to the panel.":
            "De map kon niet aan het paneel worden toegevoegd.",
        "Folder: {name}": "Map: {name}",
        "Folder": "Map",
        "Remove": "Verwijderen",
        "No drawer yet. Add one to hide panel icons behind an arrow.":
            "Nog geen la. Voeg er een toe om paneelpictogrammen achter een pijltje te verbergen.",
        "The drawer could not be added to the panel.":
            "De la kon niet aan het paneel worden toegevoegd.",
        "No panel found.": "Geen paneel gevonden.",
        "In this drawer": "In deze la",
        "Hide all programs, open ones too": "Alle programma's verbergen, ook geopende",
        "Hide only pinned programs that are not open":
            "Alleen vastgemaakte programma's verbergen die niet open zijn",
        "Open programs are windows: with the second choice they stay in the panel and only "
        "the pinned icons of programs that are not running disappear.":
            "Geopende programma's zijn vensters: bij de tweede keuze blijven ze in het paneel "
            "staan en verdwijnen alleen de vastgemaakte pictogrammen van programma's die niet "
            "draaien.",
        "Task manager:": "Taakbeheer:",
        "A click on the arrow": "Een klik op het pijltje",
        "Pointing at the arrow (a click works too)":
            "Het pijltje aanwijzen (klikken werkt ook)",
        "Open with:": "Openen met:",
        "Pointing opens after:": "Aanwijzen opent na:",
        "Close by itself:": "Vanzelf sluiten:",
        "Never": "Nooit",
        "When the pointer leaves the drawer": "Als de muis de la verlaat",
        "When the pointer leaves the panel": "Als de muis het paneel verlaat",
        "The drawer is the arrow and the items it shows; empty panel space next to them "
        "is outside it.":
            "De la is het pijltje met de onderdelen die het toont; lege ruimte in het "
            "paneel ernaast valt erbuiten.",
        "Closes after:": "Sluit na:",
        "Close with a click on an empty spot in the panel":
            "Sluiten met een klik op een lege plek in het paneel",
        "Open when a program asks for attention": "Openen als een programma om aandacht vraagt",
        "Animation:": "Animatie:",
        "Slide": "Schuiven",
        "One by one": "Eén voor één",
        "Fade": "Vervagen",
        "Slide: the icons slide out from under the arrow at their normal size, like a drawer. "
        "Grow: they grow from small to their normal size. One by one: they come and go one "
        "after the other. Fade: they fade together and the rest closes up.":
            "Schuiven: de pictogrammen schuiven op normale grootte onder het pijltje vandaan, "
            "als een la. Groeien: ze groeien van klein naar hun normale grootte. Eén voor één: "
            "ze komen en gaan na elkaar. Vervagen: ze vervagen tegelijk en de rest sluit aan.",
        "Grow": "Groeien",
        "Speed:": "Snelheid:",
        "How long the movement takes; one by one, how long each icon takes.":
            "Hoe lang de beweging duurt; bij één voor één, hoe lang elk pictogram erover doet.",
        "Appearance": "Uiterlijk",
        "Open programs:": "Open programma's:",
        "On their pinned spot": "Op hun vaste plek",
        "All in front": "Allemaal vooraan",
        "All at the back": "Allemaal achteraan",
        "It goes there:": "Het gaat daarheen:",
        "Gliding": "Glijdend",
        "Fading over": "Overvloeiend",
        "How a program that opens goes to the open programs, and back when it closes. Gliding: it slides there on top of the icons it passes. Fading over: it fades out on its old spot and comes up on the new one. The icons it passes glide a place over either way.":
            "Hoe een programma dat opent naar de open programma's gaat, en terug als het sluit. Glijdend: het schuift erheen, over de pictogrammen waar het langs komt. Overvloeiend: het vervaagt op de oude plek en komt op de nieuwe tevoorschijn. De pictogrammen waar het langs komt schuiven in beide gevallen een plek op.",
        "A pinned program that is open normally stays on its pinned spot, between the others. "
        "In front or at the back, the open programs stand together and the pinned ones slide "
        "out next to them.":
            "Een vastgemaakt programma dat open is, blijft normaal op zijn vaste plek staan, "
            "tussen de andere. Vooraan of achteraan staan de open programma's bij elkaar en "
            "schuiven de vastgemaakte ernaast uit.",
        "Arrow points the other way": "Pijltje wijst de andere kant op",
        "Contents": "Inhoud",
        "Opening and closing": "Openen en sluiten",
        "Arrow": "Pijltje",
        "Opening": "Openen",
        "Closing": "Sluiten",
        "Shortcut:": "Sneltoets:",
        "A shortcut for this drawer alone. The shortcut for all drawers at once is set in "
        "System Settings.":
            "Een sneltoets voor alleen deze la. De sneltoets voor alle laden tegelijk stel je "
            "in bij Systeeminstellingen.",
        "Open when the desktop is shown": "Openen als het bureaublad wordt getoond",
        "Works while Tidy is running.": "Werkt zolang Tidy draait.",
        "Close after a click on something in the drawer": "Sluiten na een klik op iets in de la",
        "Panel stays after starting a program:": "Paneel blijft na het starten van een programma:",
        "Stays open after that click:": "Blijft open na die klik:",
        "After a click on a program in the drawer the drawer stays this long before it closes, so you see where the program went. With the programs in the middle of the panel a longer time is calmer. It never closes under the pointer: it waits until the pointer has left the drawer.":
            "Na een klik op een programma in de la blijft de la zo lang staan voordat hij sluit, zodat je ziet waar het programma heen ging. Met de programma's in het midden van het paneel is een langere tijd rustiger. Hij sluit nooit onder de aanwijzer: hij wacht tot de aanwijzer de la heeft verlaten.",
        "A panel that hides itself or dodges windows goes the moment the window of a program "
        "you start from the drawer opens. With a time here it stays that long, so you can go "
        "on in the panel. 0: it goes at once.":
            "Een paneel dat zichzelf verbergt of vensters ontwijkt, verdwijnt zodra het venster "
            "opent van een programma dat je vanuit de la start. Met een tijd hier blijft het zo "
            "lang staan, zodat je verder kunt in het paneel. 0: het verdwijnt meteen.",
        "Close when a window that fills the screen comes to the front":
            "Sluiten als een schermvullend venster naar voren komt",
        "Icon:": "Pictogram:",
        "Double arrow": "Dubbel pijltje",
        "Triangle": "Driehoekje",
        "Dots": "Puntjes",
        "Menu lines": "Menustreepjes",
        "Grip": "Greep",
        "My own icon": "Eigen pictogram",
        "No icon": "Geen pictogram",
        "Without an icon the spot stays clickable and lights up under the pointer.":
            "Zonder pictogram blijft de plek aanklikbaar en licht hij op onder de muis.",
        "Icon name or image file": "Pictogramnaam of afbeeldingsbestand",
        "Close when the panel slides out of view": "Sluiten als het paneel uit beeld schuift",
        "When the panel hides (auto-hide, dodging a window, or hidden together with the "
        "desktop icons) the drawer closes, so the panel comes back tidy. It does not open "
        "again by itself.":
            "Als het paneel verdwijnt (automatisch verbergen, een venster ontwijken, of samen "
            "met de bureaubladpictogrammen verborgen) sluit de la, zodat het paneel opgeruimd "
            "terugkomt. Hij gaat niet vanzelf weer open.",
        "Without an icon the arrow takes no room in the panel":
            "Zonder pictogram neemt het pijltje geen ruimte in het paneel",
        "The empty spot goes, and with it pointing at it and clicking it. Only while the "
        "drawer can be opened another way: a click on an empty spot of the panel, a shortcut, "
        "or when the desktop is shown. The room is back while you edit the panel and while "
        "the drawer is paused.":
            "De lege plek verdwijnt, en daarmee ook het aanwijzen en aanklikken ervan. Alleen "
            "zolang de la op een andere manier open kan: een klik op een lege plek van het "
            "paneel, een sneltoets, of wanneer het bureaublad wordt getoond. De ruimte is "
            "terug terwijl je het paneel bewerkt en terwijl de la gepauzeerd is.",
        "Its room comes back while the mark has something to tell":
            "De ruimte komt terug zolang de stip iets te melden heeft",
        "On: the spot returns to show the mark, so the panel shifts a little at that moment. "
        "Off: the mark is not shown.":
            "Aan: de plek komt terug om de stip te tonen, dus het paneel verschuift dan even "
            "een stukje. Uit: de stip wordt niet getoond.",
        "Choose…": "Kiezen…",
        "Choose an image": "Kies een afbeelding",
        "The place of the arrow is set in Tidy.": "De plaats van het pijltje stel je in Tidy in.",
        "Mark on the closed drawer:": "Teken op een gesloten la:",
        "A dot when programs are open": "Een stip als er programma's open zijn",
        "The number of open programs": "Het aantal open programma's",
        "A dot only when a program asks for attention":
            "Alleen een stip als een programma om aandacht vraagt",
        "Shown on the arrow while the drawer is closed and hides a task manager with all its "
        "programs. The dot changes colour when a program asks for attention.":
            "Staat op het pijltje zolang de la dicht is en een taakbeheer met al zijn "
            "programma's verbergt. De stip verandert van kleur als een programma om aandacht "
            "vraagt.",
        "Place of the arrow:": "Plaats van het pijltje:",
        "Just before the items it hides": "Direct vóór de onderdelen die het verbergt",
        "Just after the items it hides": "Direct na de onderdelen die het verbergt",
        "Where I put it myself": "Waar ik het zelf neerzet",
        "After a task manager the arrow sits right behind the last program. The task manager "
        "then no longer fills the panel; the drawer does that instead.":
            "Na een taakbeheer staat het pijltje direct achter het laatste programma. "
            "Taakbeheer vult het paneel dan niet meer op; dat doet de la.",
        "All drawers": "Alle laden",
        "Close and open together with the desktop icons":
            "Sluiten en openen samen met de bureaubladpictogrammen",
        "The arrow sits next to the items it hides. To place it yourself, choose \"Where I "
        "put it myself\", right-click the panel, choose Enter Edit Mode and drag it.":
            "Het pijltje staat naast de onderdelen die het verbergt. Zelf plaatsen: kies "
            "\"Waar ik het zelf neerzet\", klik met rechts op het paneel, kies Bewerkmodus "
            "en sleep het.",
        "Show the hidden items": "Verborgen onderdelen tonen",
        "Hide the items": "Onderdelen verbergen",
        "{app} settings…": "{app}-instellingen…",
        "Paused. Click to resume": "Gepauzeerd. Klik om te hervatten",
        # focus mode
        "Focus mode": "Focusmodus",
        "Focus mode tucks everything away at once and keeps it away: nothing comes back on "
        "mouse movement or a click on the desktop. Switching it off puts everything back as "
        "it was.":
            "De focusmodus bergt alles in één keer op en houdt het weg: er komt niets terug "
            "bij een muisbeweging of een klik op het bureaublad. Zet je hem uit, dan staat "
            "alles weer zoals het was.",
        "In focus mode": "In de focusmodus",
        "Hide the desktop icons": "Bureaubladpictogrammen verbergen",
        "Close the panel drawers": "Paneelladen sluiten",
        "Set the system tray to Minimal": "Systeemvak op Minimaal zetten",
        "Auto-hide the panel": "Paneel automatisch verbergen",
        "Switch focus mode off": "Focusmodus uitzetten",
        "Save and switch focus mode on": "Opslaan en focusmodus aanzetten",
        "Focus mode is also in the tray menu, and you can give it a shortcut (see the General "
        "tab). A closed drawer still opens when you click or point at its arrow.":
            "De focusmodus staat ook in het systeemvakmenu, en je kunt er een sneltoets aan "
            "geven (zie het tabblad Algemeen). Een gesloten la gaat nog steeds open als je op "
            "het pijltje klikt of het aanwijst.",
        "Focus mode — everything stays away until you switch it off":
            "Focusmodus — alles blijft weg tot je hem uitzet",
        "{app} — focus mode": "{app} — focusmodus",
        # restore everything
        "Restore everything…": "Alles terugzetten…",
        "Restore everything?": "Alles terugzetten?",
        "This shows your desktop icons, your panel and everything in the drawers again, and "
        "puts back the Plasma settings that {app} changed. {app} is switched off and the "
        "drawers are paused until you switch {app} on again.":
            "Dit toont je bureaubladpictogrammen, je paneel en alles in de laden weer, en zet "
            "de Plasma-instellingen terug die {app} heeft aangepast. {app} wordt uitgeschakeld "
            "en de laden pauzeren tot je {app} weer inschakelt.",
        "Also put the system tray back as it was before {app} changed it":
            "Ook het systeemvak terugzetten zoals het was voordat {app} het aanpaste",
        "Restore": "Terugzetten",
        # about
        "Version {version}": "Versie {version}",
        "Hides your desktop icons when you don't need them, tucks the programs and icons "
        "in your panel away behind an arrow, and lets you choose per icon what shows in the "
        "system tray.":
            "Verbergt je bureaubladpictogrammen als je ze niet nodig hebt, bergt de "
            "programma's en pictogrammen in je paneel op achter een pijltje, en laat je per "
            "pictogram kiezen wat er in het systeemvak staat.",
        "coming with the first release": "volgt bij de eerste release",
        "Made by {author}": "Gemaakt door {author}",
        "License: {license}": "Licentie: {license}",
        "Website and source code": "Website en broncode",
        "Report a problem or share an idea": "Probleem melden of idee delen",
        "Support {app}": "Steun {app}",
        "{app} is free and open source. Find it useful? "
        "A small donation helps further development.":
            "{app} is gratis en open source. Vind je het handig? "
            "Met een kleine donatie help je de verdere ontwikkeling.",
        "♥  Donate": "♥  Doneren",
        "The donation page is coming with the first release.":
            "De doneerpagina volgt bij de eerste release.",
        # settings
        "{app} — settings": "{app} — instellingen",
        "Desktop": "Bureaublad",
        "System tray": "Systeemvak",
        "About {app}": "Over {app}",
        "Hide now": "Nu verbergen",
        "Hide after:": "Verbergen na:",
        "On any mouse movement or key press": "Bij elke muisbeweging of toets",
        "The icons come back:": "De pictogrammen komen terug:",
        "On a click on the desktop": "Bij een klik op het bureaublad",
        "On a double-click on the desktop": "Bij een dubbelklik op het bureaublad",
        "When the icons hide": "Wanneer de pictogrammen verdwijnen",
        "How they come back": "Hoe ze terugkomen",
        "What hides along": "Wat mee verdwijnt",
        "How it is done": "Hoe het gebeurt",
        "Left": "Links",
        "Middle": "Midden",
        "Right": "Rechts",
        "With mouse button:": "Met muisknop:",
        "After that time without movement (moving postpones)":
            "Na die tijd stilstand (bewegen stelt uit)",
        "After that time, even while you move": "Na die tijd, ook als je beweegt",
        "With a fixed time the icons can disappear just as you are about to click "
        "something; 10 s or more works well.":
            "Bij een vaste tijd kunnen de pictogrammen verdwijnen terwijl je "
            "net iets wilt aanklikken; 10 s of meer is prettig.",
        "After that they hide:": "Daarna verdwijnen ze:",
        "Moving the mouse into this screen corner brings the icons back.\n"
        "Note: KDE may already have an action on that corner "
        "(System Settings → Screen Edges).":
            "Muis in deze schermhoek haalt de pictogrammen terug.\n"
            "Let op: KDE kan zelf al een actie op die hoek hebben "
            "(Systeeminstellingen → Schermranden).",
        "Screen corner shows:": "Schermhoek toont:",
        "Activity in other windows doesn't count": "Activiteit in andere vensters telt niet mee",
        "On: while you work in another window the timer keeps running "
        "and the icons disappear behind your window. Moving the mouse over "
        "the desktop itself always counts.\n"
        "Off: every mouse movement or key press, anywhere, counts.":
            "Aan: werk je in een ander venster, dan loopt de teller door "
            "en verdwijnen de pictogrammen achter je venster. De muis bewegen "
            "boven het bureaublad zelf telt altijd mee.\n"
            "Uit: elke muisbeweging of toets, waar dan ook, telt.",
        "Moving over the panel does count": "Bewegen boven het paneel telt wel mee",
        "On: moving the mouse over the panel (taskbar) keeps the icons, "
        "like moving over the desktop.\n"
        "Off: only the desktop itself counts.":
            "Aan: de muis bewegen boven het paneel (de taakbalk) houdt de pictogrammen "
            "in beeld, net als bewegen boven het bureaublad.\n"
            "Uit: alleen het bureaublad zelf telt.",
        "Also hide the panel (taskbar)": "Paneel (taakbalk) ook verbergen",
        "Show the panel:": "Paneel tonen:",
        "After minimising a window": "Na het minimaliseren van een venster",
        "After minimising or closing a window": "Na het minimaliseren of sluiten van een venster",
        "A panel that is hidden, by Tidy or by itself, comes into view when you put a window "
        "away, so you can go straight to the next program. It goes again after the time on the Desktop tab, "
        "and stays while the pointer is on it.":
            "Een paneel dat verborgen is, door Tidy of uit zichzelf, komt in beeld als je een "
            "venster wegzet, zodat je meteen door kunt naar het volgende programma. Het "
            "verdwijnt weer na de tijd op het tabblad Bureaublad, en blijft zolang de muis erop staat.",
        "Start at login": "Starten bij inloggen",
        "Language:": "Taal:",
        "System language": "Systeemtaal",
        "General": "Algemeen",
        "Hide the icons on:": "Pictogrammen verbergen op:",
        "Fade the icons in and out": "Pictogrammen laten vervagen bij verbergen en tonen",
        "Needs the helper widget on the desktop.":
            "Heeft de hulpwidget op het bureaublad nodig.",
        "Hide with a helper widget on the desktop (lighter)":
            "Verbergen met een hulpwidget op het bureaublad (lichter)",
        "On: an invisible widget on the desktop makes the icons go and come. That is at once, "
        "costs no memory and writes nothing to disk; fading, hiding widgets and the "
        "double-click need it.\n"
        "Off: Tidy swaps the desktop's folder for an empty one and lays an invisible window "
        "over the desktop for your click. That needs nothing inside Plasma.\n"
        "Tidy also falls back on the second way by itself when the helper does not work.":
            "Aan: een onzichtbare widget op het bureaublad laat de pictogrammen verdwijnen en "
            "verschijnen. Dat gaat direct, kost geen geheugen en schrijft niets naar schijf; "
            "vervagen, widgets verbergen en de dubbelklik hebben hem nodig.\n"
            "Uit: Tidy wisselt de map van het bureaublad voor een lege en legt een onzichtbaar "
            "venster over het bureaublad voor je klik. Daar is niets binnen Plasma voor nodig.\n"
            "Tidy valt ook vanzelf terug op de tweede manier als de hulpwidget niet werkt.",
        "New icons go under the ^ arrow by themselves":
            "Nieuwe pictogrammen gaan vanzelf onder het pijltje ^",
        "An application that shows a tray icon for the first time gets it hidden. Works while "
        "Tidy is running.":
            "Een programma dat voor het eerst een pictogram in het systeemvak zet, krijgt het "
            "verborgen. Werkt zolang Tidy draait.",
        "Profiles": "Profielen",
        "A profile keeps all settings together: desktop, drawers, system tray and focus mode. "
        "Switch between them here or in the tray menu.":
            "Een profiel houdt alle instellingen bij elkaar: bureaublad, laden, systeemvak en "
            "focusmodus. Wissel hier of in het systeemvakmenu.",
        "Apply": "Toepassen",
        "Cancel": "Annuleren",
        "Save current as…": "Huidige bewaren als…",
        "Delete": "Verwijderen",
        "Name of the profile:": "Naam van het profiel:",
        "None yet: save one in the settings": "Nog geen: bewaar er een in de instellingen",
        "All settings": "Alle instellingen",
        "Export…": "Exporteren…",
        "Saves all settings and profiles in a file.":
            "Bewaart alle instellingen en profielen in een bestand.",
        "Import…": "Importeren…",
        "Reads settings and profiles from a file and applies them.":
            "Leest instellingen en profielen uit een bestand en past ze toe.",
        "Defaults…": "Standaardwaarden…",
        "Puts every setting back to how Tidy comes. Your drawers stay, with what is in them; "
        "the system tray is left alone.":
            "Zet elke instelling terug naar hoe Tidy geleverd wordt. Je laden blijven, met wat "
            "erin zit; het systeemvak blijft ongemoeid.",
        "Export settings": "Instellingen exporteren",
        "Import settings": "Instellingen importeren",
        "This is not a file with Tidy settings.": "Dit is geen bestand met Tidy-instellingen.",
        "Put every setting back to how Tidy comes?":
            "Elke instelling terugzetten naar hoe Tidy geleverd wordt?",
        "Shortcuts: System Settings → Keyboard → Shortcuts → Add New → Application… → Tidy. "
        "There you can give a key to showing and hiding the icons, switching Tidy on or off, "
        "focus mode, opening or closing the drawers, and restoring everything.":
            "Sneltoetsen: Systeeminstellingen → Toetsenbord → Sneltoetsen → Nieuwe toevoegen → "
            "Toepassing… → Tidy. Daar geef je een toets aan het tonen en verbergen van de "
            "pictogrammen, Tidy in- of uitschakelen, de focusmodus, de laden openen of sluiten, "
            "en alles terugzetten.",
        "Shows everything again, puts back the Plasma settings that Tidy changed, and switches "
        "Tidy off.":
            "Toont alles weer, zet de Plasma-instellingen terug die Tidy heeft aangepast, en "
            "schakelt Tidy uit.",
        "Search…": "Zoeken…",
        "All automatic": "Alles automatisch",
        "Plasma decides for every icon; what is switched off stays off.":
            "Plasma bepaalt het per pictogram; wat uit staat blijft uit.",
        "Plasma default": "Plasma-standaard",
        "Everything switched on and automatic, as a fresh Plasma has it.":
            "Alles ingeschakeld en automatisch, zoals een verse Plasma het heeft.",
        "My preset": "Mijn voorkeur",
        "Apply the arrangement you saved.": "Past de indeling toe die je hebt bewaard.",
        "Save as my preset": "Bewaren als mijn voorkeur",
        "Remember the choices as they are now.": "Onthoudt de keuzes zoals ze nu staan.",
        "Undo": "Ongedaan maken",
        "Back to how the list was when this window opened.":
            "Terug naar hoe de lijst stond toen dit venster openging.",
        "♥ Support {app}": "♥ Steun {app}",
        "Donate or more information": "Doneren of meer informatie",
        "Disabled": "Uitgeschakeld",
        "Hidden — waiting for a click on the desktop":
            "Verborgen — wacht op een klik op het bureaublad",
        "Hidden — waiting for mouse movement or a key press":
            "Verborgen — wacht op een muisbeweging of toets",
        "Paused — menu open or Plasma in edit mode":
            "Gepauzeerd — menu open of Plasma in bewerkingsmodus",
        "paused": "pauze",
        "Visible — hiding in:": "Zichtbaar — verbergen over:",
        # tray menu
        "Enabled": "Ingeschakeld",
        "Settings…": "Instellingen…",
        "♥ Donate…": "♥ Doneren…",
        "Quit": "Afsluiten",
        "{app} — disabled": "{app} — uitgeschakeld",
        "{app} — icons hidden": "{app} — pictogrammen verborgen",
        "{app} — icons visible": "{app} — pictogrammen zichtbaar",
        # command line
        "Usage: plasma-tidy [--show | --hide | --toggle | --settings | --welcome | --focus | "
        "--peek | --drawer-open | --drawer-close | --drawer-toggle | --restore | --check | "
        "--report | --version]":
            "Gebruik: plasma-tidy [--show | --hide | --toggle | --settings | --welcome | "
            "--focus | --peek | --drawer-open | --drawer-close | --drawer-toggle | --restore | "
            "--check | --report | --version]",
        "the drawers": "de laden",
        "hiding programs in a drawer": "programma's in een la verbergen",
        "the system tray in a drawer": "het systeemvak in een la",
        "only the preview in a program's pop-up": "alleen het voorbeeld in de pop-up van een programma",
        "pop-ups and balloons floating above the panel": "pop-ups en ballonnen die boven het paneel zweven",
        "knowing where another program (Modish) has moved a widget":
            "weten waarheen een ander programma (Modish) een widget heeft verschoven",
        "the desktop helper": "de bureaubladhelper",
        "hiding the widgets on the desktop": "de widgets op het bureaublad verbergen",
        "the double-click on the desktop": "de dubbelklik op het bureaublad",
        "knowing which window is in front": "weten welk venster vooraan staat",
        "the pointer over the desktop counting": "de muis boven het bureaublad laten meetellen",
        "drawers staying open under a menu": "laden die open blijven onder een menu",
        "drawers closing when the panel hides": "laden die sluiten als het paneel verdwijnt",
        "works": "werkt",
        "does not work in this version": "werkt niet in deze versie",
        "not in use": "niet in gebruik",
        "not seen yet": "nog niet gezien",
        "Plasma {version} is new to Tidy in some places. These parts are switched off: {parts}. "
        "Everything else works as before. In a terminal, plasma-tidy --check tells more.":
            "Plasma {version} is op een paar plekken nieuw voor Tidy. Deze onderdelen staan "
            "uit: {parts}. Al het andere werkt zoals altijd. In een terminal vertelt "
            "plasma-tidy --check meer.",
        "Tidy {version} on Plasma {plasma}": "Tidy {version} op Plasma {plasma}",
        "has not reported (yet)": "heeft (nog) niets gemeld",
        "KWin script": "KWin-script",
        "Desktop helper on desktop {id}": "Bureaubladhelper op bureaublad {id}",
        "Desktop helper": "Bureaubladhelper",
        "Drawer: {name}": "La: {name}",
        "Tidy is not running. Start it, wait a few seconds, and try again.":
            "Tidy draait niet. Start het, wacht een paar seconden en probeer het opnieuw.",
        "Tidy did not answer.": "Tidy gaf geen antwoord.",
        "for example: discord":
            "bijvoorbeeld: discord",
        "Remove this rule":
            "Deze regel verwijderen",
        "Add a rule for a name":
            "Regel voor een naam toevoegen",
        "A rule decides by name how an application's icon appears: when the rule is made, and every time such an icon shows up for the first time. A rule goes before the choice on the left.":
            "Een regel bepaalt op naam hoe het pictogram van een programma verschijnt: op het moment dat je de regel maakt, en elke keer dat zo'n pictogram voor het eerst opduikt. Een regel gaat voor op de keuze links.",
        "Name contains:":
            "Naam bevat:",
        "Programs that go in the drawer":
            "Programma's die in de la gaan",
        "A program without a tick stays in the panel, also while the drawer is closed.":
            "Een programma zonder vinkje blijft in het paneel staan, ook als de la dicht is.",
        "The programs of the task manager appear here a moment after the drawer has one in it. Open this window again to see them.":
            "De programma's van het takenbeheer verschijnen hier kort nadat er een in de la zit. Open dit venster opnieuw om ze te zien.",
        "Program name":
            "Naam van het programma",
        "The list holds the programs that are open now. You can also type the name.":
            "In de lijst staan de programma's die nu open zijn. Je kunt de naam ook typen.",
        "A rule uses one of your profiles, switches focus mode on, or keeps the night light off, for as long as something is the case. For the profile the highest rule that applies decides. You make profiles on the General tab.":
            "Een regel gebruikt een van je profielen, zet de focusmodus aan, of houdt het nachtlicht uit, zolang iets het geval is. Voor het profiel beslist de bovenste regel die geldt. Profielen maak je op het tabblad Algemeen.",
        "Night light off":
            "Nachtlicht uit",
        "Any program":
            "Elk programma",
        "No rules yet.":
            "Nog geen regels.",
        "Add a rule":
            "Regel toevoegen",
        "The profile for when no rule with a profile applies.":
            "Het profiel voor als er geen regel met een profiel geldt.",
        "Otherwise:":
            "Anders:",
        "A ✓ marks the rules that apply right now. A profile is put to use at the moment the choice changes; what you change by hand afterwards stays until the next change, so save it in the profile to keep it. Rules work while Tidy is running and switched on.":
            "Een ✓ staat bij de regels die nu gelden. Een profiel wordt gebruikt op het moment dat de keuze verandert; wat je daarna met de hand wijzigt blijft tot de volgende wissel, dus sla het op in het profiel om het te houden. Regels werken zolang Tidy draait en aan staat.",
        "Leave everything as it is":
            "Alles laten zoals het is",
        "Hide the icons after:":
            "Pictogrammen verbergen na:",
        "Start":
            "Starten",
        "More settings…":
            "Meer instellingen…",
        "Rules":
            "Regels",
        "A double-click on an empty spot of the desktop hides the icons":
            "Dubbelklikken op een lege plek van het bureaublad verbergt de pictogrammen",
        "Also hide the widgets on the desktop":
            "Widgets op het bureaublad ook verbergen",
        "Without a tick this widget stays in view.":
            "Zonder vinkje blijft deze widget in beeld.",
        "Clocks, notes and other widgets on the desktop go and come with the icons. Needs the "
        "helper widget on the desktop.":
            "Klokken, notities en andere widgets op het bureaublad verdwijnen en verschijnen "
            "samen met de pictogrammen. Heeft de hulpwidget op het bureaublad nodig.",
        "While you hold this key, the desktop icons and everything in the drawers are shown; let go and they are away again. Works in focus mode too.":
            "Zolang je deze toets ingedrukt houdt, zijn de bureaubladpictogrammen en alles in de la's te zien; laat los en ze zijn weer weg. Werkt ook in de focusmodus.",
        "Hold to peek:":
            "Ingedrukt houden om te gluren:",
        "This key has no Ctrl, Alt or Meta with it. While Tidy runs it would no longer work in "
        "any program, not for typing or moving either. Better choose a combination, such as "
        "Meta+Z.":
            "Deze toets heeft geen Ctrl, Alt of Meta erbij. Zolang Tidy draait werkt hij dan in "
            "geen enkel programma meer, ook niet om te typen of te bewegen. Kies liever een "
            "combinatie, zoals Meta+Z.",
        "A peek also shows the panel, on top of your windows":
            "Gluren laat ook het paneel zien, boven je vensters",
        "A panel that hides by itself or sits behind a window comes into view while you hold "
        "the key. Your windows keep their size. A program in full screen stays on top of the "
        "panel.":
            "Een paneel dat zichzelf verbergt of achter een venster zit komt in beeld zolang je "
            "de toets vasthoudt. Je vensters houden hun grootte. Een programma op volledig "
            "scherm blijft boven het paneel.",
        "Open with a click on an empty spot in the panel":
            "Openen met een klik op een lege plek in het paneel",
        "A click where the panel is empty opens this drawer. As long as a drawer that opens "
        "with the same click is closed, the click only opens; it closes when all of them are open.":
            "Een klik waar het paneel leeg is opent deze la. Zolang er een la dicht is die met "
            "dezelfde klik opent, opent de klik alleen; sluiten gebeurt als ze allemaal open staan.",
        "That click is:": "Die klik is:",
        "Left click": "Linkerklik",
        "Middle click": "Middelklik",
        "Ctrl + click": "Ctrl + klik",
        "Shift + click": "Shift + klik",
        "Alt + click": "Alt + klik",
        "Which click on an empty spot of the panel opens this drawer, and closes it if that is ticked below. Give two drawers a different click and each opens on its own: the programs with a left click, say, and the system tray with the middle button. Drawers with the same click go together.":
            "Welke klik op een lege plek van het paneel deze la opent, en sluit als dat hieronder is aangevinkt. Geef twee laden een andere klik en elk opent apart: de programma's met een linkerklik bijvoorbeeld, en het systeemvak met de middelste knop. Laden met dezelfde klik gaan samen.",
        "and":
            "en",
        "Applies right now":
            "Geldt nu",
        "Welcome to {app}":
            "Welkom bij {app}",
        "{app} keeps your desktop clean. It hides the desktop icons when you don't need them "
        "and brings them back when you do. A few choices to start with; everything can be "
        "changed later.":
            "{app} houdt je bureaublad schoon. Het verbergt de bureaubladpictogrammen als je ze "
            "niet nodig hebt en haalt ze terug als je ze wel nodig hebt. Een paar keuzes om mee "
            "te beginnen; alles is later te wijzigen.",
        "{app} can also tidy your panel:": "{app} kan ook je paneel opruimen:",
        "Add a drawer for the programs in the panel":
            "Een la toevoegen voor de programma's in het paneel",
        "Puts an arrow next to the task manager. A click on it tucks the program icons away, "
        "and brings them back.":
            "Zet een pijltje naast het takenbeheer. Een klik erop stopt de programmapictogrammen "
            "weg, en haalt ze weer terug.",
        "There is one already, or the panel has no task manager.":
            "Er is er al een, of het paneel heeft geen takenbeheer.",
        "Tidy the system tray": "Het systeemvak opruimen",
        "Only network, volume and battery stay in view, and Tidy's own icon; the rest goes "
        "under the ^ arrow.":
            "Alleen netwerk, volume en batterij blijven in beeld, en Tidy's eigen pictogram; "
            "de rest gaat onder het pijltje ^.",
        "There is more in the settings: focus mode, rules, profiles and a key to peek. {app} "
        "lives in the system tray: click its icon to open the settings.":
            "In de instellingen zit meer: focusmodus, regels, profielen en een toets om te "
            "gluren. {app} staat in het systeemvak: klik op het pictogram om de "
            "instellingen te openen.",
        "Welcome window…": "Welkomstscherm…",
        "Balloons and previews": "Ballonnen en voorbeelden",
        "Plasma shows a balloon with text when you point at something":
            "Plasma toont een ballon met tekst als je iets aanwijst",
        "Plasma's own setting, for every balloon in the panel, the system tray and on the "
        "desktop. Off: none of them appear. The pop-up of a program in the panel is chosen "
        "below, and can stay.":
            "Plasma's eigen instelling, voor elke ballon in het paneel, het systeemvak en op "
            "het bureaublad. Uit: er verschijnt er geen enkele. De pop-up van een programma "
            "in het paneel kies je hieronder, en die kan blijven.",
        "Pop-up of a program in the panel:": "Pop-up van een programma in het paneel:",
        "With a preview of the window": "Met een voorbeeld van het venster",
        "Title and text only": "Alleen titel en tekst",
        "What comes up when you point at a program in the panel. With or without the preview "
        "is the task manager's own setting. Only the preview, none at all, and a pop-up while "
        "Plasma's balloons are off, are done by a drawer: they work for a task manager that is "
        "in a drawer. Only the preview leaves out the title and the text. A program that is "
        "not open shows its name, as long as Plasma's balloons are on.":
            "Wat er verschijnt als je een programma in het paneel aanwijst. Met of zonder "
            "voorbeeld is de eigen instelling van het takenbeheer. Alleen het voorbeeld, "
            "helemaal geen pop-up, en een pop-up terwijl Plasma's ballonnen uit staan, regelt "
            "een la: dat werkt voor een takenbeheer dat in een la zit. Alleen het voorbeeld "
            "laat de titel en de tekst weg. Een programma dat niet open is toont zijn naam, "
            "zolang Plasma's ballonnen aan staan.",
        "With only the preview: keep the close button, above it":
            "Bij alleen het voorbeeld: de sluitknop houden, erboven",
        "The pop-up's close button sits next to the title and the text. On: it stays where it "
        "is, above the preview. Off: it goes with them.":
            "De sluitknop van de pop-up staat naast de titel en de tekst. Aan: hij blijft "
            "waar hij staat, boven het voorbeeld. Uit: hij verdwijnt mee.",
        "This pop-up floats above the panel, like Plasma's own pop-ups":
            "Deze pop-up zweeft boven het paneel, net als Plasma's eigen pop-ups",
        "On: the same distance from the panel as the start menu and the system tray's own "
        "pop-up. Off: against the panel, as Plasma puts it. Only a floating panel shows the "
        "difference. Works in a panel that has a drawer.":
            "Aan: dezelfde afstand tot het paneel als het startmenu en de eigen pop-up van "
            "het systeemvak. Uit: tegen het paneel aan, zoals Plasma het doet. Alleen bij een "
            "zwevend paneel zie je verschil. Werkt in een paneel waar een la in zit.",
        "Balloons float above the panel, like Plasma's own pop-ups":
            "Ballonnen zweven boven het paneel, net als Plasma's eigen pop-ups",
        "Only the preview of the window": "Alleen het voorbeeld van het venster",
        "The arrow shows a balloon when you point at it":
            "Het pijltje toont een ballon als je het aanwijst",
        "Shows its contents:": "Toont zijn inhoud:",
        "In the panel": "In het paneel",
        "In a pop-up above the arrow": "In een pop-up boven het pijltje",
        "Pop-up:": "Pop-up:",
        "A row of icons": "Een rij pictogrammen",
        "A column of icons": "Een kolom pictogrammen",
        "Place of the pop-up:": "Plek van de pop-up:",
        "Above the arrow": "Boven de pijl",
        "At the start of the panel": "Aan het begin van het paneel",
        "In the middle of the panel": "In het midden van het paneel",
        "At the end of the panel": "Aan het eind van het paneel",
        "Above the arrow, or at a fixed spot of the panel, wherever the arrow is. The pop-up "
        "ends where the panel ends. Is that at the edge of the screen, then a pointer pushed "
        "against that edge is on the icons.":
            "Boven de pijl, of op een vaste plek van het paneel, waar de pijl ook staat. De "
            "pop-up eindigt waar het paneel eindigt. Is dat aan de schermrand, dan staat een "
            "muis die je tegen die rand duwt op de pictogrammen.",
        "Pop-up has a background, like the panel": "Pop-up heeft een achtergrond, zoals het paneel",
        "Pop-up floats above the panel, like Plasma's own pop-ups":
            "Pop-up zweeft boven het paneel, zoals Plasma's eigen pop-ups",
        "On: the pop-up keeps the same distance from the panel as the system tray's own pop-up "
        "and the start menu, so they all line up. Off: it stands on the panel's edge. Only a "
        "floating panel shows the difference.":
            "Aan: de pop-up houdt dezelfde afstand tot het paneel als de eigen pop-up van het "
            "systeemvak en het startmenu, zodat ze op één lijn staan. Uit: hij staat op de rand "
            "van het paneel. Alleen bij een zwevend paneel zie je het verschil.",
"The system tray's own arrow (^):": "Het eigen pijltje (^) van het systeemvak:",
        "In the panel while the pop-up is open": "In het paneel zolang de pop-up open is",
        "Always in the panel": "Altijd in het paneel",
        "With the system tray in a pop-up, only its icons go there. The tray's own arrow, for "
        "the icons it keeps hidden, can stay in the panel, show there only while the pop-up "
        "is open, or go altogether. Without it, the icons under it can only be reached by "
        "setting them to Show on the System tray tab.":
            "Met het systeemvak in een pop-up gaan alleen de pictogrammen daarheen. Het eigen "
            "pijltje van het systeemvak, voor de pictogrammen die het verborgen houdt, kan in "
            "het paneel blijven, daar alleen staan zolang de pop-up open is, of helemaal "
            "verdwijnen. Zonder pijltje zijn de pictogrammen eronder alleen nog te bereiken "
            "door ze op het tabblad Systeemvak op Tonen te zetten.",
        "On: the pop-up looks like a piece of your panel. Off: only the icons, on whatever is "
        "behind them.":
            "Aan: de pop-up ziet eruit als een stukje van je paneel. Uit: alleen de pictogrammen, "
            "op wat er ook achter staat.",
        "A grid with names": "Een raster met namen",
        "A list with names": "Een lijst met namen",
        "In the panel: what is in the drawer slides out next to the arrow. In a pop-up: it "
        "stays out of the panel and comes up in a small window above the arrow, so the panel "
        "never changes size; made for a panel that is as long as its contents. Programs are "
        "shown as icons you can click; any other widget, such as the system tray, is moved "
        "into the pop-up as it is and keeps its own shape.":
            "In het paneel: wat in de la zit schuift naast het pijltje uit. In een pop-up: het "
            "blijft buiten het paneel en komt omhoog in een klein venster boven het pijltje, "
            "zodat het paneel nooit van grootte verandert; gemaakt voor een paneel dat zo lang "
            "is als zijn inhoud. Programma's worden getoond als pictogrammen waarop je kunt "
            "klikken; elke andere widget, zoals het systeemvak, wordt zoals hij is naar de "
            "pop-up verplaatst en houdt zijn eigen vorm.",
        "This panel is as long as its contents, so it jumps to its new size when the drawer "
        "opens. Sliding inside it adds nothing then: the icons fade, whatever is chosen here.":
            "Dit paneel is zo lang als zijn inhoud en springt dus naar zijn nieuwe grootte als "
            "de la opengaat. Schuiven erbinnen voegt dan niets toe: de pictogrammen vervagen, "
            "wat hier ook gekozen is.",
        "This panel is as long as its contents: it has no empty spot to click on.":
            "Dit paneel is zo lang als zijn inhoud: er is geen lege plek om op te klikken.",
        "This panel is as long as its contents: it changes size when a drawer opens. Showing "
        "the contents in a pop-up (Appearance) keeps the panel still.":
            "Dit paneel is zo lang als zijn inhoud: het verandert van grootte als een la "
            "opengaat. Met de inhoud in een pop-up (Uiterlijk) blijft het paneel stilstaan.",
        "Shows the window from the first start again, with the choices to begin with.":
            "Toont het venster van de eerste start opnieuw, met de keuzes om mee te beginnen.",
        "Profile: {name}":
            "Profiel: {name}",
        "Desktop {n}":
            "Bureaublad {n}",
        "Higher: goes before the rules below it":
            "Hoger: gaat voor op de regels eronder",
        "Lower":
            "Lager",
        "On battery":
            "Op de accu",
        "On mains power":
            "Op netstroom",
        "An external screen is connected":
            "Er is een extern scherm aangesloten",
        "Between these times":
            "Tussen deze tijden",
        "This program is in front":
            "Dit programma staat vooraan",
        "A program fills the whole screen":
            "Een programma vult het hele scherm",
        "On this virtual desktop":
            "Op dit virtuele bureaublad",
        "In this activity":
            "In deze activiteit",
        "swayidle is missing.\n\nInstall it with:\nsudo dnf install swayidle":
            "swayidle ontbreekt.\n\nInstalleer het met:\nsudo dnf install swayidle",
    },
}
# Choices for the language setting. Languages go by their own name; "auto" follows the system.
LANGUAGES = [("auto", "System language"), ("en", "English"), ("nl", "Nederlands")]


def pick_catalog(choice):
    """Table for the chosen language; with "auto", for the first system language we know.
    English needs no table."""
    if choice in TRANSLATIONS:
        return TRANSLATIONS[choice]
    if choice == "en":
        return {}
    for language in QLocale.system().uiLanguages():
        code = language.replace("_", "-").split("-")[0].lower()
        if code == "en":
            break
        if code in TRANSLATIONS:
            return TRANSLATIONS[code]
    return {}


CATALOG = pick_catalog(QSettings(APP, APP).value("language", "auto"))


def set_language(choice):
    global CATALOG
    CATALOG = pick_catalog(choice)


def tr(text):
    return CATALOG.get(text, text)


def speaks_dutch():
    return CATALOG is TRANSLATIONS.get("nl")
