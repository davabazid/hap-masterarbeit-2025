

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 18:12:17 2025

@author: david
"""

import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import folium
import webbrowser
import os
import qrcode
import matplotlib.pyplot as plt

from C_hilfsfunktionen import simuliere_fall
from C_hilfsfunktionen import lade_radiosondendaten
from C_hilfsfunktionen import lade_flugpfad
from C_hilfsfunktionen import generiere_truemmer_szenario
from C_hilfsfunktionen import berechne_differenz_m
from C_hilfsfunktionen import erstelle_zeitverlauf_plot
from C_hilfsfunktionen import erstelle_radiosonden_plots

# Zentrum der Kreisbahn (fix definiert)
zentrum_lat = 28.518039819774355
zentrum_lon = -13.893774438364316
radius_m = 1974.34

# -----------------------------
# Benutzerdefinierte Höhe über GUI
# -----------------------------
def waehle_starthoehe_und_szenario():
    selected = {"hoehe": None, "szenario": None}

    def auswahl_bestaetigen():
        hoehe = combo_hoehe.get()
        szenario = combo_szenario.get()
        if hoehe and szenario:
            selected["hoehe"] = float(hoehe)
            selected["szenario"] = szenario
            root.destroy()

    root = tk.Tk()
    root.title("Start-Höhe und Szenario auswählen")
    root.geometry("350x200")
    root.attributes("-topmost", True)
    root.focus_force()
    root.lift()

    tk.Label(root, text="Start-Höhe (m):").pack(pady=5)
    combo_hoehe = ttk.Combobox(root, values=[str(h) for h in range(0, 20001, 100)], state="readonly")
    combo_hoehe.current(200)
    combo_hoehe.pack()

    szenarienliste = [
        "Antriebausfall", "Strukturbruch", "Steuerverlust",
        "Fluegelabriss", "Flat Spin", "Solarmodul", "Motorblock"
    ]
    tk.Label(root, text="Szenario:").pack(pady=5)
    combo_szenario = ttk.Combobox(root, values=szenarienliste, state="readonly")
    combo_szenario.current(0)
    combo_szenario.pack()

    tk.Button(root, text="Simulation starten", command=auswahl_bestaetigen).pack(pady=10)
    root.mainloop()
    return selected["hoehe"], selected["szenario"]

# -----------------------------
# Hauptsimulation mit Karte, Validierung & QR
# -----------------------------

plt.close('all')  # Alle vorherigen Plots schließen

df_radiosonde, _ = lade_radiosondendaten("radiosonde_data_60018_2025-04-18.xlsx")
df_flug = lade_flugpfad("flugbahn_200m_8pts.xlsx")

x_flight = pd.to_numeric(df_flug["longitude"], errors='coerce').values
y_flight = pd.to_numeric(df_flug["latitude"], errors='coerce').values
z_flight = pd.to_numeric(df_flug["altitude"], errors='coerce').values
vx = vy = vz = np.zeros_like(x_flight)

start_hoehe, szenarioname = waehle_starthoehe_und_szenario()
szenario = generiere_truemmer_szenario(szenarioname)

index = np.argmin(np.abs(z_flight - start_hoehe))
lon_start = x_flight[index]
lat_start = y_flight[index]

masse = szenario["masse"][0]
cw = szenario["cw_wert"][0]
cl = szenario["cl_wert"][0]
flaeche = szenario["flaeche"][0]

zeiten, daten, lat_impact, lon_impact = simuliere_fall(
    masse,
    cw,
    cl,
    flaeche,
    df_radiosonde,
    x_flight,
    y_flight,
    z_flight,
    vx,
    vy,
    vz,
    lon_start,
    lat_start,
    zeitschritt=0.01,
    start_hoehe=start_hoehe
)



fallzeit = zeiten[-1]
zentrum_dist_x, zentrum_dist_y = berechne_differenz_m(zentrum_lon, zentrum_lat, lon_impact, lat_impact)
distanz_zum_zentrum = np.sqrt(zentrum_dist_x**2 + zentrum_dist_y**2)
delta_x, delta_y = berechne_differenz_m(lon_start, lat_start, lon_impact, lat_impact)
luftlinie = np.sqrt(delta_x**2 + delta_y**2)

t_theorie = np.sqrt(2 * start_hoehe / 9.81)
v_theorie = 9.81 * t_theorie

text = (
    f"📋 Simulationsergebnis\n\n"
    f"🕸️ Start-Höhe: {start_hoehe:.1f} m\n"
    f"📌 Szenario: {szenarioname} "
    f"(Masse: {masse} kg, Cd: {cw}, Cl: {cl}, Fläche: {flaeche} m², "
    f"v_terminal: {daten['VZ [m/s]'].abs().max():.2f} m/s)\n"
    f"⏱️ Fallzeit: {fallzeit:.2f} s\n\n"
    f"🧭 Aufprall: {lat_impact:.6f}, {lon_impact:.6f}\n"
    f"📏 Distanz Start→Aufprall: {luftlinie:.2f} m"
    f"📏 Distanz Zentrum→Aufprall: {distanz_zum_zentrum:.2f} m"
    f"🧪 Theorie (ohne Luft): {t_theorie:.2f} s, v = {v_theorie:.1f} m/s"
)
print(text)

root = tk.Tk()
root.withdraw()
from datetime import datetime
heute = datetime.now().strftime("%d.%m.%Y")
messagebox.showinfo("Simulation abgeschlossen - David Aba " + heute, text)

# Interaktive Karte mit allen Elementen
karte = folium.Map(location=[zentrum_lat, zentrum_lon], zoom_start=14)
folium.Marker([lat_start, lon_start], tooltip="Start", icon=folium.Icon(color="green")).add_to(karte)
folium.Marker([lat_impact, lon_impact], tooltip="Aufprallpunkt", icon=folium.Icon(color="red")).add_to(karte)
folium.Marker([zentrum_lat, zentrum_lon], tooltip="Zentrum der Kreisbahn", icon=folium.Icon(color="blue")).add_to(karte)
folium.PolyLine([[lat_start, lon_start], [lat_impact, lon_impact]], color="blue", weight=2.5, tooltip="Fluglinie").add_to(karte)
folium.PolyLine([[zentrum_lat, zentrum_lon], [lat_impact, lon_impact]], color="black", weight=2, tooltip="Luftlinie zum Zentrum").add_to(karte)
folium.Circle(
    location=[zentrum_lat, zentrum_lon],
    radius=radius_m,
    color="blue",
    fill=False,
    weight=1.5,
    dash_array='10',
    tooltip="Kreisbahn"
).add_to(karte)

karte_path = "aufprallkarte_gesamt.html"
karte.save(karte_path)
webbrowser.open('file://' + os.path.realpath(karte_path))
webbrowser.open(f"https://www.google.com/maps?q={lat_impact},{lon_impact}")

# QR-Code
google_drive_link = "https://drive.google.com/file/d/1yKnnUTBDN1ZQOSeatAzcIk5EEJ6mXf2p/view?usp=drive_link"
qr_text = (
    f"📋 Start-Höhe: {start_hoehe:.0f} m\n"
    f"Fallzeit: {fallzeit:.2f} s\n"
    f"→ Longitude: {lon_impact:.6f}\n"
    f"→ Latitude : {lat_impact:.6f}\n"
    f"🌐 Karte: {google_drive_link}"
)
qr = qrcode.make(qr_text)
qr.save("qr_simulationsergebnis.png")
print("✅ QR-Code gespeichert als qr_simulationsergebnis.png")

# Validierungsplot
plt.figure(figsize=(8,5))
plt.plot(daten["Zeit [s]"], daten["Z [m]"], label="Simulation")
plt.axhline(y=start_hoehe, color='gray', linestyle='--', label=f"Start-Höhe: {start_hoehe:.0f} m")
plt.axhline(y=0, color='black', linestyle='--', label="Boden")
plt.xlabel("Zeit [s]")
plt.ylabel("Höhe [m]")
plt.title(f"Höhenprofil der Fallbewegung: {szenarioname}")
plt.grid()
plt.legend(title=(
    f"Masse: {masse} kg\n"
    f"Cd: {cw}, Cl: {cl}\n"
    f"Fläche: {flaeche} m²\n"
    f"v_terminal: {daten['VZ [m/s]'].abs().max():.2f} m/s"
))
plt.tight_layout()
filename_plot = f"verlauf_hoehe_zeit_{szenarioname.replace(' ', '_')}.png"
plt.savefig(filename_plot)
plt.show()
print(f"📈 Validierungsplot gespeichert als {filename_plot}")

# Zusatzplots
v_terminal = daten['VZ [m/s]'].abs().max()
erstelle_zeitverlauf_plot(daten, masse, cw, cl, flaeche, v_terminal, szenarioname)
erstelle_radiosonden_plots(df_radiosonde)
# Winddaten laden und analysieren

wind_df = pd.read_excel("radiosonde_data_60018_2025-04-18.xlsx")

# Windrichtungsverteilung (Windrose)
plt.figure(figsize=(8, 8))
ax = plt.subplot(111, polar=True)
wind_direction_rad = np.deg2rad(wind_df["DRCT"].dropna())
ax.hist(wind_direction_rad, bins=36, color='skyblue', edgecolor='black')
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_title("Windrichtung (Windrose)")
plt.tight_layout()
plt.savefig("windrose.png")
plt.show()

# Windprofil (Richtung und Geschwindigkeit mit Höhe)
plt.figure(figsize=(10, 6))
plt.quiver(
    np.zeros(len(wind_df)),  # X-Koordinate
    wind_df["HGHT"],         # Y-Koordinate = Höhe
    np.cos(np.deg2rad(wind_df["DRCT"])) * wind_df["SPED"],  # u-Komponente
    np.sin(np.deg2rad(wind_df["DRCT"])) * wind_df["SPED"],  # v-Komponente
    angles='xy', scale_units='xy', scale=1, color='teal', alpha=0.7
)
plt.xlabel("")
plt.ylabel("Höhe (m)")
plt.title("Windprofil – Richtung und Geschwindigkeit mit Höhe")
plt.grid(True)
plt.tight_layout()
plt.savefig("windprofil_hoehe.png")
plt.show()

# Werte nur ab Start-Höhe filtern
daten_gefiltert = daten[daten["Z [m]"] <= start_hoehe]

# Trajektorienplot: X-Position gegen Höhe
plt.figure(figsize=(8, 6))
plt.plot(daten["X [m]"], daten["Z [m]"], color='blue', label='X vs Höhe')
plt.xlabel("X-Position [m]")
plt.ylabel("Höhe [m]")
plt.title(f"X-Position über Höhe ({szenarioname})")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"x_vs_hoehe_{szenarioname.replace(' ', '_')}.png")
plt.show()
print(f"📈 X vs Höhe Plot gespeichert als x_vs_hoehe_{szenarioname.replace(' ', '_')}.png")

# Trajektorienplot: Y-Position gegen Höhe
plt.figure(figsize=(8, 6))
plt.plot(daten["Y [m]"], daten["Z [m]"], color='green', label='Y vs Höhe')
plt.xlabel("Y-Position [m]")
plt.ylabel("Höhe [m]")
plt.title(f"Y-Position über Höhe ({szenarioname})")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"y_vs_hoehe_{szenarioname.replace(' ', '_')}.png")
plt.show()
print(f"📈 Y vs Höhe Plot gespeichert als y_vs_hoehe_{szenarioname.replace(' ', '_')}.png")


# Trajektorienplot (X-Y Flugbahn Bodenebene)
plt.figure(figsize=(8, 6))
plt.plot(daten["X [m]"], daten["Y [m]"], color='blue', label='Trajektorie')
plt.scatter(0, 0, color='red', label='Startpunkt (0,0)', zorder=5)
plt.xlabel("X-Position [m]")
plt.ylabel("Y-Position [m]")
plt.title(f"Flugbahn am Boden ({szenarioname})")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.tight_layout()
plt.savefig(f"flugbahn_boden_{szenarioname.replace(' ', '_')}.png")
plt.show()
print(f"📈 Flugbahnplot gespeichert als flugbahn_boden_{szenarioname.replace(' ', '_')}.png")
