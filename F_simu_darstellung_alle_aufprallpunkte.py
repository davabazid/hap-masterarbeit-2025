import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import tkinter as tk
from tkinter import ttk
import folium
from simplekml import Kml
import webbrowser
import os
import subprocess
import platform
import math

# --------------------
# Dropdown-Funktion
# --------------------
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

# --------------------
# Hauptcode
# --------------------
zentrum_longitude = -13.893774438364316
zentrum_latitude = 28.518039819774355

csv_datei = waehle_szenario()

if csv_datei is not None:
    # CSV laden
    df = pd.read_csv(csv_datei)

    # Abstand zum Zentrum berechnen
    df["Abstand_zum_Zentrum"] = np.sqrt(
        (df["Longitude Aufprall"] - zentrum_longitude)**2 +
        (df["Latitude Aufprall"] - zentrum_latitude)**2
    )

    # Scatterplot mit allen Daten
    plt.figure(figsize=(10, 8))
    plt.scatter(df["Longitude Aufprall"], df["Latitude Aufprall"], c="darkgreen", s=10, alpha=0.7)
    plt.scatter(zentrum_longitude, zentrum_latitude, c="red", marker="x", s=100, label="Zentrum der Flugbahn")
    plt.xlabel("Längengrad")
    plt.ylabel("Breitengrad")
    plt.title(f"Aufprallpunkte ({csv_datei}) mit Zentrum der Flugbahn")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Histogramm des Abstands zum Zentrum
    x = df["Abstand_zum_Zentrum"].dropna()
    mu = x.mean()
    std = x.std()
    plt.figure(figsize=(10, 6))
    plt.hist(x, bins=20, density=True, alpha=0.6, color="lightcoral", edgecolor='black', label='Abstandsverteilung')
    x_range = np.linspace(x.min(), x.max(), 100)
    pdf = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_range - mu) / std) ** 2)
    plt.plot(x_range, pdf, 'r--', linewidth=2, label=f'Gauß-Fit\nμ={mu:.4f}, σ={std:.4f}')
    plt.axvline(mu, color='green', linestyle='-', linewidth=2, label='Mittelwert μ')
    plt.axvline(mu - std, color='orange', linestyle='--', linewidth=1.5, label='μ - σ')
    plt.axvline(mu + std, color='orange', linestyle='--', linewidth=1.5, label='μ + σ')
    plt.title("Abstand zum Zentrum: Histogramm mit Gauß-Funktion")
    plt.xlabel("Abstand (Grad)")
    plt.ylabel("Dichte")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("hist_abstand_zum_zentrum_mit_mu_sigma.png")
    plt.show()

    # Shapiro-Wilk-Test auf Abstand zur Kreisbahn
    shapiro_dist = stats.shapiro(df["Abstand_zum_Zentrum"].dropna())
    print("Shapiro-Wilk-Test für Abstand zum Zentrum:", shapiro_dist)

    if shapiro_dist.pvalue > 0.05:
        print("Abstand zum Zentrum ist normalverteilt (p > 0,05)")
    else:
        print("Abstand zum Zentrum ist NICHT normalverteilt (p <= 0,05)")

    # --------------------
    # Interaktive Folium-Karte
    # --------------------
    karte = folium.Map(location=[zentrum_latitude, zentrum_longitude], zoom_start=13)

    # Zentrum markieren
    folium.Marker(
        [zentrum_latitude, zentrum_longitude],
        popup="Zentrum der Flugbahn",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(karte)

    # Aufprallpunkte einfügen
    for idx, row in df.iterrows():
        folium.CircleMarker(
            location=[row["Latitude Aufprall"], row["Longitude Aufprall"]],
            radius=3,
            color="darkgreen",
            fill=True,
            fill_color="green",
            fill_opacity=0.7
        ).add_to(karte)

    # --------------------
    # Sigma-Zonen basierend auf Aufprallpunkten hinzufügen
    # --------------------
    sigma_grad = df["Abstand_zum_Zentrum"].std()
    print(f"Standardabweichung σ = {sigma_grad:.6f} Grad")

    def grad_to_meter(grad):
        return grad * 111000

    def kreis_label_position(lat, lon, radius_m, richtung=45):
        richtung_rad = math.radians(richtung)
        lat_neu = lat + (radius_m/111000) * math.cos(richtung_rad)
        lon_neu = lon + (radius_m/111000) * math.sin(richtung_rad) / math.cos(math.radians(lat))
        return lat_neu, lon_neu

    sigma_zonen = [
        {"multiplikator": 1, "farbe": "green", "label": "1σ Zone (68%)"},
        {"multiplikator": 2, "farbe": "orange", "label": "2σ Zone (95%)"},
        {"multiplikator": 3, "farbe": "red", "label": "3σ Zone (99,7%)"},
    ]

    for zone in sigma_zonen:
        radius_meter = grad_to_meter(sigma_grad * zone["multiplikator"])
        folium.Circle(
            location=[zentrum_latitude, zentrum_longitude],
            radius=radius_meter,
            color=zone["farbe"],
            fill=False
        ).add_to(karte)
        label_lat, label_lon = kreis_label_position(zentrum_latitude, zentrum_longitude, radius_meter)
        folium.map.Marker(
            [label_lat, label_lon],
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 12px; color: {zone['farbe']};"><b>{zone['label']}</b></div>"""
            )
        ).add_to(karte)

    # Karte speichern
    karte.save("karte_sigma_zonen.html")
    print("Interaktive Karte wurde als 'karte_sigma_zonen.html' gespeichert.")

    # Karte im Browser öffnen
    karte_datei = os.path.abspath("karte_sigma_zonen.html")
    webbrowser.open(f"file://{karte_datei}", new=2)

    # --------------------
    # KML-Datei erstellen
    # --------------------
    kml = Kml()
    kml.newpoint(name="Zentrum", coords=[(zentrum_longitude, zentrum_latitude)])
    for idx, row in df.iterrows():
        kml.newpoint(name="", coords=[(row["Longitude Aufprall"], row["Latitude Aufprall"])])
    
    # 🛠️ Neuen Dateinamen basierend auf dem Szenario erzeugen:
    szenarioname_ohne_endung = os.path.splitext(csv_datei)[0]  # Entfernt .csv
    kml_dateiname = f"{szenarioname_ohne_endung}.kml"
    
    kml.save(kml_dateiname)
    print(f"KML-Datei wurde als '{kml_dateiname}' gespeichert.")

else:
    print("Kein Szenario ausgewählt. Programm wird beendet.")

# --------------------
# Winddaten aus Radiosonde laden und analysieren
# --------------------
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
    np.zeros(len(wind_df)),
    wind_df["HGHT"],
    np.cos(np.deg2rad(wind_df["DRCT"])) * wind_df["SPED"],
    np.sin(np.deg2rad(wind_df["DRCT"])) * wind_df["SPED"],
    angles='xy', scale_units='xy', scale=1, color='teal', alpha=0.7
)
plt.xlabel("")
plt.ylabel("Höhe (m)")
plt.title("Windprofil – Richtung und Geschwindigkeit mit Höhe")
plt.grid(True)
plt.tight_layout()
plt.savefig("windprofil_hoehe.png")
plt.show()
