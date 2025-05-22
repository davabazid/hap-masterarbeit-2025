# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 10:53:48 2025

@author: david
"""

import pandas as pd
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import webbrowser

station = "60018"

# Hier jetzt der vollständige Text, aus deiner langen Nachricht kopiert:
daten_text = """
 1004.0    105   18.4   10.4     60   7.91    185    4.0  291.2  313.9  292.6
 1000.0    150   19.0   10.0     56   7.73    175    3.0  292.1  314.4  293.5
  999.0    159   19.4   10.4     56   7.95    173    3.0  292.6  315.6  294.0
  952.0    571   16.0    8.0     59   7.08     77    1.3  293.2  313.8  294.5
  944.0    642   15.9    7.1     56   6.70     60    1.0  293.9  313.5  295.1
  925.0    815   15.8    4.8     48   5.84    335    3.0  295.5  312.7  296.5
  907.0    982   15.2    2.6     43   5.10      0    5.0  296.5  311.7  297.4
  902.0   1029   15.0    2.0     41   4.91      0    5.1  296.8  311.5  297.6
  882.0   1219   17.2   -8.8     16   2.23      2    5.5  301.0  308.0  301.4
  857.0   1463   16.1  -13.0     12   1.64      5    6.0  302.3  307.6  302.6
  850.0   1533   15.8  -14.2     11   1.50     10    6.0  302.7  307.6  303.0
  832.0   1714   15.6  -22.4      6   0.76     22    6.8  304.3  306.9  304.5
  805.0   1990   13.8  -24.7      5   0.65     40    8.0  305.3  307.5  305.4
  791.0   2138   12.8  -25.9      5   0.59     35    9.0  305.8  307.8  305.9
  771.0   2352   11.4  -27.6      5   0.52     24    8.6  306.5  308.3  306.6
  747.0   2613    9.5  -28.5      5   0.49     10    8.0  307.2  308.9  307.3
  700.0   3148    5.6  -30.4      5   0.44     20    6.0  308.7  310.2  308.7
  690.0   3263    4.8  -30.9      5   0.42     20    6.0  309.1  310.6  309.1
  678.0   3404    3.9  -31.4      6   0.41     15    5.0  309.6  311.0  309.6
  653.0   3704    1.9  -32.6      6   0.38    295    5.0  310.6  312.0  310.7
  591.0   4502   -3.5  -35.8      6   0.31    245    5.0  313.4  314.5  313.5
  582.0   4625   -4.3  -36.3      6   0.30    253    5.0  313.8  314.9  313.9
  580.0   4652   -4.5  -35.4      7   0.32    255    5.0  313.9  315.1  313.9
  540.0   5209   -8.9  -16.9     52   1.89    242    6.7  315.1  321.5  315.5
  533.0   5309   -9.5  -17.0     55   1.91    240    7.0  315.5  322.0  315.9
  524.0   5441  -10.4  -17.0     58   1.93    255    5.0  316.1  322.6  316.5
  516.0   5559  -11.1  -17.1     61   1.95    268    7.7  316.6  323.2  317.0
  515.0   5574  -11.2  -17.3     60   1.91    270    8.0  316.7  323.2  317.0
  500.0   5800  -12.1  -21.1     47   1.43    270   10.0  318.2  323.2  318.5
  464.0   6369  -16.1  -26.1     42   0.98    268   12.8  320.1  323.6  320.3
  426.0   7004  -21.6  -31.6     40   0.64    265   16.0  321.1  323.4  321.2
  403.0   7416  -25.1  -35.1     39   0.48    256   20.4  321.6  323.4  321.7
  400.0   7470  -25.3  -36.3     35   0.43    255   21.0  322.0  323.6  322.1
  390.0   7654  -25.7  -46.7     12   0.15    252   23.9  323.8  324.4  323.9
  387.0   7710  -25.9  -42.9     19   0.22    251   24.8  324.3  325.2  324.3
  383.0   7784  -26.6  -43.0     20   0.22    250   26.0  324.4  325.2  324.4
  330.0   8840  -36.3  -44.3     43   0.23    259   21.4  325.1  326.0  325.2
  329.0   8861  -36.1  -51.1     20   0.11    259   21.3  325.7  326.1  325.7
  326.0   8925  -36.3  -53.0     16   0.09    260   21.0  326.3  326.7  326.3
  315.0   9163  -36.9  -59.9      7   0.04    258   23.1  328.6  328.8  328.6
  300.0   9500  -38.3  -66.3      4   0.02    255   26.0  331.3  331.3  331.3
  270.0  10215  -41.1  -70.1      3   0.01    250   39.6  337.3  337.4  337.3
  267.0  10290  -41.6  -69.9      3   0.01    250   41.0  337.6  337.7  337.6
  250.0  10730  -44.7  -68.7      5   0.01    250   42.0  339.5  339.5  339.5
  235.0  11142  -47.3  -71.3      5   0.01    250   44.0  341.6  341.6  341.6
  221.0  11545  -48.7  -73.5      4   0.01    250   46.0  345.4  345.5  345.4
  200.0  12200  -51.1  -77.1      3   0.01    250   43.0  351.7  351.7  351.7
  175.0  13057  -54.9  -80.9      3   0.00    240   40.0  359.0  359.1  359.0
  159.0  13673  -57.7  -83.7      2   0.00    246   37.5  364.3  364.4  364.4
  150.0  14040  -59.1  -85.1      2   0.00    250   36.0  368.1  368.1  368.1
  142.0  14379  -61.3  -86.0      2   0.00    255   32.0  370.1  370.1  370.1
  127.0  15069  -65.7  -87.7      3   0.00    243   28.4  374.1  374.1  374.1
  118.0  15512  -66.9  -87.9      4   0.00    235   26.0  379.9  379.9  379.9
  107.0  16102  -68.4  -88.3      4   0.00    245   29.0  387.7  387.7  387.7
  100.0  16510  -69.5  -88.5      5   0.00    255   19.0  393.2  393.2  393.2
   96.0  16753  -70.3  -88.7      5   0.00    240   14.9  396.3  396.3  396.3
   92.0  17006  -71.1  -88.9      6   0.00    250   12.4  399.6  399.6  399.6
   87.0  17338  -72.1  -89.1      6   0.00    230   15.4  403.9  403.9  403.9
   85.0  17477  -71.9  -89.2      6   0.00    235   12.4  407.0  407.1  407.0
   81.0  17763  -71.4  -89.4      5   0.00    215    6.2  413.6  413.6  413.6
   78.0  17987  -71.1  -89.6      5   0.00    220   13.4  418.8  418.8  418.8
   75.0  18220  -70.7  -89.8      5   0.00    265   10.8  424.3  424.3  424.3
   71.0  18546  -70.2  -90.0      4   0.00    250    9.8  432.1  432.1  432.1
   70.0  18630  -70.1  -90.1      4   0.00    255    9.8  434.1  434.1  434.1
   65.0  19073  -69.5  -90.2      4   0.00    285    3.6  444.6  444.6  444.6
   60.0  19550  -68.9  -90.4      3   0.00    275    5.2  456.2  456.2  456.2
   51.0  20521  -67.7  -90.7      3   0.00    135    5.2  480.7  480.8  480.7
   50.8  20544  -67.7  -90.7      3   0.00    139    5.2  481.3  481.4  481.3
   50.0  20640  -66.5  -90.5      2   0.00    155    5.2  486.4  486.4  486.4
   48.6  20813  -63.3  -90.3      1   0.00     84    2.8  497.9  497.9  497.9
   47.0  21021  -62.4  -89.8      1   0.00      0    0.0  504.9  505.0  504.9
                  
