import asyncio
import websockets
import json
import random
import tkinter as tk
from threading import Thread

class SpaceGameServer:
    def __init__(self):
        self.clients = {}
        self.current_task = None
        self.score = 0
        self.game_active = False
        self.loop = None
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
        
        # Sende Geräte-ID und initiale Konfiguration
        await websocket.send(json.dumps({
            "type": "init",
            "device_id": client_id,
            "controls": self.generate_controls()
        }))
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(data, client_id)
        except websockets.exceptions.ConnectionClosed:
            print(f"Gerät getrennt: {client_id}")
            if client_id in self.clients:
                del self.clients[client_id]
            self.update_gui()
    
    def generate_controls(self):
        colors = ["rot", "grün", "blau", "gelb"]
        shapes = ["rund", "eckig"]
        control_types = ["schalter", "slider", "knopf"]
        
        controls = []
        for i in range(6):
            control = {
                "id": f"control_{i}",
                "type": random.choice(control_types),
                "color": random.choice(colors),
                "shape": random.choice(shapes) if random.random() > 0.5 else None,
                "position": 0
            }
            controls.append(control)
        return controls
    
    async def handle_message(self, data, client_id):
        if data["type"] == "control_change":
            await self.check_solution(data, client_id)
    
    async def check_solution(self, data, client_id):
        if not self.current_task:
            return
        
        if (data["control_id"] == self.current_task["target_control"] and
            data["value"] == self.current_task["target_value"]):
            self.score += 10
            await self.broadcast({
                "type": "success",
                "message": "SUPER! Problem gelöst! ⭐",
                "score": self.score
            })
            self.update_gui()
            await asyncio.sleep(2)
            await self.send_new_task()
    
    async def send_new_task(self):
        if not self.clients or not self.game_active:
            return
        
        # Wähle zufälliges Gerät und Kontrolle
        device_id = random.choice(list(self.clients.keys()))
        control_id = f"control_{random.randint(0, 5)}"
        target_value = random.randint(1, 3)
        
        # Hole Kontrollinformationen (simuliert)
        colors = ["rot", "grün", "blau", "gelb"]
        types = ["Schalter", "Slider", "Knopf"]
        
        instruction = f"{random.choice(colors).capitalize()} {random.choice(types)} auf Position {target_value}!"
        
        self.current_task = {
            "target_control": control_id,
            "target_value": target_value,
            "problem": random.choice(self.problems),
            "instruction": instruction
        }
        
        await self.broadcast({
            "type": "new_task",
            "problem": self.current_task["problem"],
            "instruction": instruction
        })
        
        self.update_gui()
    
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