import threading
import socket
import tkinter as tk
from tkinter import scrolledtext
import datetime

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

class ChatServer:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Server")

        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=20)
        self.log_area.pack(padx=10, pady=10)

        self.message_entry = tk.Entry(root, width=50)
        self.message_entry.pack(padx=10, pady=5)

        self.send_button = tk.Button(root, text="Broadcast", command=self.server_broadcast)
        self.send_button.pack(padx=10, pady=5)

        self.start_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_button.pack(padx=10, pady=10)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)

        self.clients = set()
        self.clients_lock = threading.Lock()

    def log_message(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.config(state='disabled')
        self.log_area.yview(tk.END)

    def handle_client(self, conn, addr):
        self.log_message(f"[NEW CONNECTION] {addr} Connected")
        try:
            connected = True
            while connected:
                msg = conn.recv(1024).decode(FORMAT)
                if not msg:
                    break

                if msg == DISCONNECT_MESSAGE:
                    connected = False
                else:
                    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    broadcast_message = f"{time} [{addr}] {msg}"
                    self.log_message(broadcast_message)
                    self.broadcast(broadcast_message, conn)
        finally:
            with self.clients_lock:
                self.clients.remove(conn)
            conn.close()

    def server_broadcast(self, addr=ADDR):
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message=f"{time} [{addr}] "+self.message_entry.get()
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.sendall(message.encode(FORMAT))
                    self.message_entry.delete(0, tk.END)
                except Exception as e:
                    self.log_message(f"[ERROR] {e}")

    def broadcast(self, message, sender_conn=None):
        with self.clients_lock:
            for client in self.clients:
                if client != sender_conn:
                    try:
                        client.sendall(message.encode(FORMAT))
                    except Exception as e:
                        self.log_message(f"[ERROR] {e}")

    def start_server(self):
        self.start_button.config(state='disabled')
        self.log_message('[SERVER STARTED]!')
        self.server.listen()
        threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while True:
            conn, addr = self.server.accept()
            with self.clients_lock:
                self.clients.add(conn)
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

def start_server_gui():
    root = tk.Tk()
    ChatServer(root)
    root.mainloop()

if __name__ == "__main__":
    start_server_gui()


    