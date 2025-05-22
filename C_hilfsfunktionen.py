# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 13:39:27 2025

@author: david
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Zusätzliche Flugphasenfunktionen ---
def get_flight_phase(z, vz): 
    z_high = 20000.0
    vz_schwelle = 0.5
    if z >= z_high and abs(vz) <= vz_schwelle:
        return 'cruise'
    elif vz >= 0:
        return 'climb'
    else:
        return 'descent'

def get_start_speed(phase, z):
    z_low = 0.0
    z_high = 20000.0

    if phase == 'cruise':
        return 25.2
    elif phase == 'climb':
        # Geschwindigkeit linear von 7.8 auf 25.2 steigen zwischen 0 und 20.000 m
        return 7.8 + (25.2 - 7.8) * (z - z_low) / (z_high - z_low)
    elif phase == 'descent':
        # Geschwindigkeit linear von 25.2 auf 7.8 sinken zwischen 20.000 m und 0
        return 25.2 - (25.2 - 7.8) * (z_low + (z_high - z)) / (z_high - z_low)
    else:
        return 0.0

def lade_radiosondendaten(dateiname):
    df = pd.read_excel(dateiname)
    return df, df.columns

def lade_flugpfad(dateiname):
    return pd.read_excel(dateiname)

def berechne_windgeschwindigkeit_bei_hoehe(hoehe, radiosondendaten, max_toleranz=1000, schritt=100):
    for toleranz in range(schritt, max_toleranz + schritt, schritt):
        bereich = radiosondendaten[
            (radiosondendaten["HGHT"] >= hoehe - toleranz) &
            (radiosondendaten["HGHT"] <= hoehe + toleranz)
        ]
        if not bereich.empty:
            geschwindigkeit = np.interp(hoehe, bereich["HGHT"], bereich["SPED"])
            richtung_grad = np.interp(hoehe, bereich["HGHT"], bereich["DRCT"])
            richtung_bogen = np.deg2rad((richtung_grad + 180) % 360)
            wind_x = geschwindigkeit * np.cos(richtung_bogen)
            wind_y = geschwindigkeit * np.sin(richtung_bogen)
            return wind_x, wind_y
    return 0.0, 0.0

def berechne_luftdichte_bei_hoehe(hoehe, radiosondendaten):
    if "RELH" in radiosondendaten and "TEMP" in radiosondendaten:
        temp = np.interp(hoehe, radiosondendaten["HGHT"], radiosondendaten["TEMP"])
        T = temp + 273.15
        p0 = 101325
        R = 287.05
        h_scale = 8500
        p = p0 * np.exp(-hoehe / h_scale)
        rho = p / (R * T)
        return rho
    else:
        return 1.225



def berechne_differenz_m(lon1, lat1, lon2, lat2): # GEO in metrisch
    R = 6371000
    dlat = np.deg2rad(lat2 - lat1)
    dlon = np.deg2rad(lon2 - lon1)
    lat1 = np.deg2rad(lat1)
    lat2 = np.deg2rad(lat2)
    dx = R * dlon * np.cos((lat1 + lat2) / 2)
    dy = R * dlat
    return dx, dy

def verschiebung_zu_geokoordinaten(x, y, lon0, lat0): # metrisch in GEO zurück
    R = 6371000
    dlat = (y / R) * (180 / np.pi)
    dlon = (x / (R * np.cos(np.deg2rad(lat0)))) * (180 / np.pi)
    return lat0 + dlat, lon0 + dlon

def generiere_truemmer_szenario(szenarienname=None):
    szenarien = {
        "Antriebausfall": {"masse": [134], "cw_wert": [1.3], "cl_wert": [0.8], "flaeche": [30]},
        "Strukturbruch": {"masse": [80, 54], "cw_wert": [1.1, 1.4], "cl_wert": [0.3, 0.2], "flaeche": [1.2, 0.9]},
        "Steuerverlust": {"masse": [134], "cw_wert": [1.2], "cl_wert": [0.7], "flaeche": [30]},
        "Fluegelabriss": {"masse": [40, 10], "cw_wert": [1.6, 1.8], "cl_wert": [0.1, 0.05], "flaeche": [0.9, 0.3]},
        "Flat Spin": {"masse": [134], "cw_wert": [2.0], "cl_wert": [0.0], "flaeche": [2]},
        "Solarmodul": {"masse": [3], "cw_wert": [1.7], "cl_wert": [0.0], "flaeche": [0.5]},
        "Motorblock": {"masse": [15], "cw_wert": [1.1], "cl_wert": [0.0], "flaeche": [0.15]}
    }

    szenario = szenarien[szenarienname]

    # Bestes (gefährlichstes) Teil auswählen
    max_index = np.argmax([
        m * cw * a for m, cw, a in zip(szenario["masse"], szenario["cw_wert"], szenario["flaeche"])
    ])

    return {
        "masse": [szenario["masse"][max_index]],
        "cw_wert": [szenario["cw_wert"][max_index]],
        "cl_wert": [szenario["cl_wert"][max_index]],
        "flaeche": [szenario["flaeche"][max_index]]
    }



