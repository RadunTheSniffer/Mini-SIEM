import socket
import ssl
import sqlite3
import threading
import json
import os

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL", "logs.db")

def create_table():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

create_table()

def store_log(log_message):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT INTO logs (message) VALUES (?)", (log_message,))
    conn.commit()
    conn.close()

def analyze_log(log_message):
    try:
        with open("rules.json", "r") as f:
            rules = json.load(f)
        # Placeholder: you can add rule application later
    except Exception:
        pass  # Skip analysis for now if file or logic isn't ready

def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                store_log(data)
                analyze_log(data)
            except:
                break

def start_socket_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(5)

    with context.wrap_socket(server_socket, server_side=True) as ssock:
        print("Secure server listening on port 12345...")
        while True:
            client_socket, addr = ssock.accept()
            print(f"Accepted connection from {addr}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()

class LogEntry(BaseModel):
    id: int
    message: str
    timestamp: str

@app.get("/logs/", response_model=list[LogEntry])
async def get_logs():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT id, message, timestamp FROM logs ORDER BY id DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "message": row[1], "timestamp": row[2]} for row in rows]

if __name__ == "__main__":
    threading.Thread(target=start_socket_server, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
