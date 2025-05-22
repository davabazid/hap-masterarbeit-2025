import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# ------------------------------
# 1. Daten laden
# ------------------------------
datei = "radiosonde_data_60018_2025-04-18.xlsx"
df = pd.read_excel(datei)

# ------------------------------
# 2. Nur relevante Spalten extrahieren
# ------------------------------
df_wind = df[['DRCT', 'SPED', 'HGHT']].dropna()

# ------------------------------
# 3. Windgeschwindigkeit vs. Höhe
# ------------------------------
plt.figure(figsize=(8, 6))
plt.plot(df_wind['SPED'], df_wind['HGHT'], color='orange')
plt.xlabel("Windgeschwindigkeit [m/s]")
plt.ylabel("Höhe [m]")
plt.title("Windgeschwindigkeit")
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------
# 4. Windrichtung vs. Höhe
# ------------------------------
plt.figure(figsize=(8, 6))
plt.plot(df_wind['DRCT'], df_wind['HGHT'], color='blue')
plt.xlabel("Windrichtung [°]")
plt.ylabel("Höhe [m]")
plt.title("Windrichtung")
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------
# 5. Scatterplot: Windrichtung vs. Windgeschwindigkeit
# ------------------------------
plt.figure(figsize=(10, 6))
plt.scatter(df_wind['DRCT'], df_wind['SPED'], c='teal', alpha=0.6)
plt.xlabel("Windrichtung (°)")
plt.ylabel("Windgeschwindigkeit (m/s)")
plt.title("Scatterplot: Windrichtung vs. Windgeschwindigkeit")
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------
# 6. Histogramme
# ------------------------------
# 6.1 Histogramm Windrichtung
plt.figure(figsize=(8, 5))
plt.hist(df_wind['DRCT'], bins=36, range=(0, 360), color='skyblue', edgecolor='black')
plt.xlabel("Windrichtung (°)")
plt.ylabel("Anzahl")
plt.title("Histogramm der Windrichtung")
plt.grid(True)
plt.tight_layout()
plt.show()

# 6.2 Histogramm Windgeschwindigkeit
plt.figure(figsize=(8, 5))
plt.hist(df_wind['SPED'], bins=20, color='lightgreen', edgecolor='black')
plt.xlabel("Windgeschwindigkeit (m/s)")
plt.ylabel("Anzahl")
plt.title("Histogramm der Windgeschwindigkeit")
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------
# 7. Windrose: Barplot Darstellung
# ------------------------------
df_wind['DRCT_rounded'] = (df_wind['DRCT'] / 10).round() * 10 % 360
wind_counts = df_wind.groupby('DRCT_rounded')['SPED'].mean()

theta = np.deg2rad(wind_counts.index)
r = wind_counts.values

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
bars = ax.bar(theta, r, width=np.deg2rad(10), bottom=0.0,
              color=cm.viridis(r / np.max(r)), edgecolor='black')
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_rlabel_position(225)
ax.set_title("Windrose: Mittelwert der Windgeschwindigkeit", va='bottom')

plt.tight_layout()
plt.show()

# ------------------------------
# 8. Windprofil – Richtung und Geschwindigkeit mit Höhe
# ------------------------------
plt.figure(figsize=(10, 6))
plt.quiver(
    np.zeros(len(df_wind)),
    df_wind["HGHT"],
    np.cos(np.deg2rad(df_wind["DRCT"])) * df_wind["SPED"],
    np.sin(np.deg2rad(df_wind["DRCT"])) * df_wind["SPED"],
    angles='xy', scale_units='xy', scale=1, color='teal', alpha=0.7
)
plt.ylabel("Höhe (m)")
plt.title("Windprofil – Richtung und Geschwindigkeit mit Höhe")
plt.grid(True)
plt.tight_layout()
plt.savefig("windprofil_hoehe.png")
plt.show()

# ------------------------------
# 9. Temperaturprofil
# ------------------------------
df_phys = df[['HGHT', 'TEMP', 'PRES']].dropna()
plt.figure(figsize=(8, 6))
plt.plot(df_phys['TEMP'], df_phys['HGHT'], color='red')
plt.xlabel("Temperatur [°C]")
plt.ylabel("Höhe [m]")
plt.title("Temperaturprofil")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot_temperaturprofil.png")
plt.show()

# ------------------------------
# 10. Druckprofil
# ------------------------------
plt.figure(figsize=(8, 6))
plt.plot(df_phys['PRES'], df_phys['HGHT'], color='darkgreen')
plt.xlabel("Druck [hPa]")
plt.ylabel("Höhe [m]")
plt.title("Druckprofil")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot_druckprofil.png")
plt.show()

# ------------------------------
# 11. Dichteprofil
# ------------------------------
R_s = 287.05  # J/(kg·K)
temperature_K = df_phys['TEMP'] + 273.15
density = (df_phys['PRES'] * 100) / (R_s * temperature_K)  # hPa → Pa

plt.figure(figsize=(8, 6))
plt.plot(density, df_phys['HGHT'], color='purple')
plt.xlabel("Luftdichte [kg/m³]")
plt.ylabel("Höhe [m]")
plt.title("Dichteprofil")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot_dichteprofil.png")
plt.show()