def erstelle_zeitverlauf_plot(df, masse, cw, cl, flaeche, v_terminal, szenarioname):
    zeit = df["Zeit [s]"]
    fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

    # Geschwindigkeit
    axs[0].plot(zeit, df["VX [m/s]"], label="VX", color="blue")
    axs[0].plot(zeit, df["VY [m/s]"], label="VY", color="green")
    axs[0].plot(zeit, df["VZ [m/s]"], label="VZ", color="red")
    axs[0].axhline(-v_terminal, color="red", linestyle="--", linewidth=1.0, label="v_terminal")
    axs[0].set_ylabel("Geschwindigkeit [m/s]")
    axs[0].legend(loc="upper right")
    axs[0].grid()

    # Beschleunigung
    axs[1].plot(zeit, df["AX [m/s²]"], label="AX", color="blue")
    axs[1].plot(zeit, df["AY [m/s²]"], label="AY", color="green")
    axs[1].plot(zeit, df["AZ [m/s²]"], label="AZ", color="red")
    axs[1].set_ylabel("Beschleunigung [m/s²]")
    axs[1].legend(loc="upper right")
    axs[1].grid()

    # Höhe
    axs[2].plot(zeit, df["Z [m]"], label="Höhe", color="black")
    axs[2].set_xlabel("Zeit [s]")
    axs[2].set_ylabel("Höhe [m]")
    axs[2].legend(loc="upper right")
    axs[2].grid()

    # Titel und Parameter-Box
    fig.suptitle(f"Flugverlauf – {szenarioname}", fontsize=14)

    param_text = (
        f"Masse: {masse} kg\n"
        f"Cd: {cw}, Cl: {cl}\n"
        f"Fläche: {flaeche} m²\n"
        f"v_terminal: {v_terminal:.2f} m/s"
    )

    fig.text(0.98, 0.02, param_text, ha='right', va='bottom',
             bbox=dict(facecolor='white', edgecolor='black'), fontsize=9)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f"zeitverlauf_{szenarioname.replace(' ', '_')}.png")
    plt.show()



def erstelle_radiosonden_plots(df):
    fig, ax = plt.subplots(3, 1, figsize=(7, 10), sharex=False)

    ax[0].plot(df["SPED"], df["HGHT"], color='orange')
    ax[0].set_title("Windgeschwindigkeit")
    ax[0].set_xlabel("[m/s]")
    ax[0].set_ylabel("Höhe [m]")
    ax[0].grid()

    ax[1].plot(df["DRCT"], df["HGHT"], color='blue')
    ax[1].set_title("Windrichtung")
    ax[1].set_xlabel("[°]")
    ax[1].set_ylabel("Höhe [m]")
    ax[1].grid()

    rho = 101325 * np.exp(-df["HGHT"] / 8500) / (287.05 * (df["TEMP"] + 273.15))
    ax[2].plot(rho, df["HGHT"], color='green')
    ax[2].set_title("Luftdichte (angenähert)")
    ax[2].set_xlabel("[kg/m³]")
    ax[2].set_ylabel("Höhe [m]")
    ax[2].grid()

    plt.tight_layout()
    plt.savefig("radiosonden_verlauf.png")
    plt.show()

