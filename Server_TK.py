import socket
import random
import threading
import tkinter as tk
from tkinter import ttk

HOST = "127.0.0.1"
PORT_FROM_CLIENT1 = 5000
HOST_TO_CLIENT2 = "127.0.0.1"
PORT_TO_CLIENT2 = 6000

server_running = False

root = None
server_log = None
combo_error = None


def bit_flip(text):
    if not text:
        return text
    idx = random.randrange(len(text))
    return text[:idx] + chr(ord(text[idx]) ^ 1) + text[idx+1:]


def char_substitution(text):
    if not text:
        return text
    idx = random.randrange(len(text))
    return text[:idx] + chr(random.randint(65, 90)) + text[idx+1:]


def char_deletion(text):
    if len(text) < 2:
        return text
    idx = random.randrange(len(text))
    return text[:idx] + text[idx+1:]


def char_insertion(text):
    if not text:
        return text
    idx = random.randint(0, len(text))
    return text[:idx] + chr(random.randint(97, 122)) + text[idx:]


def char_swap(text):
    if len(text) < 2:
        return text
    idx = random.randrange(len(text) - 1)
    return text[:idx] + text[idx+1] + text[idx] + text[idx+2:]


def burst_error(text):
    if len(text) < 4:
        return text
    start = random.randrange(len(text) - 3)
    end = min(start + random.randint(3, 8), len(text))
    corrupted = ''.join(chr(random.randint(33, 126)) for _ in range(end - start))
    return text[:start] + corrupted + text[end:]


def multiple_bit_flips(text):
    if not text:
        return text
    t = list(text)
    for _ in range(random.randint(2, 5)):
        i = random.randrange(len(t))
        t[i] = chr(ord(t[i]) ^ 1)
    return "".join(t)


def apply_error(method, text):
    return {
        "Bit Flip": bit_flip,
        "Char Substitution": char_substitution,
        "Char Deletion": char_deletion,
        "Insert Random Char": char_insertion,
        "Swap Adjacent": char_swap,
        "Burst Error": burst_error,
        "Multiple Bit Flips": multiple_bit_flips,
        "No Error": lambda x: x
    }.get(method, lambda x: x)(text)


def start_server():
    global server_running
    server_running = True

    server_log.insert(tk.END, "🔵 Server started. Waiting for Client1...\n", "info")
    server_log.see(tk.END)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT_FROM_CLIENT1))
        server.listen()

        while server_running:
            conn, _ = server.accept()
            with conn:
                data = conn.recv(4096).decode("utf-8")
                if not data:
                    continue

                server_log.insert(tk.END, f"\n📥 Incoming Packet:\n{data}\n", "in")
                server_log.see(tk.END)

                try:
                    incoming_text, method, control = data.split("|")
                except:
                    server_log.insert(tk.END, "❌ The packet format is wrong!\n", "error")
                    server_log.see(tk.END)
                    continue

                error_method = combo_error.get()

                corrupted = apply_error(error_method, incoming_text)
                new_packet = f"{corrupted}|{method}|{control}"

                server_log.insert(
                    tk.END,
                    f"💥 Corrupted Packet ({error_method}):\n{new_packet}\n",
                    "corrupt"
                )
                server_log.insert(tk.END, "📤 Forwarded to Client2.\n", "info")
                server_log.see(tk.END)

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as out:
                    out.connect((HOST_TO_CLIENT2, PORT_TO_CLIENT2))
                    out.sendall(new_packet.encode("utf-8"))


def start_server_thread():
    threading.Thread(target=start_server, daemon=True).start()



def init_ui():
    global server_log, combo_error

    root.configure(bg="#060018")
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

    header = tk.Frame(root, bg="#0a0020", bd=2, relief="ridge")
    header.pack(fill="x", padx=10, pady=10)

    tk.Label(
        header,
        text="SERVER  //  ERROR INJECTION HUB",
        font=("Consolas", 16, "bold"),
        fg="#ff00ff",
        bg="#0a0020"
    ).pack(side="left", padx=10)

    tk.Label(
        header,
        text="BIT FLIP · INSERT · DELETE · BURST",
        font=("Consolas", 9),
        fg="#00ffe1",
        bg="#0a0020"
    ).pack(side="right", padx=10)

    control = tk.Frame(root, bg="#060018")
    control.pack(fill="x", padx=20, pady=5)

    tk.Label(
        control,
        text="Error Method:",
        font=("Consolas", 11),
        fg="#ffea00",
        bg="#060018"
    ).grid(row=0, column=0, sticky="w", pady=4)



    combo_error = ttk.Combobox(
        control,
        values=[
            "Bit Flip",
            "Char Substitution",
            "Char Deletion",
            "Insert Random Char",
            "Swap Adjacent",
            "Burst Error",
            "Multiple Bit Flips",
            "No Error"
        ],
        state="readonly",
        width=25,
        style = "Cyber.TCombobox"
    )
    combo_error.current(0)
    combo_error.grid(row=1, column=0, sticky="w")


    tk.Button(
        control,
        text="START SERVER",
        command=start_server_thread,
        font=("Consolas", 11, "bold"),
        bg="#00ffe1",
        fg = "#060018",
        activebackground = "#33fff3",
        relief = "flat",
        width = 16
    ).grid(row=1, column=1, padx=15)

    log_frame = tk.LabelFrame(
        root,
        text=" SERVER LOG ",
        font=("Consolas", 10),
        fg="#00ffe1",
        bg="#060018",
        bd=2,
        relief="ridge",
        labelanchor="n"
    )
    log_frame.pack(fill="both", expand=True, padx=15, pady=10)


    server_log = tk.Text(
        log_frame,
        bg="#060018",
        fg="#00ffe1",
        font=("Consolas", 9),
        insertbackground="#00ffe1",
        relief="flat",
        highlightthickness=1,
        highlightbackground="#ff00ff",
        highlightcolor="#ff00ff"
    )
    server_log.pack(fill="both", expand=True, padx=8, pady=8)

    server_log.tag_config("info", foreground="#00ff90")
    server_log.tag_config("in", foreground="#00ffe1")
    server_log.tag_config("corrupt", foreground="#ffea00")
    server_log.tag_config("error", foreground="#ff5555")


def create_server_ui(parent):
    global root
    root = parent
    init_ui()
