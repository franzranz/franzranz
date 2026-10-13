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


def alternativen(strecke: Strecke, titel: str) -> None:
    """Gleiches Ziel (leichter anfahren), andere Wege: kürzeres Ritzel, Mehrgang-Nabe, Motor.

    Achtung: Das Fahrermodell kennt keine Trittfrequenz-Kosten (kürzeres Ritzel = höhere Kadenz bei Reisetempo)
    und tritt immer mit voller Kraft; der Motor macht den Fahrer schneller, nicht leichter.
    """
    # Sturmey-Archer S2 Kickshift (120 mm, ~0,5 kg netto): kleiner Gang direkt, großer Gang 138 % über Planeten.
    # Shimano Nexus 3 (120 mm, ~0,9 kg netto): 1. Gang 0,733 über Planeten, 2. Gang direkt (= Singlespeed).
    # Wirkungsgrade der Planetenstufe: Annahme 0,94 (Kyle/Berto: Nabenschaltungen 86-95 %).
    s2 = Rad(masse_ohne_speicher=BASIS_RAD + 0.5, gang_klein=1 / 1.38, eta_klein=0.99, eta_gross=0.94)
    nexus3 = Rad(masse_ohne_speicher=BASIS_RAD + 0.9, gang_klein=0.733, eta_klein=0.94, eta_gross=0.99)
    g = STRATEGIEN[1]
    anfahrhilfe = Boost("Anfahrhilfe nur bis 12 km/h", True, 10, 35, 1000, v_bis=12 / 3.6)
    ritzel_12 = Rad(masse_ohne_speicher=BASIS_RAD, gang_klein=0.88, v_schalt=math.inf)
    ritzel_20 = Rad(masse_ohne_speicher=BASIS_RAD, gang_klein=0.80, v_schalt=math.inf)
    for p_anfahr in (300, 150):
        fahrer = Fahrer(masse=100, p_anfahr=p_anfahr)
        ref = simuliere(strecke, fahrer, Rad(masse_ohne_speicher=BASIS_RAD), None, None, runden=1)
        print(f"\n### Alternativen zum selben Ziel: {titel}, Fahrer 100 kg, Antritt {p_anfahr} W\n")
        print("| Variante | Rad kg | Fahrer gesamt vs. SS | 0→20 km/h s | Fahrer-J pro Start | "
              "s am Kraftlimit ohne Motorhilfe |")
        print("|---|---|---|---|---|---|")
        zeilen = [("Singlespeed", BASIS_RAD, ref)]
        zeilen.append(("Singlespeed, Ritzel +2 Zähne (12 % kürzer, höhere Kadenz)", BASIS_RAD,
                       simuliere(strecke, fahrer, ritzel_12, None, None, runden=1)))
        zeilen.append(("Singlespeed, 20 % kürzer übersetzt (höhere Kadenz)", BASIS_RAD,
                       simuliere(strecke, fahrer, ritzel_20, None, None, runden=1)))
        zeilen.append(("Zweigang-Nabe Sturmey-Archer S2 (Anfahrgang direkt, großer Gang 138 %)", s2.masse_ohne_speicher,
                       simuliere(strecke, fahrer, s2, None, None, runden=1)))
        zeilen.append(("Dreigang-Nabe Shimano Nexus 3 (1. Gang 0,733, 2. Gang direkt)", nexus3.masse_ohne_speicher,
                       simuliere(strecke, fahrer, nexus3, None, None, runden=1)))
        for key in ("sx1", "all_axle"):
            motor = MOTOREN[key]
            rad = rad_fuer(motor)
            for b in (g, anfahrhilfe):
                sp = SPEICHER()
                zeilen.append((f"{motor.name}, {b.name}", rad.masse_ohne_speicher + sp.masse,
                               simuliere_stationaer(strecke, fahrer, rad, motor, sp, strategie=b)))
        for name, kg, e in zeilen:
            print(f"| {name} | {kg:.1f} | {100 * (e.fahrerarbeit_kj / ref.fahrerarbeit_kj - 1):+.1f} % | "
                  f"{e.anfahrzeit_s:.1f} | {e.anfahr_fahrer_j_pro_start:.0f} | {e.zeit_kraftlimit_s:.0f} |")


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
    alternativen(stadt, "Stadtstrecke mit Gefällen")
    alternativen(Strecke(flach_mit_ampeln(400)), "flach, Ampel alle 400 m")


if __name__ == "__main__":
    main()