def erstelle_gesamtplot(daten, radiosondendaten):
    fig, axs = plt.subplots(4, 1, figsize=(10, 14), sharex=False)

    axs[0].plot(daten["Zeit [s]"], daten["Z [m]"], color="blue")
    axs[0].set_ylabel("Höhe [m]")
    axs[0].set_title("Höhenprofil")
    axs[0].grid()

    axs[1].plot(daten["Zeit [s]"], daten["VX [m/s]"], label="VX", color="blue")
    axs[1].plot(daten["Zeit [s]"], daten["VY [m/s]"], label="VY", color="green")
    axs[1].plot(daten["Zeit [s]"], daten["VZ [m/s]"], label="VZ", color="red")
    axs[1].set_ylabel("Geschwindigkeit [m/s]")
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(daten["Zeit [s]"], daten["AX [m/s²]"], label="AX", color="blue")
    axs[2].plot(daten["Zeit [s]"], daten["AY [m/s²]"], label="AY", color="green")
    axs[2].plot(daten["Zeit [s]"], daten["AZ [m/s²]"], label="AZ", color="red")
    axs[2].set_ylabel("Beschleunigung [m/s²]")
    axs[2].legend()
    axs[2].grid()

    rho = 101325 * np.exp(-radiosondendaten["HGHT"] / 8500) / (287.05 * (radiosondendaten["TEMP"] + 273.15))
    axs[3].plot(rho, radiosondendaten["HGHT"], color='purple', label="Luftdichte")
    axs[3].set_ylabel("Höhe [m]")
    axs[3].set_xlabel("ρ [kg/m³]")
    axs[3].set_title("Luftdichteprofil")
    axs[3].grid()
    axs[3].legend()

    plt.tight_layout()
    plt.savefig("gesamtplot.png")
    plt.show()

def berechne_auftriebsbeiwert(rho, v, CL, flaeche, masse):
    F_auftrieb = 0.5 * rho * v**2 * CL * flaeche
    return F_auftrieb / masse

def simuliere_fall(masse, cw, cl, flaeche, radiosonde, x, y, z, vx, vy, vz, lon0, lat0, zeitschritt=0.01, start_hoehe=None):

    if start_hoehe is not None:
        index = np.argmin(np.abs(z - start_hoehe))
    else:
        index = 0 # erste Punkt in der liste

    z0 = z[index]
    phase = get_flight_phase(z0, vz[index])
    start_v = get_start_speed(phase, z0)
    zustand = np.array([x[index], y[index], z[index], start_v, 0.0, vz[index]])

    zeit = 0.0
    lz, lx, ly, lz_h = [], [], [], []
    lvx, lvy, lvz = [], [], []
    lax, lay, laz = [], [], []

    while zustand[2] > 0:
        x_, y_, z_, vx_, vy_, vz_ = zustand
        lz.append(zeit)
        lx.append(x_)
        ly.append(y_)
        lz_h.append(z_)
        lvx.append(vx_)
        lvy.append(vy_)
        lvz.append(vz_)

        wind_x, wind_y = berechne_windgeschwindigkeit_bei_hoehe(z_, radiosonde)
        v_rel_x = vx_ - wind_x
        v_rel_y = vy_ - wind_y
        v_rel_z = vz_
        v_rel = np.sqrt(v_rel_x**2 + v_rel_y**2 + v_rel_z**2)

        rho = berechne_luftdichte_bei_hoehe(z_, radiosonde)
        faktor = 0.5 * rho * cw * flaeche / masse

        a_x = -faktor * v_rel * v_rel_x
        a_y = -faktor * v_rel * v_rel_y
        a_z = -faktor * v_rel * v_rel_z + berechne_auftriebsbeiwert(rho, abs(v_rel_z), cl, flaeche, masse) - 9.81


        lax.append(a_x)
        lay.append(a_y)
        laz.append(a_z)

        vx_ += a_x * zeitschritt
        vy_ += a_y * zeitschritt
        vz_ += a_z * zeitschritt
        x_ += vx_ * zeitschritt
        y_ += vy_ * zeitschritt
        z_ = max(0, z_ + vz_ * zeitschritt)

        zustand = np.array([x_, y_, z_, vx_, vy_, vz_])
        zeit += zeitschritt

    lat, lon = verschiebung_zu_geokoordinaten(zustand[0], zustand[1], lon0, lat0)

    df = pd.DataFrame({
        "Zeit [s]": lz,
        "X [m]": lx,
        "Y [m]": ly,
        "Z [m]": lz_h,
        "VX [m/s]": lvx,
        "VY [m/s]": lvy,
        "VZ [m/s]": lvz,
        "AX [m/s²]": lax,
        "AY [m/s²]": lay,
        "AZ [m/s²]": laz
    })

    return np.array(lz), df, lat, lon
