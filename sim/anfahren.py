#!/usr/bin/env python3
"""Anfahr-Boost: Wie gibt man die an der Ampel rekuperierte Energie am besten wieder ab?

Vergleicht Strategien im eingeschwungenen Zustand (ohne Ladestecker). Aufruf: python3 sim/anfahren.py
"""
from energiebilanz import *

st = Strecke(STADT)
STRATEGIEN = [
    Boost("Ampel + Berg (bisher)"),
    Boost("A: alles sofort (35 Nm/1000 W)", True, 10, 35, 1000),
    Boost("B: sanft 15 Nm, max 10 s", True, 10, 15, 500),
    Boost("C: sanft 15 Nm bis Reisetempo", True, math.inf, 15, 500),
    Boost("D: 20 Nm bis Reisetempo", True, math.inf, 20, 500),
    Boost("E: erst ab 8 km/h, 35 Nm", True, 10, 35, 500, v_ab=8/3.6),
    Boost("F: erst ab 8 km/h, 20 Nm bis Reisetempo", True, math.inf, 20, 500, v_ab=8/3.6),
    Boost("G: Speicher gleichmäßig über 10 s", True, 10, 35, 1000, gleichmaessig=True),
]

def tabelle(fahrer, motor=Motor(), speicher_fn=lambda: lto(60), titel=""):
    ref = simuliere(st, fahrer, Rad(masse_ohne_speicher=10.0), None, None, runden=1)
    print(f"\n### {titel}Fahrer {fahrer.masse:.0f} kg, Antritt {fahrer.p_anfahr:.0f} W\n")
    print("| Strategie | Fahrer vs. SS | 0→20 km/h flach s (SS) | Boost s/Start | Wh/Start | η Boost | Rekup Wh | Reibbremse Wh |")
    print("|---|---|---|---|---|---|---|---|")
    for b in STRATEGIEN:
        e = simuliere_stationaer(st, fahrer, Rad(), motor, speicher_fn(), strategie=b)
        print(f"| {b.name} | {100*(e.fahrerarbeit_kj/ref.fahrerarbeit_kj-1):+.1f} % | {e.anfahrzeit_s:.1f} ({ref.anfahrzeit_s:.1f}) | "
              f"{e.boost_zeit_s/e.starts:.1f} | {e.boost_wh/e.starts:.2f} | {100*e.eta_boost:.0f} % | {e.rekup_wh:.1f} | {e.reibbremse_wh:.1f} |")

if __name__ == "__main__":
    tabelle(Fahrer(masse=100, p_anfahr=300), titel="LTO 60 Wh, ")
    tabelle(Fahrer(masse=100, p_anfahr=150), titel="LTO 60 Wh, ")
    tabelle(Fahrer(masse=75, p_anfahr=300), titel="LTO 60 Wh, ")
    tabelle(Fahrer(masse=120, p_anfahr=300), titel="LTO 60 Wh, ")
