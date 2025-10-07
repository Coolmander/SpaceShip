# SpaceShip Multiplayer Konsolen-Spiel

## Überblick
Dieses Projekt besteht aus einem WebSocket-Server (`space_server.py`) und einem webbasierten Client (`space_client.html`). Gemeinsam bilden sie ein kooperatives Multiplayer-Minispiel, bei dem mehrere Spieler*innen unterschiedliche Kontrollflächen bedienen, um Notfälle auf einem Raumschiff zu lösen.

Der Python-Server verteilt zufällig generierte Steuerelemente an die verbundenen Clients, startet Aufgaben und bewertet die Eingaben. Die HTML/JavaScript-Oberfläche stellt für jedes Endgerät eine individuelle Konsole dar.

## Voraussetzungen
- Python 3.9 oder neuer
- Abhängigkeiten:
  - `websockets` (per `pip install websockets`)
  - `tkinter` (bei vielen Python-Distributionen bereits enthalten)
- Ein moderner Browser auf den Endgeräten der Spieler*innen
- Alle Geräte müssen sich im selben Netzwerk befinden

## Installation
1. Repository klonen oder entpacken.
2. Abhängigkeiten installieren:
   ```bash
   pip install websockets
   ```

## Server starten
1. Stelle sicher, dass sich alle Dateien im selben Verzeichnis befinden.
2. Starte den Server auf dem Host-Rechner (z. B. Laptop/PC, der im selben Netz wie die mobilen Geräte ist):
   ```bash
   python space_server.py
   ```
3. Es öffnet sich eine Desktop-GUI, die den aktuellen Spielstatus, verbundene Geräte sowie die IP-Adresse des Servers anzeigt.
4. Über die Buttons in der GUI kann das Spiel gestartet oder gestoppt werden.

## Client verbinden
1. Öffne die Datei `space_client.html` auf dem Endgerät der Spieler*innen in einem Browser. (Lokales Öffnen genügt; ein Webserver ist nicht erforderlich.)
2. Gib im Startbildschirm die IP-Adresse ein, die in der Server-GUI angezeigt wird. Der Port ist fest auf `8765` gesetzt.
3. Nach erfolgreicher Verbindung blendet der Client den Steuerungsbereich ein. Jede Session erhält eigene Steuerelemente mit unterschiedlichen Farben, Formen und Interaktionen.

## Spielablauf
- Der Server wählt zufällig Aufgaben aus, die gelöst werden müssen (z. B. "Schilde verstärken").
- Im Client erscheint das aktuelle Problem sowie die Anweisung, welche Kontrolle (z. B. roter Slider auf Position 2) betätigt werden soll.
- Wenn die richtige Kontrolle in den vorgegebenen Zustand versetzt wird, vergibt der Server Punkte und generiert eine neue Aufgabe.
- Erfolgreiche Aktionen werden an alle verbundenen Clients gesendet; die Server-GUI zeigt den Punktestand und das aktive Problem.

## Hinweise zur Erweiterung
- `space_server.py` ist modular aufgebaut und kann erweitert werden (z. B. für persistente Highscores, zusätzliche Kontrolltypen oder komplexere Aufgabenlogik).
- `space_client.html` nutzt einfache DOM-Manipulation. Zusätzliche UI-Elemente oder Styling-Anpassungen können direkt in der Datei vorgenommen werden.
- Aktuell werden Kontrollen zufällig generiert. Für konsistentere Spielerlebnisse könnte man vordefinierte Sets erstellen.

## Troubleshooting
- **Keine Verbindung möglich:** Prüfe Firewall-Einstellungen und ob alle Geräte im selben Netzwerk sind.
- **Tkinter-Fehler:** Unter manchen Linux-Distributionen muss das Paket `python3-tk` nachinstalliert werden.
- **Browser blockiert WebSockets:** Verwende einen aktuellen Browser (Chrome, Firefox, Safari, Edge). Manche mobile Browser benötigen HTTPS für WebSockets; bei lokalen Netzen funktioniert HTTP jedoch in der Regel.

Viel Spaß bei der Weltraum-Mission! 🚀
