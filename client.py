import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")

        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=20)
        self.chat_area.pack(padx=10, pady=10)

        self.message_entry = tk.Entry(root, width=50)
        self.message_entry.pack(padx=10, pady=5)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)

        self.client = self.connect_to_server()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def connect_to_server(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        return client

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode(FORMAT)
                if message:
                    self.display_message(message)
            except Exception as e:
                print(f"[ERROR] {e}")
                break

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.client.sendall(message.encode(FORMAT))
            self.message_entry.delete(0, tk.END)
            if message == DISCONNECT_MESSAGE:
                self.client.close()
                self.root.quit()

def start_client():
    root = tk.Tk()
    ChatClient(root)
    root.mainloop()

if __name__ == "__main__":
    start_client()

    