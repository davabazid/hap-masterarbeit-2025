# (Neue Version: Alles um Flugbahnzentrum statt Mittelwert)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import tkinter as tk
from tkinter import filedialog, ttk
import simplekml
import os
import webbrowser

# ------------------------------
# Hilfsfunktionen
# ------------------------------

def waehle_szenario():
    root = tk.Tk()
    root.title("Szenario auswählen")
    root.geometry("400x200")
    selected = {"szenario": None}

    def bestaetigen():
        selected["szenario"] = combo.get()
        root.destroy()

    def abbrechen():
        selected["szenario"] = None
        root.destroy()

    tk.Label(root, text="Bitte Szenario auswählen:").pack(pady=10)

    szenarien = [
        "aufprallpunkte_Antriebausfall.csv",
        "aufprallpunkte_Steuerverlust.csv",
        "aufprallpunkte_Strukturbruch.csv",
        "aufprallpunkte_Fluegelabriss.csv",
        "aufprallpunkte_Flat Spin.csv",
        "aufprallpunkte_Solarmodul.csv",
        "aufprallpunkte_Motorblock.csv"
    ]

    combo = ttk.Combobox(root, values=szenarien, state="readonly", width=40)
    combo.current(0)
    combo.pack(pady=5)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Button(frame, text="OK", width=12, command=bestaetigen).grid(row=0, column=0, padx=5)
    tk.Button(frame, text="Abbrechen", width=12, command=abbrechen).grid(row=0, column=1, padx=5)

    root.mainloop()
    return selected["szenario"]

def generate_risk_map_single_point(impact_x, impact_y, sigma, grid_size=300, extent=0.02):
    x_values = np.linspace(impact_x - extent, impact_x + extent, grid_size)
    y_values = np.linspace(impact_y - extent, impact_y + extent, grid_size)
    x_grid, y_grid = np.meshgrid(x_values, y_values)

    dist = np.sqrt((x_grid - impact_x)**2 + (y_grid - impact_y)**2)

    risk_map = (1 / (2 * np.pi * sigma**2)) * np.exp(-dist**2 / (2 * sigma**2))

    integral = np.trapezoid(np.trapezoid(risk_map, x_values), y_values)
    risk_map /= integral

    return risk_map, x_grid, y_grid

def calculate_probability_within_radius(risk_map, x_grid, y_grid, impact_x, impact_y, radius_km):
    distance_grid = np.sqrt((x_grid - impact_x)**2 + (y_grid - impact_y)**2)
    radius_deg = radius_km / 111
    mask = distance_grid <= radius_deg
    probability = np.sum(risk_map[mask])
    return probability

# ------------------------------
# 1. Datei wählen und laden
# ------------------------------

szenario_datei = waehle_szenario()

if not szenario_datei:
    print("❌ Kein Szenario ausgewählt.")
    exit()

file_path = szenario_datei

if not os.path.isfile(file_path):
    print(f"❌ Datei nicht gefunden: {file_path}")
    exit()

df = pd.read_csv(file_path)

# ------------------------------
# 2. Flugbahnzentrum definieren
# ------------------------------
zentrum_longitude = -13.893774438364316
zentrum_latitude = 28.518039819774355

print(f"Zentrum Longitude: {zentrum_longitude:.6f}")
print(f"Zentrum Latitude: {zentrum_latitude:.6f}")

# Sigma neu berechnen (mittlere quadratische Entfernung zum Zentrum)
abstaende = np.sqrt((df["Longitude Aufprall"] - zentrum_longitude)**2 + (df["Latitude Aufprall"] - zentrum_latitude)**2)
sigma_neu = abstaende.mean()

print(f"Neues Sigma (basierend auf Flugbahnzentrum): {sigma_neu:.6f} Grad")

