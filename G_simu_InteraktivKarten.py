import pandas as pd
import folium
from branca.element import Template, MacroElement
import webbrowser
from scipy.spatial import ConvexHull
import simplekml
import numpy as np
import time
import tkinter as tk
from tkinter import ttk
from math import radians, cos, sin, asin, sqrt

# Fortschrittsbalken-Funktion
def show_progress(status):
    progress_label.config(text=status)
    root.update()

# Fenster für Fortschrittsanzeige
root = tk.Tk()
root.title("Status: Aufprallkartenerstellung")
progress_label = ttk.Label(root, text="Starte...")
progress_label.pack(padx=20, pady=20)

#--------------------------
# Zentrum der Flugbahn
#--------------------------
zentrum_longitude = -13.893774438364316
zentrum_latitude = 28.518039819774355

show_progress("Lade Aufpralldateien...")

#--------------------------
# Dateien einlesen
#--------------------------
dateien = {
    "Antriebausfall": "aufprallpunkte_Antriebausfall.csv",
    "Strukturbruch": "aufprallpunkte_Strukturbruch.csv",
    "Steuerverlust": "aufprallpunkte_Steuerverlust.csv",
    "Fluegelabriss": "aufprallpunkte_Fluegelabriss.csv",
    "Flat Spin": "aufprallpunkte_Flat Spin.csv",
    "Solarmodul": "aufprallpunkte_Solarmodul.csv",
    "Motorblock": "aufprallpunkte_Motorblock.csv"
}

farben = {
    "Antriebausfall": "blue",
    "Strukturbruch": "green",
    "Steuerverlust": "yellow",
    "Fluegelabriss": "orange",
    "Flat Spin": "violet",
    "Solarmodul": "brown",
    "Motorblock": "aqua"
}

#--------------------------
# Interaktive Karte initialisieren
#--------------------------
show_progress("Erstelle Karte...")

m = folium.Map(location=[zentrum_latitude, zentrum_longitude], zoom_start=13)

# Zentrum markieren (schönes Icon: Stern)
folium.Marker(
    location=[zentrum_latitude, zentrum_longitude],
    popup="Zentrum der Flugbahn",
    icon=folium.Icon(color="red", icon="star")
).add_to(m)

#--------------------------
# Aufprallpunkte aus allen Dateien hinzufügen
#--------------------------
show_progress("Füge Aufprallpunkte hinzu...")

all_points = []
for name, path in dateien.items():
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["Latitude Aufprall"], row["Longitude Aufprall"]],
            radius=5,  # etwas größere Marker für bessere Sichtbarkeit
            color=farben[name],
            fill=True,
            fill_opacity=0.7,
            popup=name
        ).add_to(m)
        all_points.append((row["Longitude Aufprall"], row["Latitude Aufprall"]))

#--------------------------
# Karte Legende
#--------------------------
show_progress("Erstelle Legende...")

legend_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 180px; height: 180px; 
    z-index:9999; font-size:14px;
    background-color: white;
    padding: 10px;
    border:2px solid grey;
    border-radius:5px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
">
<b>Legende:</b><br>
<span style="color:blue">●</span> Antriebausfall<br>
<span style="color:green">●</span> Strukturbruch<br>
<span style="color:yellow">●</span> Steuerverlust<br>
<span style="color:orange">●</span> Fluegelabriss<br>
<span style="color:violet">●</span> Flat Spin<br>
<span style="color:brown">●</span> Solarmodul<br>
<span style="color:aqua">●</span> Motorblock<br>
</div>
{% endmacro %}
"""
legend = MacroElement()
legend._template = Template(legend_html)
m.get_root().add_child(legend)

#--------------------------
# Karte speichern
#--------------------------
show_progress("Speichere Karte...")

karte_pfad = "gesamtkarte_aufprallpunkte.html"
m.save(karte_pfad)

#--------------------------
# KML-Datei mit konvexer Aufprallzone erzeugen
#--------------------------
show_progress("Berechne konvexe Hülle...")

if all_points:
    points_array = np.array(all_points)
    hull = ConvexHull(points_array)
    hull_points = points_array[hull.vertices]
    hull_coords = [(lon, lat) for lon, lat in hull_points]
    hull_coords.append(hull_coords[0])  # Polygon schließen

    kml = simplekml.Kml()
    pol = kml.newpolygon(name="Aufprallzone", outerboundaryis=hull_coords)
    pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.red)
    pol.style.linestyle.width = 2
    pol.style.linestyle.color = simplekml.Color.red

    kml_path = "aufprallzone_konvex.kml"
    kml.save(kml_path)

    show_progress("Starte Google Earth Web...")
    webbrowser.open("https://earth.google.com/web/")

#--------------------------
# Abschluss
#--------------------------
show_progress("✅ Fertig! Öffne Karte...")
time.sleep(1)
webbrowser.open(karte_pfad)

root.destroy()

print("✅ Die Karte wurde gespeichert und geöffnet. Google Earth wurde ebenfalls gestartet.")




# Funktion zur Berechnung der Entfernung (Haversine)
def haversine(lon1, lat1, lon2, lat2):
    R = 6371000  # Radius der Erde in Metern
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# Zentrum der Flugbahn
zentrum_longitude = -13.893774438364316
zentrum_latitude = 28.518039819774355

# Alle CSV-Dateien einlesen
dateien = [
    "aufprallpunkte_Antriebausfall.csv",
    "aufprallpunkte_Strukturbruch.csv",
    "aufprallpunkte_Steuerverlust.csv",
    "aufprallpunkte_Fluegelabriss.csv",
    "aufprallpunkte_Flat Spin.csv",
    "aufprallpunkte_Solarmodul.csv",
    "aufprallpunkte_Motorblock.csv"
]

# Alle Punkte sammeln
all_points = []
for path in dateien:
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        all_points.append((row["Longitude Aufprall"], row["Latitude Aufprall"]))

# Entfernungen berechnen
distances = [haversine(zentrum_longitude, zentrum_latitude, lon, lat) for lon, lat in all_points]

# Maximale Entfernung finden
max_distance = max(distances)  # in Metern
print(f"Maximaler Abstand zum Zentrum: {round(max_distance/1000, 2)} km")

# Kreis um das Zentrum mit diesem Radius zeichnen
kml = simplekml.Kml()
kreis = kml.newpolygon(name="Maximaler Kreis")

# Viele Punkte erzeugen (damit der Kreis rund aussieht)
num_points = 100
kreis_coords = []
for i in range(num_points):
    angle = 2 * np.pi * i / num_points
    dx = (max_distance / 6371000) * cos(angle)
    dy = (max_distance / 6371000) * sin(angle)
    lat = zentrum_latitude + (dy * 180/np.pi)
    lon = zentrum_longitude + (dx * 180/np.pi) / cos(radians(zentrum_latitude))
    kreis_coords.append((lon, lat))
kreis_coords.append(kreis_coords[0])  # Kreis schließen

kreis.outerboundaryis = kreis_coords
kreis.style.polystyle.color = simplekml.Color.changealphaint(80, simplekml.Color.blue)
kreis.style.linestyle.width = 2
kreis.style.linestyle.color = simplekml.Color.blue

# Speichern und starten
kml_path = "kreis_maximale_reichweite.kml"
kml.save(kml_path)

import webbrowser
webbrowser.open("https://earth.google.com/web/")

print("✅ Kreis wurde erzeugt und Google Earth wurde geöffnet.")