""" # Gekürzt wegen Platz, vollständiger Text würde eingefügt werden.


# Verarbeitung
linien = daten_text.strip().split('\n')
daten_zeilen = []
for zeile in linien:
    if re.match(r'^\s*\d', zeile):
        daten_zeilen.append(zeile)

spalten = ['PRES', 'HGHT', 'TEMP', 'DWPT', 'RELH', 'MIXR', 'DRCT', 'SPED', 'THTA', 'THTE', 'THTV']

daten = []
for zeile in daten_zeilen:
    werte = re.split(r'\s+', zeile.strip())
    while len(werte) < len(spalten):
        werte.append(None)
    daten.append(werte[:len(spalten)])

# DataFrame erstellen
df = pd.DataFrame(daten, columns=spalten)

# Konvertiere die Spalten in numerische Werte
for spalte in df.columns:
    df[spalte] = pd.to_numeric(df[spalte], errors='coerce')

# Aktuelles Datum holen (Format: JJJJ-MM-TT)
heute = datetime.now().strftime("%Y-%m-%d")

# Dateinamen
output_excel = f"radiosonde_data_{station}_{heute}.xlsx"
output_html = f"radiosonde_data_{station}_{heute}.html"

# DataFrame als Excel speichern
df.to_excel(output_excel, index=False)
print(f"✅ Excel gespeichert: {output_excel}")

# DataFrame als HTML speichern mit schöner Tabelle
html_content = df.to_html(index=False, border=0, classes='table table-striped table-hover')
with open(output_html, "w", encoding="utf-8") as f:
    f.write(f"""
    <html>
    <head>
        <title>Radiosondendaten {station} {heute}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
    </head>
    <body>
    <div class="container">
        <h2 class="mt-4 mb-4">Radiosondendaten Station {station} vom {heute}</h2>
        {html_content}
    </div>
    </body>
    </html>
    """)
print(f"✅ HTML gespeichert: {output_html}")

# HTML-Datei im Browser öffnen
webbrowser.open(output_html)

# GUI-Tabelle anzeigen (tkinter)
root = tk.Tk()
root.title("Radiosondendaten Tabelle")

# Treeview Tabelle
tree = ttk.Treeview(root)
tree['columns'] = list(df.columns)
tree['show'] = 'headings'

# Scrollbar hinzufügen
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Spaltenüberschriften erstellen
for col in df.columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=80)

# Daten einfügen
for index, row in df.iterrows():
    tree.insert("", "end", values=list(row))

# Packen
tree.pack(side="left", expand=True, fill='both')
scrollbar.pack(side="right", fill='y')

# Fenster starten
root.mainloop()
