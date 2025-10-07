import asyncio
import websockets
import json
import random
import tkinter as tk
from threading import Thread

class SpaceGameServer:
    CONTROL_LIBRARY = [
        {"name": "Antrieb", "type": "schalter", "color": "rot", "min_value": 0, "max_value": 3},
        {"name": "Schilde", "type": "slider", "color": "blau", "min_value": 0, "max_value": 3},
        {"name": "Navigation", "type": "knopf", "color": "grün", "min_value": 0, "max_value": 3},
        {"name": "Kommunikation", "type": "schalter", "color": "gelb", "min_value": 0, "max_value": 2},
        {"name": "Triebwerk", "type": "slider", "color": "rot", "min_value": 0, "max_value": 4},
        {"name": "Scanner", "type": "knopf", "color": "blau", "min_value": 0, "max_value": 4},
        {"name": "Laser", "type": "knopf", "color": "rot", "min_value": 0, "max_value": 3},
        {"name": "Fracht", "type": "slider", "color": "grün", "min_value": 0, "max_value": 5},
        {"name": "Sauerstoff", "type": "schalter", "color": "blau", "min_value": 0, "max_value": 3},
        {"name": "Gravitation", "type": "slider", "color": "gelb", "min_value": 0, "max_value": 3},
        {"name": "Lebenserhaltung", "type": "schalter", "color": "grün", "min_value": 0, "max_value": 2},
        {"name": "Turbinen", "type": "slider", "color": "rot", "min_value": 0, "max_value": 4},
        {"name": "Dock", "type": "knopf", "color": "gelb", "min_value": 0, "max_value": 2},
        {"name": "Sensor Boost", "type": "slider", "color": "blau", "min_value": 0, "max_value": 5},
        {"name": "Plasma", "type": "schalter", "color": "rot", "min_value": 0, "max_value": 3},
        {"name": "Schildgenerator", "type": "knopf", "color": "grün", "min_value": 0, "max_value": 4},
        {"name": "Funk", "type": "slider", "color": "gelb", "min_value": 0, "max_value": 2},
        {"name": "Verteidigung", "type": "schalter", "color": "blau", "min_value": 0, "max_value": 3},
        {"name": "Warp", "type": "slider", "color": "grün", "min_value": 0, "max_value": 4},
        {"name": "Kühlung", "type": "schalter", "color": "gelb", "min_value": 0, "max_value": 2},
        {"name": "Analyse", "type": "knopf", "color": "blau", "min_value": 0, "max_value": 3},
        {"name": "Versorgung", "type": "slider", "color": "grün", "min_value": 0, "max_value": 5},
        {"name": "Stabilisator", "type": "schalter", "color": "rot", "min_value": 0, "max_value": 2},
        {"name": "Hangar", "type": "knopf", "color": "gelb", "min_value": 0, "max_value": 3},
        {"name": "Reaktor Sicherung", "type": "toggle", "color": "rot", "min_value": 0, "max_value": 1},
        {"name": "Orbit Dial", "type": "dial", "color": "blau", "min_value": 0, "max_value": 8},
        {"name": "Andock Taster", "type": "toggle", "color": "gelb", "min_value": 0, "max_value": 1},
        {"name": "Grav-Justierer", "type": "dial", "color": "grün", "min_value": 0, "max_value": 10},
    ]

    def __init__(self):
        self.clients = {}
        self.client_controls = {}
        self.client_control_specs = {}
        self.current_task = None
        self.score = 0
        self.game_active = False
        self.loop = None
        self.available_controls = self.CONTROL_LIBRARY.copy()
        self.extra_control_counter = 1
        self.problems = [
            "WARNUNG: Sauerstoff niedrig!",
            "ALARM: Energiekern überhitzt!",
            "ACHTUNG: Schilde schwach!",
            "GEFAHR: Antrieb ausgefallen!",
            "WARNUNG: Sensoren offline!"
        ]

    async def register_client(self, websocket):
        client_id = f"device_{len(self.clients) + 1}"
        self.clients[client_id] = websocket
        print(f"Neues Gerät verbunden: {client_id}")

        controls = self.generate_controls(client_id)
        self.client_controls[client_id] = controls

        # Sende Geräte-ID und initiale Konfiguration
        await websocket.send(json.dumps({
            "type": "init",
            "device_id": client_id,
            "controls": controls
        }))

        self.update_gui()

        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(data, client_id)
        except websockets.exceptions.ConnectionClosed:
            print(f"Gerät getrennt: {client_id}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]

            if client_id in self.client_controls:
                del self.client_controls[client_id]

            if client_id in self.client_control_specs:
                self.available_controls.extend(self.client_control_specs[client_id])
                del self.client_control_specs[client_id]

            if self.current_task and self.current_task.get("device_id") == client_id:
                self.current_task = None

            self.update_gui()

    def generate_controls(self, client_id):
        if len(self.available_controls) < 6:
            assigned_specs = []
            for specs in self.client_control_specs.values():
                assigned_specs.extend(specs)

            self.available_controls = [
                spec for spec in self.CONTROL_LIBRARY
                if spec not in assigned_specs
            ]

            if len(self.available_controls) < 6:
                # Falls nicht genug einzigartige Kontrollen verfügbar sind,
                # generieren wir zusätzliche Varianten mit nummerierten Namen.
                extra_controls = []
                while len(self.available_controls) + len(extra_controls) < 6:
                    template = random.choice(self.CONTROL_LIBRARY)
                    extra = template.copy()
                    extra["name"] = f"{template['name']} {self.extra_control_counter}"
                    extra_controls.append(extra)
                    self.extra_control_counter += 1

                self.available_controls.extend(extra_controls)

        selected_specs = random.sample(self.available_controls, k=6)
        for spec in selected_specs:
            self.available_controls.remove(spec)

        self.client_control_specs[client_id] = selected_specs

        controls = []
        for index, spec in enumerate(selected_specs):
            controls.append({
                "id": f"{client_id}_control_{index}",
                "type": spec["type"],
                "color": spec["color"],
                "label": spec["name"],
                "min_value": spec.get("min_value", 0),
                "max_value": spec.get("max_value", 3),
                "position": spec.get("min_value", 0)
            })

        return controls

    async def handle_message(self, data, client_id):
        if data["type"] == "control_change":
            await self.check_solution(data, client_id)

    async def check_solution(self, data, client_id):
        if not self.current_task:
            return

        if (client_id == self.current_task.get("device_id") and
            data["control_id"] == self.current_task["target_control"] and
            data["value"] == self.current_task["target_value"]):
            self.score += 10
            await self.broadcast({
                "type": "success",
                "message": "SUPER! Problem gelöst! ⭐",
                "score": self.score
            })
            self.current_task = None
            self.update_gui()
            await asyncio.sleep(2)
            await self.send_new_task()

    async def send_new_task(self):
        if not self.clients or not self.game_active:
            return

        device_id = random.choice(list(self.client_controls.keys()))
        available_controls = self.client_controls.get(device_id, [])

        if not available_controls:
            return

        control = random.choice(available_controls)
        target_value = self.generate_target_value(control)
        instruction = self.build_instruction(device_id, control, target_value)

        self.current_task = {
            "device_id": device_id,
            "target_control": control["id"],
            "target_value": target_value,
            "problem": random.choice(self.problems),
            "instruction": instruction
        }

        await self.broadcast({
            "type": "new_task",
            "problem": self.current_task["problem"],
            "instruction": instruction,
            "target_device": device_id
        })

        self.update_gui()

    def generate_target_value(self, control):
        min_value = control.get("min_value", 0)
        max_value = control.get("max_value", 3)

        if control["type"] in {"slider", "dial"}:
            return random.randint(min_value, max_value)

        if control["type"] == "schalter":
            return random.randint(min_value, max_value)

        if control["type"] == "toggle":
            return random.choice([min_value, max_value])

        # knopf
        target = random.randint(min_value + 1, max_value)
        return target

    def build_instruction(self, device_id, control, target_value):
        type_labels = {
            "schalter": "Schalter",
            "slider": "Regler",
            "knopf": "Knopf",
            "toggle": "Schalter",
            "dial": "Drehregler",
        }

        color = control.get("color", "").capitalize()
        label = control.get("label", "Kontrolle")
        type_label = type_labels.get(control.get("type"), "Kontrolle")

        if control["type"] in {"slider", "dial"}:
            return (f"{device_id.upper()}: Stelle den {color} {type_label} '{label}' auf Stufe {target_value}.")

        if control["type"] == "toggle":
            state = "AN" if target_value == control.get("max_value", 1) else "AUS"
            return (f"{device_id.upper()}: Schalte '{label}' ({color}) auf {state}.")

        if control["type"] == "schalter":
            return (f"{device_id.upper()}: Schalte '{label}' ({color}) auf Position {target_value}.")

        return (f"{device_id.upper()}: Drücke '{label}' ({color}) bis Anzeige {target_value} leuchtet.")

    async def broadcast(self, message):
        if self.clients:
            await asyncio.gather(
                *[client.send(json.dumps(message)) for client in self.clients.values()],
                return_exceptions=True
            )

    def update_gui(self):
        if hasattr(self, 'gui') and self.gui:
            try:
                self.gui.root.after(0, self.gui.update_display)
            except:
                pass
    
    async def start_game(self):
        self.game_active = True
        self.score = 0
        self.current_task = None
        await self.send_new_task()

    async def stop_game(self):
        self.game_active = False
        self.current_task = None

class GameGUI:
    def __init__(self, server):
        self.server = server
        self.server.gui = self
        self.root = tk.Tk()
        self.root.title("Weltraum-Kontrollzentrum 🚀")
        self.root.geometry("800x600")
        self.root.configure(bg="#001a33")
        
        # Titel
        title = tk.Label(self.root, text="🚀 WELTRAUM MISSION 🚀", 
                        font=("Arial", 24, "bold"), bg="#001a33", fg="#00ff00")
        title.pack(pady=20)
        
        # Punktestand
        self.score_label = tk.Label(self.root, text="Punkte: 0", 
                                    font=("Arial", 18), bg="#001a33", fg="#ffffff")
        self.score_label.pack(pady=10)
        
        # Status
        status_frame = tk.Frame(self.root, bg="#003366", relief=tk.RAISED, borderwidth=3)
        status_frame.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)
        
        tk.Label(status_frame, text="AKTUELLES PROBLEM:", 
                font=("Arial", 14, "bold"), bg="#003366", fg="#ffcc00").pack(pady=10)
        
        self.problem_label = tk.Label(status_frame, text="Warte auf Spielstart...", 
                                      font=("Arial", 16), bg="#003366", fg="#ff3333", 
                                      wraplength=600)
        self.problem_label.pack(pady=10)
        
        tk.Label(status_frame, text="ANWEISUNG:", 
                font=("Arial", 14, "bold"), bg="#003366", fg="#ffcc00").pack(pady=10)
        
        self.instruction_label = tk.Label(status_frame, text="---", 
                                          font=("Arial", 16), bg="#003366", fg="#00ffff",
                                          wraplength=600)
        self.instruction_label.pack(pady=10)
        
        # Verbundene Geräte
        self.devices_label = tk.Label(self.root, text="Verbundene Geräte: 0", 
                                      font=("Arial", 12), bg="#001a33", fg="#aaaaaa")
        self.devices_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(self.root, bg="#001a33")
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(button_frame, text="SPIEL STARTEN", 
                                      command=self.start_game, font=("Arial", 14, "bold"),
                                      bg="#00aa00", fg="white", padx=20, pady=10)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = tk.Button(button_frame, text="SPIEL STOPPEN", 
                                     command=self.stop_game, font=("Arial", 14, "bold"),
                                     bg="#aa0000", fg="white", padx=20, pady=10)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Server Info
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        ip_label = tk.Label(self.root, 
                           text=f"Server läuft auf: {local_ip}:8765\nÖffne auf Tablet/Smartphone: {local_ip} im Browser eingeben",
                           font=("Arial", 10), bg="#001a33", fg="#00ff00")
        ip_label.pack(pady=10)
        
        self.update_display()
        
    def update_display(self):
        self.score_label.config(text=f"Punkte: {self.server.score}")
        self.devices_label.config(text=f"Verbundene Geräte: {len(self.server.clients)}")
        
        if self.server.current_task:
            self.problem_label.config(text=self.server.current_task["problem"])
            self.instruction_label.config(text=self.server.current_task["instruction"])
    
    def start_game(self):
        if self.server.loop:
            asyncio.run_coroutine_threadsafe(self.server.start_game(), self.server.loop)
    
    def stop_game(self):
        if self.server.loop:
            asyncio.run_coroutine_threadsafe(self.server.stop_game(), self.server.loop)
    
    def run(self):
        self.root.mainloop()

def run_server(server):
    """Läuft im separaten Thread für asyncio"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    server.loop = loop
    
    async def start_websocket():
        async with websockets.serve(server.register_client, "0.0.0.0", 8765):
            print("🚀 Weltraum-Server gestartet auf Port 8765")
            await asyncio.Future()  # läuft für immer
    
    try:
        loop.run_until_complete(start_websocket())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

def main():
    server = SpaceGameServer()
    
    # Starte WebSocket Server in separatem Thread
    server_thread = Thread(target=lambda: run_server(server), daemon=True)
    server_thread.start()
    
    # Starte GUI im Hauptthread
    gui = GameGUI(server)
    gui.run()

if __name__ == "__main__":
    main()
