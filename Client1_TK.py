import socket
import tkinter as tk
from tkinter import ttk

HOST = "127.0.0.1"
PORT = 5000

root = None
entry_text = None
combo_method = None
log = None


def calculate_parity(text: str) -> str:
    total_ones = sum(bin(ord(c)).count("1") for c in text)
    return "0" if total_ones % 2 == 0 else "1"


def calculate_2d_parity(text: str):
    padded = text.ljust(64, "#")
    matrix = [padded[i:i+8] for i in range(0, 64, 8)]

    row_parity = ""
    col_parity = ""

    for row in matrix:
        ones = sum(bin(ord(c)).count("1") for c in row)
        row_parity += "0" if ones % 2 == 0 else "1"

    for col in range(8):
        ones = sum(bin(ord(matrix[r][col])).count("1") for r in range(8))
        col_parity += "0" if ones % 2 == 0 else "1"

    return row_parity + col_parity


def crc16(data: str):
    poly = 0x1021
    reg = 0xFFFF

    for char in data:
        reg ^= (ord(char) << 8)
        for _ in range(8):
            if reg & 0x8000:
                reg = (reg << 1) ^ poly
            else:
                reg <<= 1
            reg &= 0xFFFF

    return format(reg, "04X")


def hamming_encode(text: str):
    encoded = ""
    for ch in text:
        b = format(ord(ch), "08b")
        d1, d2, d3, d4 = map(int, b[:4])

        p1 = (d1 ^ d2 ^ d4) % 2
        p2 = (d1 ^ d3 ^ d4) % 2
        p4 = (d2 ^ d3 ^ d4) % 2

        encoded += f"{p1}{p2}{d1}{p4}{d2}{d3}{d4}"

    return encoded


def build_packet(text: str, method: str) -> str:
    if method == "PARITY":
        control = calculate_parity(text)
    elif method == "2DPARITY":
        control = calculate_2d_parity(text)
    elif method == "CRC16":
        control = crc16(text)
    elif method == "HAMMING":
        control = hamming_encode(text)
    else:
        control = "0"

    return f"{text}|{method}|{control}"



def send_packet():
    text = entry_text.get()
    method = combo_method.get()

    if text.strip() == "":
        log.insert(tk.END, "❌  Please enter text!\n", "error")
        log.see(tk.END)
        return

    packet = build_packet(text, method)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(packet.encode("utf-8"))

        log.insert(tk.END, f"📤 The Sent Package:\n{packet}\n\n", "send")
    except Exception as e:
        log.insert(tk.END, f"⚠ Connection error: {e}\n\n", "error")

    log.see(tk.END)


def init_ui():
    global entry_text, combo_method, log

    root.configure(bg="#050014")
    root.pack_propagate(False)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Cyber.TCombobox",
        fieldbackground="#0b0025",
        background="#0b0025",
        foreground="#00ffe1",
        bordercolor="#ff00ff",
        arrowsize=18
    )

    header_frame = tk.Frame(root, bg="#090021", bd=2, relief="ridge")
    header_frame.pack(fill="x", pady=8, padx=8)

    tk.Label(
        header_frame,
        text="CLIENT 1  //  CYBER DATA SENDER",
        font=("Consolas", 16, "bold"),
        bg="#090021",
        fg="#ff00ff"
    ).pack(side="left", padx=10)

    tk.Label(
        header_frame,
        text="PARITY · 2D PARITY · CRC16 · HAMMING",
        font=("Consolas", 9),
        bg="#090021",
        fg="#00ffe1"
    ).pack(side="right", padx=10)


    content = tk.Frame(root, bg="#050014")
    content.pack(fill="both", expand=True, padx=10, pady=5)

    tk.Label(content, text="Enter text:",
             font=("Consolas", 11),
             bg="#050014", fg="#ffea00").grid(row=0, column=0, sticky="w")

    entry_text = tk.Entry(
        content, width=45,
        font=("Consolas", 11),
        bg="#0b0025", fg="#00ffe1",
        insertbackground="#00ffe1"
    )
    entry_text.grid(row=1, column=0, columnspan=2, pady=4, sticky="w")

    tk.Label(content, text="Choose method:",
             font=("Consolas", 11),
             bg="#050014", fg="#ffea00").grid(row=2, column=0, sticky="w")

    combo_method = ttk.Combobox(
        content,
        values=["PARITY", "2DPARITY", "CRC16", "HAMMING"],
        style="Cyber.TCombobox",
        state="readonly",
        font=("Consolas", 10)
    )
    combo_method.current(0)
    combo_method.grid(row=3, column=0, sticky="w", pady=4)

    tk.Button(
        content,
        text="SEND →",
        command=send_packet,
        font=("Consolas", 11, "bold"),
        bg="#ff00ff", fg="#050014",
        activebackground="#ff66ff",
        width=12
    ).grid(row=3, column=1, sticky="e", padx=5)

    log_frame = tk.LabelFrame(
        content,
        text=" TRANSMISSION LOG ",
        font=("Consolas", 10),
        bg="#050014",
        fg="#00ffe1",
        bd=2,
        relief="ridge",
        labelanchor="n"
    )
    log_frame.grid(row=4, column=0, columnspan=2, pady=12, sticky="nsew")

    log = tk.Text(
        log_frame,
        height=12,
        width=70,
        bg="#050014",
        fg="#00ffe1",
        font=("Consolas", 9),
        insertbackground="#00ffe1",
        relief="flat",
        highlightbackground="#ff00ff"
    )
    log.pack(fill="both", expand=True, padx=5, pady=5)

    log.tag_config("send", foreground="#00ff90")
    log.tag_config("error", foreground="#ff5555")


def create_client1_ui(parent):
    global root
    root = parent
    init_ui()

