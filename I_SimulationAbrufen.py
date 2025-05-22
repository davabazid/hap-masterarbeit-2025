# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 12:26:14 2025

@author: david

SAFE Version v4: Open scripts with VS Code normally.
Fallback to Notepad ONLY if VS Code command ('code') is not found.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

def run_selected_script():
    script = script_var.get()
    if script:
        try:
            scripts_folder = r"E:\\TheEnd"
            script_path = os.path.join(scripts_folder, script)

            if not os.path.isfile(script_path):
                messagebox.showerror("Error", f"Script not found:\n{script_path}")
                return

            subprocess.run(["python", script_path], check=True)
            messagebox.showinfo("Success", f"{script} finished successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", f"An error occurred while running {script}.")
    else:
        messagebox.showwarning("Warning", "Please select a script first.")

def show_info():
    script = script_var.get()
    if script:
        try:
            scripts_folder = r"Gaia:\\TheEnd"
            script_path = os.path.join(scripts_folder, script)

            if not os.path.isfile(script_path):
                messagebox.showerror("Error", f"The script was not found!\n\nChecked path:\n{script_path}")
                return

            try:
                subprocess.Popen(["code", script_path])
                messagebox.showinfo("Opened", f"{script} opened in VS Code.")
            except FileNotFoundError:
                subprocess.Popen(["notepad.exe", script_path])
                messagebox.showinfo("Opened", f"{script} opened in Notepad (VS Code not found).")

        except Exception as e:
            messagebox.showerror("Error", f"General error:\n{e}")
    else:
        messagebox.showwarning("Warning", "Please select a script first.")

def close_app():
    root.destroy()

# -----------------------
# Create GUI window
# -----------------------
root = tk.Tk()
root.title("Simulation and Data Retrieval GUI")
root.geometry("450x220")
root.resizable(False, False)

# Adjust style
style = ttk.Style()
style.configure('TButton', font=('Arial', 10), padding=6)
style.configure('TLabel', font=('Arial', 10))
style.configure('TCombobox', font=('Arial', 10))

# List of scripts
scripts = [
    "A_Simu_FlightPath_12.04.2025.py",
    "B_Simu_radiosonden_daten_abholen_10.04.2025.py",
    "J_Wind.py",
    "D_SimuEinzelpunktFinal.py",
    "E_simu_berechnung_alle_aufprallpunkte.py",
    "F_simu_darstellung_alle_aufprallpunkte.py",
    "G_simu_InteraktivKarten.py",
    "H_simu_darstellung_(Gauß_Mittelpunkt)_alle_aufprallpunkte.py",
    "H_simu_darstellung_(Gauß_Bahnzentrum)_alle_aufprallpunkte.py",
    "C_hilfsfunktionen.py",
    "SkripteOeffnen_GUI.py"
]

# Dropdown selection
script_var = tk.StringVar()
label = ttk.Label(root, text="Select a Script:")
label.pack(pady=10)

dropdown = ttk.Combobox(root, textvariable=script_var, values=scripts, state="readonly", width=60)
dropdown.pack(pady=5)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=15)

start_button = ttk.Button(button_frame, text="Start Simulation", command=run_selected_script)
start_button.grid(row=0, column=0, padx=10)

info_button = ttk.Button(button_frame, text="Show Script", command=show_info)
info_button.grid(row=0, column=1, padx=10)

close_button = ttk.Button(button_frame, text="Close", command=close_app)
close_button.grid(row=0, column=2, padx=10)

# -----------------------
# Start GUI
# -----------------------
root.mainloop()