# ------------------------------
# 3. Scatterplot aller Aufprallpunkte
# ------------------------------
plt.figure(figsize=(10, 8))
plt.scatter(df["Longitude Aufprall"], df["Latitude Aufprall"], c="darkgreen", s=10, alpha=0.7)
plt.scatter(zentrum_longitude, zentrum_latitude, c='red', marker='x', label="Flugbahnzentrum")
plt.xlabel("Längengrad")
plt.ylabel("Breitengrad")
plt.title("Alle Aufprallpunkte (um Flugbahnzentrum)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# ------------------------------
# 3.1 Histogramme Longitude und Latitude
# ------------------------------
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

axs[0].hist(df["Longitude Aufprall"], bins=30, color='skyblue', edgecolor='black', density=True)
axs[0].axvline(zentrum_longitude, color='red', linestyle='--', label='Flugbahnzentrum')
axs[0].set_xlabel("Longitude")
axs[0].set_ylabel("Dichte")
axs[0].set_title("Histogramm Longitude")
axs[0].grid(True)
axs[0].legend()

axs[1].hist(df["Latitude Aufprall"], bins=30, color='lightgreen', edgecolor='black', density=True)
axs[1].axvline(zentrum_latitude, color='red', linestyle='--', label='Flugbahnzentrum')
axs[1].set_xlabel("Latitude")
axs[1].set_ylabel("Dichte")
axs[1].set_title("Histogramm Latitude")
axs[1].grid(True)
axs[1].legend()

plt.tight_layout()
plt.show()

# ------------------------------
# 4. Risikokarte erzeugen
# ------------------------------
risk_map, xg, yg = generate_risk_map_single_point(
    impact_x = zentrum_longitude,
    impact_y = zentrum_latitude,
    sigma = sigma_neu,
    grid_size = 300,
    extent = 0.02
)

# ------------------------------
# 5. Risikokarte plotten
# ------------------------------
plt.figure(figsize=(8, 6))
plt.contourf(xg, yg, risk_map, levels=30, cmap='hot')
plt.colorbar(label="Wahrscheinlichkeit pro Fläche")
plt.scatter(zentrum_longitude, zentrum_latitude, c='blue', marker='x', label="Flugbahnzentrum")

for faktor, farbe in zip([1, 2, 3], ['green', 'orange', 'red']):
    kreis = plt.Circle((zentrum_longitude, zentrum_latitude), radius=sigma_neu * faktor, color=farbe, fill=False, linestyle='--', label=f"{faktor}σ")
    plt.gca().add_artist(kreis)

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Risikokarte um Flugbahnzentrum")
plt.legend()
plt.grid(True)
plt.gca().set_aspect(1/np.cos(np.radians(zentrum_latitude)))
plt.tight_layout()
plt.show()

# ------------------------------
# 6. Tabelle der Wahrscheinlichkeiten speichern und plotten
# ------------------------------
radien_km = np.arange(1, 21, 1)
wahrscheinlichkeiten = []

for r in radien_km:
    prob = calculate_probability_within_radius(risk_map, xg, yg, zentrum_longitude, zentrum_latitude, r)
    wahrscheinlichkeiten.append(prob)

tabelle = pd.DataFrame({
    "Radius (km)": radien_km,
    "Wahrscheinlichkeit (%)": np.array(wahrscheinlichkeiten) * 100
})

excel_filename = "wahrscheinlichkeiten_pro_radius.xlsx"
tabelle.to_excel(excel_filename, index=False)
print(f"✅ Tabelle gespeichert als: {excel_filename}")

plt.figure(figsize=(8, 6))
plt.plot(tabelle["Radius (km)"], tabelle["Wahrscheinlichkeit (%)"], marker="o", color="blue")
plt.title("Trefferwahrscheinlichkeit innerhalb Radius")
plt.xlabel("Radius [km]")
plt.ylabel("Wahrscheinlichkeit [%]")
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------
# 7. Satellitenkarte (Folium)
# ------------------------------
karte = folium.Map(
    location=[zentrum_latitude, zentrum_longitude],
    zoom_start=13,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr='Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye'
)

# Marker für Zentrum
folium.Marker(
    location=[zentrum_latitude, zentrum_longitude],
    popup="Flugbahnzentrum",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(karte)

# σ-Zonen (Kreise)
for faktor, farbe in zip([1, 2, 3], ["green", "orange", "red"]):
    folium.Circle(
        location=[zentrum_latitude, zentrum_longitude],
        radius=sigma_neu * faktor * 111000,
        color=farbe,
        fill=False,
        weight=2,
        tooltip=f"{faktor}σ-Zone"
    ).add_to(karte)

# Heatmap der Aufprallpunkte
heat_data = list(zip(df["Latitude Aufprall"], df["Longitude Aufprall"]))
HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(karte)

# Jetzt erst speichern und öffnen
karte.save("risikokarte_zentrum.html")
webbrowser.open('file://' + os.path.realpath("risikokarte_zentrum.html"))

# ------------------------------
# 8. Export als KML
# ------------------------------
kml = simplekml.Kml()
kml.newpoint(name="Flugbahnzentrum", coords=[(zentrum_longitude, zentrum_latitude)])

for faktor, farbe in zip([1, 2, 3], ["green", "orange", "red"]):
    kreis_punkte = []
    radius_meter = sigma_neu * faktor * 111000
    n_points = 72

    for i in range(n_points + 1):
        winkel = i * 360 / n_points
        winkel_rad = np.radians(winkel)

        dx = (radius_meter * np.cos(winkel_rad)) / (111320 * np.cos(np.radians(zentrum_latitude)))
        dy = (radius_meter * np.sin(winkel_rad)) / 110540

        lon = zentrum_longitude + dx
        lat = zentrum_latitude + dy

        kreis_punkte.append((lon, lat))

    kreis = kml.newpolygon(name=f"{faktor}σ-Zone")
    kreis.outerboundaryis = kreis_punkte
    kreis.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.red)
    kreis.style.linestyle.color = simplekml.Color.red
    kreis.style.linestyle.width = 2

kml.save("risikokarte_zentrum.kml")
print("🌍 KML-Datei gespeichert: risikokarte_zentrum.kml")
