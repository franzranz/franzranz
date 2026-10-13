#!/usr/bin/env python3
"""Machbarkeit: echte Frontmotoren + Superkondensator, Boost nur zum Anfahren.

Vergleich mit einem 10-kg-Singlespeed ohne Motor. Aufruf: python3 sim/machbarkeit.py
"""
from dataclasses import replace

from energiebilanz import *

BASIS_RAD = 10.0        # kg, Alu-Singlespeed mit zwei Hydraulik-Scheibenbremsen
NORMALE_NABE = 0.15     # kg, entfällt
ELEKTRIK = 0.5          # kg, VESC-Regler, Kabel, Bremssensor, Knopf, Halter
SPEICHER = skeleton_13s

STRATEGIEN = [
    Boost("alles sofort (35 Nm)", True, 10, 35, 1000),
    Boost("gleichmäßig über 10 s", True, 10, 35, 1000, gleichmaessig=True),
    Boost("sanft 15 Nm bis Reisetempo", True, math.inf, 15, 500),
]


def rad_fuer(motor: Motor) -> Rad:
    return Rad(masse_ohne_speicher=BASIS_RAD - NORMALE_NABE + motor.masse + ELEKTRIK)


def tabelle(strecke: Strecke, fahrer: Fahrer, motoren, titel: str) -> None:
    ref = simuliere(strecke, fahrer, Rad(masse_ohne_speicher=BASIS_RAD), None, None, runden=1)
    print(f"\n### {titel}: Fahrer {fahrer.masse:.0f} kg, Antritt {fahrer.p_anfahr:.0f} W\n")
    print(f"Singlespeed {BASIS_RAD:.0f} kg: 0→20 km/h {ref.anfahrzeit_s:.1f} s, "
          f"Fahrerarbeit pro Start {ref.anfahr_fahrer_j_pro_start:.0f} J, "
          f"{ref.zeit_kraftlimit_s:.0f} s am Übersetzungslimit, Fahrzeit {ref.fahrzeit_s / 60:.1f} min\n")
    print("| Motor | Strategie | Rad kg | Fahrer gesamt vs. SS | 0→20 km/h s | Fahrer-J pro Start | Motoranteil Anfahren | "
          "s am Limit | Boost s/Start | η Boost | Rekup Wh/Start inkl. Gefälle |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for motor in motoren:
        rad = rad_fuer(motor)
        for b in STRATEGIEN:
            sp = SPEICHER()
            e = simuliere_stationaer(strecke, fahrer, rad, motor, sp, strategie=b)
            print(f"| {motor.name} | {b.name} | {rad.masse_ohne_speicher + sp.masse:.1f} | "
                  f"{100 * (e.fahrerarbeit_kj / ref.fahrerarbeit_kj - 1):+.1f} % | {e.anfahrzeit_s:.1f} | "
                  f"{e.anfahr_fahrer_j_pro_start:.0f} | {100 * e.motoranteil_anfahren:.0f} % | {e.zeit_kraftlimit_s:.0f} | "
                  f"{e.boost_zeit_s / e.starts:.1f} | {100 * e.eta_boost:.0f} % | {e.rekup_wh / e.starts:.2f} |")


def ampelabstand(fahrer: Fahrer, motoren, strategie: Boost) -> None:
    print(f"\n### Wann frisst das Schleppmoment den Nutzen? Flach, Fahrer {fahrer.masse:.0f} kg, "
          f"Strategie '{strategie.name}'\n")
    print("Zelle: Fahrerarbeit gesamt vs. Singlespeed / Rekuperation pro Ampelstopp (Wh, im Speicher)\n")
    abstaende = (250, 400, 600, 1000, 2000)
    print("| Motor | " + " | ".join(f"Ampel alle {a} m" for a in abstaende) + " |")
    print("|---|" + "---|" * len(abstaende))
    for motor in motoren:
        zellen = []
        for a in abstaende:
            st = Strecke(flach_mit_ampeln(a))
            ref = simuliere(st, fahrer, Rad(masse_ohne_speicher=BASIS_RAD), None, None, runden=1)
            e = simuliere_stationaer(st, fahrer, rad_fuer(motor), motor, SPEICHER(), strategie=strategie)
            zellen.append(f"{100 * (e.fahrerarbeit_kj / ref.fahrerarbeit_kj - 1):+.1f} % / {e.rekup_wh / e.starts:.2f}")
        print(f"| {motor.name} | " + " | ".join(zellen) + " |")


def ausrollen(strecke: Strecke, motoren, strategie: Boost) -> None:
    print(f"\n### Ausrollen vor der Ampel (weniger Bremsenergie). Stadtstrecke, Fahrer 100 kg, 300 W, "
          f"Strategie '{strategie.name}'\n")
    print("| Motor | ausrollen ab | Fahrer gesamt vs. SS | Fahrer-J pro Start (SS) | Motoranteil Anfahren | Rekup Wh/Start |")
    print("|---|---|---|---|---|---|")
    for motor in motoren:
        for aus in (0, 30, 60, 100):
            fahrer = Fahrer(masse=100, p_anfahr=300, ausroll_m=aus)
            ref = simuliere(strecke, fahrer, Rad(masse_ohne_speicher=BASIS_RAD), None, None, runden=1)
            e = simuliere_stationaer(strecke, fahrer, rad_fuer(motor), motor, SPEICHER(), strategie=strategie)
            print(f"| {motor.name} | {aus} m | {100 * (e.fahrerarbeit_kj / ref.fahrerarbeit_kj - 1):+.1f} % | "
                  f"{e.anfahr_fahrer_j_pro_start:.0f} ({ref.anfahr_fahrer_j_pro_start:.0f}) | "
                  f"{100 * e.motoranteil_anfahren:.0f} % | {e.rekup_wh / e.starts:.2f} |")


def main() -> None:
    stadt = Strecke(STADT)
    motoren = list(MOTOREN.values())
    sx1 = MOTOREN["sx1"]
    sx1_pess = replace(sx1, name="SX1 pessimistisch (R pro Phase, Schlepp x2)", r_wicklung=2 * sx1.r_wicklung,
                       t_schlepp=2 * sx1.t_schlepp, k_wirbel=2 * sx1.k_wirbel)
    print(f"Strecke: {stadt.laenge / 1000:.0f} km, {len(stadt.ampeln)} Ampeln, {stadt.hm:.0f} Hm. "
          f"Speicher: {SPEICHER().name}, {SPEICHER().masse:.1f} kg. Eingeschwungen, ohne Ladestecker.")
    for masse in (75.0, 100.0, 120.0):
        tabelle(stadt, Fahrer(masse=masse, p_anfahr=300), motoren + [sx1_pess], "Stadtstrecke")
    tabelle(stadt, Fahrer(masse=100, p_anfahr=150), motoren, "Stadtstrecke, schwacher Antritt")
    ampelabstand(Fahrer(masse=100, p_anfahr=300), motoren + [sx1_pess], STRATEGIEN[1])
    ausrollen(stadt, [MOTOREN["all_axle"], sx1], STRATEGIEN[1])


if __name__ == "__main__":
    main()
