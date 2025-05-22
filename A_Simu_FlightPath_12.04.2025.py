# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 13:00:28 2025

@author: david
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import folium
import webbrowser
from math import pi, radians, cos, sin, asin, sqrt
import simplekml  # <- neu installieren: pip install simplekml

# Eingabedatei definieren
excel_file = 'daten.xlsm'

# Alle Tabellenblätter anzeigen (optional)
all_sheets = pd.read_excel(excel_file, sheet_name=None)

# Einlesen des relevanten Tabellenblatts
sheet = 'Simu.Daten'
df = pd.read_excel(excel_file, sheet_name=sheet)

# Spalten extrahieren
longitude = df['longitude']
latitude = df['latitude']
altitude = df['altitude']
time = df['time']
# Kreisbahnparameter
#center coords
min_lon, max_lon = longitude.min(), longitude.max()
min_lat, max_lat = latitude.min(), latitude.max()
delta_lon = max_lon - min_lon
delta_lat = max_lat - min_lat

center_lon = longitude.mean()
center_lat = latitude.mean()
# Umfang und radios in "m"
def haversine(lon1, lat1, lon2, lat2):
    R = 6371000
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

radii = [haversine(lon, lat, center_lon, center_lat) for lon, lat in zip(longitude, latitude)]
mean_radius = sum(radii) / len(radii)
umfang = 2 * pi * mean_radius

print("Mittlerer Radius der Kreisbahn:", round(mean_radius, 2), "Meter")
print("Umfang der Kreisbahn:", round(umfang, 2), "Meter")
print("Zentrum der Kreisbahn:")
print("Longitude:", center_lon)
print("Latitude:", center_lat)

# Ursprünglicher 3D-Plot
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.plot(longitude, latitude, altitude, color='blue', label='Original-Flugbahn')
ax.set_xlabel("longitude")
ax.set_ylabel("latitude")
ax.set_zlabel("altitude")
ax.set_title("3D-Flugbahn aus Excel-Daten")
plt.legend()
plt.show()

# 2D-Plot
plt.figure(figsize=(10, 10))
plt.plot(longitude, latitude, marker='o', linestyle='-', color='blue', label='Flugbahn')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("2D-Flugbahn (Projektion)")
plt.grid(True)
plt.legend()
plt.show()

# Höhenprofil über Zeit
time_hours = time / 3600  # Sekunden in Stunden umrechnen

plt.figure(figsize=(10, 10))
plt.plot(time_hours, altitude, marker='o', linestyle='-', color='green', label='Höhenprofil')
plt.xlabel("Time [h]")  # Einheit anpassen
plt.ylabel("Altitude")
plt.title("Flight Profile (Altitude vs. Time)")
plt.grid(True)
plt.legend()
plt.show()




# -------------------------------------------------
# Neue Funktion: Vereinfachte/gefilterte Flugbahn (flexibel)
# -------------------------------------------------
def create_filtered_flightpath(df, height_step=200, points_per_level=8):
    df['height_level'] = (df['altitude'] // height_step).astype(int)

    rep_points_list = []
    for _, group in df.groupby('height_level'):
        if len(group) >= points_per_level:
            step = len(group) // points_per_level
            reps = group.iloc[::step].head(points_per_level)
        else:
            reps = group
        rep_points_list.append(reps)

    rep_points = pd.concat(rep_points_list).reset_index(drop=True)

    # 3D-Plot nur mit Punkten
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(df['longitude'], df['latitude'], df['altitude'], linestyle='-', color='lightgray', label='Original')
    ax.scatter(rep_points['longitude'], rep_points['latitude'], rep_points['altitude'], color='red', s=20, label='Gefiltert')
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_zlabel("Altitude")
    ax.set_title(f"Reduzierte 3D-Flugbahn ({points_per_level} Punkt(e) pro {height_step} m Höhe)")
    ax.legend()
    plt.tight_layout()
    plt.show()

    output_path = os.path.join(os.getcwd(), f"flugbahn_{height_step}m_{points_per_level}pts.xlsx")
    rep_points.to_excel(output_path, index=False)
    print(f"\n✅ Reduzierte Flugbahn gespeichert unter:\n{output_path}")

    return rep_points

# Beispielaufruf mit benutzerdefinierten Werten
height_step_input = 200  # z. B. 200 m
points_per_level_input = 8  # z. B. 4 Punkte pro Höhenintervall
filtered = create_filtered_flightpath(df, height_step=height_step_input, points_per_level=points_per_level_input)



# -------------------------------------------------
# 4. Interaktive Karte mit beiden Linien (Folium)
# -------------------------------------------------

# Mittelpunkt berechnen
lat_center = (df["latitude"].mean() + filtered["latitude"].mean()) / 2
lon_center = (df["longitude"].mean() + filtered["longitude"].mean()) / 2

# Karte erzeugen
karte = folium.Map(location=[lat_center, lon_center], zoom_start=13)

# 🔵 Originalflugbahn (hellblau)
pfad_original = list(zip(df["latitude"], df["longitude"]))
folium.PolyLine(
    pfad_original,
    color="blue",
    weight=2,
    opacity=1,
    tooltip="Originalflugbahn"
).add_to(karte)

# 🔴 Reduzierte Flugbahn (rot)
if "time" in filtered.columns:
    filtered_sorted = filtered.sort_values(by="time")
elif "height_level" in filtered.columns:
    filtered_sorted = filtered.sort_values(by=["height_level", "index"])
else:
    filtered_sorted = filtered.sort_values(by=filtered.columns[0])  # Fallback

pfad_reduziert = list(zip(filtered_sorted["latitude"], filtered_sorted["longitude"]))
folium.PolyLine(
    pfad_reduziert,
    color="red",
    weight=1,
    opacity=0.5,
    tooltip="Reduzierte Flugbahn"
).add_to(karte)

# Lokale Folium-Karte speichern und anzeigen
karte.save("flugbahn_nur_linien.html")
webbrowser.open('file://' + os.path.realpath("flugbahn_nur_linien.html"))
print("🗺️ Folium-Karte mit Original- und reduzierter Flugbahn geöffnet: flugbahn_nur_linien.html")

# -------------------------------------------------
# 5. Google Earth / Google Maps: KML Datei erzeugen
# -------------------------------------------------

# 5. Google Earth / Google Maps: KML Datei erzeugen
kml = simplekml.Kml()

# Originalflugbahn als blaue Linie
linien_original = [(lon, lat) for lat, lon in pfad_original]
line1 = kml.newlinestring(name="Originalflugbahn", coords=linien_original, description="Originalflugbahn")
line1.style.linestyle.color = simplekml.Color.blue
line1.style.linestyle.width = 2  # optional

# Reduzierte Flugbahn als rote Linie
linien_reduziert = [(lon, lat) for lat, lon in pfad_reduziert]
line2 = kml.newlinestring(name="Reduzierte Flugbahn", coords=linien_reduziert, description="Reduzierte Flugbahn")
line2.style.linestyle.color = simplekml.Color.red
line2.style.linestyle.width = 2  # optional

# KML-Datei speichern
kml_path = "flugbahn.kml"
kml.save(kml_path)

print("🌍 Google Earth/Maps KML-Datei erzeugt:", kml_path)

# Optional: automatisch im Browser öffnen
#webbrowser.open('file://' + os.path.realpath(kml_path))



