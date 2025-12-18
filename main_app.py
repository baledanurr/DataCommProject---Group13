import tkinter as tk
from tkinter import ttk
from Client1_TK import create_client1_ui
from Server_TK import create_server_ui
from Client2_TK import create_client2_ui

root = tk.Tk()
root.title("Cyber DataComm App")
root.geometry("1000x700")
root.configure(bg="#050014")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

frame1 = tk.Frame(notebook, bg="#050014")
frame2 = tk.Frame(notebook, bg="#050014")
frame3 = tk.Frame(notebook, bg="#050014")

notebook.add(frame1, text="CLIENT 1")
notebook.add(frame2, text="SERVER")
notebook.add(frame3, text="CLIENT 2")

create_client1_ui(frame1)
create_server_ui(frame2)
create_client2_ui(frame3)


root.mainloop()
