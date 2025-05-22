# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 07:30:24 2025

@author: david
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 2025

@author: david

Simple GUI to open predefined Python scripts from E:\TheEnd directly in Visual Studio Code.
Static list of scripts, no auto-scan.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

def open_in_vscode():
    script = script_var.get()
    if script:
        script_path = os.path.join(scripts_folder, script)

        if not os.path.isfile(script_path):
            messagebox.showerror("Error", f"The script was not found:\n{script_path}")
            return

        try:
            subprocess.Popen(["code", script_path])
            messagebox.showinfo("Opened", f"{script} opened in VS Code.")
        except FileNotFoundError:
            messagebox.showerror("Error", "VS Code (code) not found on this system.")
    else:
        messagebox.showwarning("Warning", "Please select a script first.")

def close_app():
    root.destroy()

# -----------------------
# Settings
# -----------------------
scripts_folder = r"E:\\TheEnd"

# Static script list
scripts = [
    "A_Simu_FlightPath_12.04.2025.py",
    "B_Simu_radiosonden_daten_abholen_10.04.2025.py",
    "J_Wind.py",
    "D_SimuEinzelpunktFinal.py",
    "F_simu_darstellung_alle_aufprallpunkte.py",
    "G_simu_InteraktivKarten.py",
    "H_simu_darstellung_(Gauß_Mittelpunkt)_alle_aufprallpunkte.py",
    "H_simu_darstellung_(Gauß_Bahnzentrum)_alle_aufprallpunkte.py",
    "C_hilfsfunktionen.py",
    "E_simu_berechnung_alle_aufprallpunkte.py"
]

# -----------------------
# Create GUI window
# -----------------------
root = tk.Tk()
root.title("Skripte Öffnen - VS Code")
root.geometry("450x200")
root.resizable(False, False)

# Style
style = ttk.Style()
style.configure('TButton', font=('Arial', 10), padding=6)
style.configure('TLabel', font=('Arial', 10))
style.configure('TCombobox', font=('Arial', 10))

# Widgets
label = ttk.Label(root, text="Select a Script:")
label.pack(pady=10)

script_var = tk.StringVar()
dropdown = ttk.Combobox(root, textvariable=script_var, values=scripts, state="readonly", width=60)
dropdown.pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=15)

open_button = ttk.Button(button_frame, text="Open in VS Code", command=open_in_vscode)
open_button.grid(row=0, column=0, padx=10)

close_button = ttk.Button(button_frame, text="Close", command=close_app)
close_button.grid(row=0, column=1, padx=10)

# -----------------------
# Start GUI
# -----------------------
root.mainloop()