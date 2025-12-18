import socket
import threading
import tkinter as tk
from tkinter import ttk

HOST = "127.0.0.1"
PORT = 6000

root = None
log_box = None



def calculate_parity(text: str) -> str:
    total_ones = sum(bin(ord(c)).count("1") for c in text)
    return "0" if total_ones % 2 == 0 else "1"


def calculate_2d_parity(text: str):
    padded = text.ljust(64, "#")
    matrix = [padded[i:i + 8] for i in range(0, 64, 8)]

    row_parity = ""
    col_parity = ""

    for row in matrix:
        ones = sum(bin(ord(c)).count("1") for c in row)
        row_parity += "0" if ones % 2 == 0 else "1"

    for col in range(8):
        ones = sum(bin(ord(matrix[r][col])).count("1") for r in range(8))
        col_parity += "0" if ones % 2 == 0 else "1"

    return row_parity + col_parity


def crc16(text: str):
    poly = 0x1021
    reg = 0xFFFF

    for char in text:
        reg ^= (ord(char) << 8)
        for _ in range(8):
            if reg & 0x8000:
                reg = (reg << 1) ^ poly
            else:
                reg <<= 1
            reg &= 0xFFFF

    return format(reg, "04X")


def hamming_check(encoded: str):
    if len(encoded) % 7 != 0:
        return "CORRUPTED"

    blocks = [encoded[i:i + 7] for i in range(0, len(encoded), 7)]
    error_found = False

    for block in blocks:
        p1 = int(block[0])
        p2 = int(block[1])
        d1 = int(block[2])
        p4 = int(block[3])
        d2 = int(block[4])
        d3 = int(block[5])
        d4 = int(block[6])

        c1 = (d1 ^ d2 ^ d4) % 2
        c2 = (d1 ^ d3 ^ d4) % 2
        c4 = (d2 ^ d3 ^ d4) % 2

        if c1 != p1 or c2 != p2 or c4 != p4:
            error_found = True

    return "CORRUPTED" if error_found else "OK"


def append_log(text: str, tag=None):
    if tag:
        log_box.insert(tk.END, text + "\n", tag)
    else:
        log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)


def start_receiver():
    append_log("🟢 Receiver started, Waiting for packet from Server...\n", "info")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()

        while True:
            conn, addr = server.accept()
            with conn:
                packet = conn.recv(4096).decode("utf-8")
                if not packet:
                    continue

                append_log(f"📥 Incoming Packet:\n{packet}", "in")

                try:
                    incoming_data, method, incoming_control = packet.split("|")
                except:
                    append_log("❌ The packet format is damaged!\n", "error")
                    continue

                if method == "PARITY":
                    computed = calculate_parity(incoming_data)

                elif method == "2DPARITY":
                    computed = calculate_2d_parity(incoming_data)

                elif method == "CRC16":
                    computed = crc16(incoming_data)

                elif method == "HAMMING":
                    r = hamming_check(incoming_control)
                    computed = incoming_control
                    status = "DATA CORRECT" if r == "OK" else "DATA CORRUPTED"
                else:
                    computed = "0"

                if method != "HAMMING":  # Normal methods
                    status = "DATA CORRECT" if computed == incoming_control else "DATA CORRUPTED"

                append_log("➡ DETAILS:", "info")
                append_log(f"   Data              : {incoming_data}")
                append_log(f"   Method            : {method}")
                append_log(f"   Sent Check Bits   : {incoming_control}")
                append_log(f"   Computed Check    : {computed}")

                tag = "ok" if status == "DATA CORRECT" else "bad"
                append_log(f"   Status            : {status}", tag)
                append_log("-" * 60 + "\n")


def start_receiver_thread():
    t = threading.Thread(target=start_receiver, daemon=True)
    t.start()



def init_ui():
    global log_box

    root.configure(bg="#050014")
    root.pack_propagate(False)

    header = tk.Frame(root, bg="#090021", bd=2, relief="ridge")
    header.pack(fill="x", padx=8, pady=8)

    tk.Label(
        header,
        text="CLIENT 2  //  RECEIVER + ERROR CHECKER",
        font=("Consolas", 16, "bold"),
        bg="#090021",
        fg="#ff00ff"
    ).pack(side="left", padx=10, pady=4)

    tk.Label(
        header,
        text="PARITY · 2D PARITY · CRC16 · HAMMING CHECK",
        font=("Consolas", 9),
        bg="#090021",
        fg="#00ffe1"
    ).pack(side="right", padx=10)

    content = tk.Frame(root, bg="#050014")
    content.pack(fill="both", expand=True, padx=10, pady=5)

    tk.Button(
        content,
        text="START RECEIVER",
        command=start_receiver_thread,
        font=("Consolas", 11, "bold"),
        bg="#2196F3",
        fg="#050014",
        activebackground="#64b5ff",
        width=20
    ).pack(pady=5)

    log_frame = tk.LabelFrame(
        content,
        text=" RECEIVER LOG ",
        font=("Consolas", 10),
        bg="#050014",
        fg="#00ffe1",
        bd=2,
        relief="ridge",
        labelanchor="n"
    )
    log_frame.pack(fill="both", expand=True, pady=8)

    log_box = tk.Text(
        log_frame,
        height=22,
        width=90,
        bg="#050014",
        fg="#00ffe1",
        font=("Consolas", 9),
        insertbackground="#00ffe1",
        relief="flat",
        highlightthickness=1,
        highlightbackground="#ff00ff",
        highlightcolor="#ff00ff"
    )
    log_box.pack(fill="both", expand=True, padx=5, pady=5)

    log_box.tag_config("info", foreground="#00ff90")
    log_box.tag_config("in", foreground="#00ffe1")
    log_box.tag_config("ok", foreground="#00ff90")
    log_box.tag_config("bad", foreground="#ff5555")
    log_box.tag_config("error", foreground="#ff5555")



def create_client2_ui(parent):
    global root
    root = parent
    init_ui()
