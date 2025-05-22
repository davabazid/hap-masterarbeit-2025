# 🎓 Master Thesis – Safety Analysis of High-Altitude Platforms (HAP)

This repository contains the complete simulation and visualization framework developed as part of my Master's thesis in Aerospace Engineering at TU Braunschweig, in collaboration with the German Aerospace Center (DLR).

---

## 📦 Repository Contents

### 🧠 Simulation Modules
| Filename | Description |
|----------|-------------|
| `A_Simu_FlightPath_12.04.2025.py` | Calculates and plots 2D/3D nominal flight paths from Excel data |
| `B_Simu_radiosonden_daten_abholen_10.04.2025.py` | Parses atmospheric radiosonde measurements |
| `C_hilfsfunktionen.py` | Physics, aerodynamics, and utility functions for all simulations |
| `D_SimuEinzelpunktFinal.py` | GUI-based simulation of single crash point for selected scenarios |
| `E_simu_berechnung_alle_aufprallpunkte.py` | Computes impact points across the entire flight trajectory |
| `F_simu_darstellung_alle_aufprallpunkte.py` | Visualization and Gaussian classification of impact zones |
| `G_simu_InteraktivKarten.py` | Interactive map with convex hulls, legend, and Google Earth link |
| `H_simu_darstellung_(Gauß_Bahnzentrum)_alle_aufprallpunkte.py` | Heatmaps and histograms centered on flight path barycenter |
| `I_SimulationAbrufen.py` | GUI-based script launcher (start simulations directly) |
| `J_Wind.py` | Wind and atmospheric profile visualization (wind rose, quiver, etc.) |
| `SkripteOeffnen_GUI.py` | Tool to launch simulation scripts from local folder via VS Code |

---

## 📎 CV

📄 A complete overview of my academic and aerospace experience can be found here:

👉 [CV_DavidAba.pdf](./CV_DavidAba.pdf)

This CV also links back to this repository and is suitable for aerospace, defense, or simulation-focused applications.

---

## 🚀 How to Use

1. Install required libraries:
   ```bash
   pip install pandas numpy matplotlib scipy folium simplekml
   ```
2. Run `I_SimulationAbrufen.py` to launch the main control GUI.
3. Select a simulation scenario and observe results including:
   - Flight paths
   - Impact zones
   - Risk maps
   - Interactive maps (HTML/Folium)
   - Statistical evaluations

---

## 🛰️ Thesis Info

- **Title**: Risk and Safety Analysis of HAP (High-Altitude Platform) Systems  
- **Author**: David Wolf (formerly David Aba Zid)  
- **Institution**: TU Braunschweig  
- **Partner**: DLR – German Aerospace Center  
- **Field**: Aerospace Safety, Crash Modelling, Wind Profiling  
- **Tools**: Python, Folium, VS Code, Excel, Tkinter GUIs

---

## 📬 Contact

📧 david.abazid@gmx.de  
🔗 [LinkedIn](https://www.linkedin.com/in/david-a-665392244)

---

## 📜 License

This work is distributed for educational and research purposes only. Any commercial use requires written permission.
