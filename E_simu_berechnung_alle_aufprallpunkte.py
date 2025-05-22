import pandas as pd
import numpy as np
from C_hilfsfunktionen import simuliere_fall
from C_hilfsfunktionen import lade_radiosondendaten
from C_hilfsfunktionen import lade_flugpfad
from C_hilfsfunktionen import generiere_truemmer_szenario
from C_hilfsfunktionen import berechne_differenz_m
from C_hilfsfunktionen import get_flight_phase
from C_hilfsfunktionen import get_start_speed
import tkinter as tk
from tkinter import ttk



# dropbox
def waehle_szenario():
    selected = {"szenario": None}

    def auswahl_bestaetigen():
        szenario = combo_szenario.get()
        if szenario:
            selected["szenario"] = szenario
        root.destroy()

    def abbrechen():
        selected["szenario"] = None
        root.destroy()

    root = tk.Tk()
    root.title("Szenario auswählen")
    root.geometry("300x160")
    root.attributes("-topmost", True)
    root.focus_force()
    root.lift()

    tk.Label(root, text="Szenario:").pack(pady=5)
    szenarienliste = [
        "Antriebausfall", "Strukturbruch", "Steuerverlust",
        "Fluegelabriss", "Flat Spin", "Solarmodul", "Motorblock"
    ]
    combo_szenario = ttk.Combobox(root, values=szenarienliste, state="readonly")
    combo_szenario.current(0)
    combo_szenario.pack(pady=5)

    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=10)

    tk.Button(frame_buttons, text="Berechnung starten", command=auswahl_bestaetigen, width=15).pack(side="left", padx=5)
    tk.Button(frame_buttons, text="Abbrechen", command=abbrechen, width=10).pack(side="left", padx=5)

    root.mainloop()
    return selected["szenario"]

# Aufruf
szenarioname = waehle_szenario()


# -----------------------------
# Hauptsimulation mit Karte, Validierung & QR
# -----------------------------

# 1. Lade Daten
df_radiosonde, _ = lade_radiosondendaten("radiosonde_data_60018_2025-04-18.xlsx")
df_flug = lade_flugpfad("flugbahn_200m_8pts.xlsx")

# 2. Extrahiere Flugdaten
x_flight = pd.to_numeric(df_flug["longitude"], errors='coerce').values
y_flight = pd.to_numeric(df_flug["latitude"], errors='coerce').values
z_flight = pd.to_numeric(df_flug["altitude"], errors='coerce').values
vx = vy = vz = np.zeros_like(x_flight)

# 3. Szenario auswaehlen
#szenarioname = "Antriebausfall"
szenario = generiere_truemmer_szenario(szenarioname)

#Simulation (alle Punkte)
alle_ergebnisse = []
# 3. Schleife über alle Punkte
for i in range(len(x_flight)):
    lon_start = x_flight[i]
    lat_start = y_flight[i]
    start_hoehe = z_flight[i]

    # 🧠 Flugphase & Startgeschwindigkeit berechnen
    phase = get_flight_phase(start_hoehe, vz[i])
    start_v = get_start_speed(phase, start_hoehe)
    vz[i] = start_v  # ❗ WICHTIG: vz individuell setzen

    # 🚀 Simulation starten
    zeiten, daten, lat_impact, lon_impact = simuliere_fall(
        masse=szenario["masse"][0],
        cw=szenario["cw_wert"][0],
        cl=szenario["cl_wert"][0],
        flaeche=szenario["flaeche"][0],
        radiosonde=df_radiosonde,
        x=x_flight,
        y=y_flight,
        z=z_flight,
        vx=vx,
        vy=vy,
        vz=vz,
        lon0=lon_start,
        lat0=lat_start,
        start_hoehe=start_hoehe
    )

    fallzeit = zeiten[-1]
    delta_x, delta_y = berechne_differenz_m(lon_start, lat_start, lon_impact, lat_impact)
    luftlinie = np.sqrt(delta_x**2 + delta_y**2)

    alle_ergebnisse.append({
        "Punkt": i + 1,
        "Start_Höhe [m]": start_hoehe,
        "Fallzeit [s]": fallzeit,
        "Latitude Aufprall": lat_impact,
        "Longitude Aufprall": lon_impact,
        "Distanz [m]": luftlinie
    })


# 6. Ergebnisse am Ende als CSV speichern – mit Szenarioname
df_ergebnisse = pd.DataFrame(alle_ergebnisse)
dateiname = f"aufprallpunkte_{szenarioname}.csv"
df_ergebnisse.to_csv(dateiname, index=False)


