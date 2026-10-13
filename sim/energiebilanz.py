#!/usr/bin/env python3
"""Energiebilanz: Singlespeed-Rad mit Boost-Knopf, Laden nur über den Bremshebel.

Fährt eine synthetische Stadtstrecke mehrmals ab und rechnet:
  - wie viel Bremsenergie im Speicher landet (Ertrag),
  - wie viel der Boost verbraucht (Bedarf),
  - wie groß und schwer der Speicher sein muss,
  - wie viel Arbeit der Fahrer im Vergleich zum normalen Singlespeed leistet.

Alle Parameter sind ANNAHMEN (siehe Dataclasses). Ergebnis = Größenordnung, keine Messung.
Keine Abhängigkeiten außer Python 3.9+.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

G = 9.81
RHO = 1.2  # Luftdichte kg/m³
DT = 0.1   # Zeitschritt s


@dataclass
class Fahrer:
    masse: float = 100.0            # kg
    p_max: float = 150.0            # W, was der Fahrer dauerhaft tritt
    f_max: float = 100.0            # N am Rad, Grenze durch Singlespeed-Übersetzung (Wiegetritt)
    v_reise: float = 22 / 3.6       # m/s
    v_bergab_max: float = 28 / 3.6  # m/s, darüber wird bergab gebremst
    a_brems: float = 1.5            # m/s², normales Bremsen an der Ampel
    t_ampel: float = 15.0           # s Standzeit


@dataclass
class Rad:
    masse_ohne_speicher: float = 14.0  # kg inkl. Motor, Regler, Kabel
    crr: float = 0.006                 # Rollwiderstand Stadtreifen
    cda: float = 0.55                  # m², aufrecht
    r: float = 0.34                    # m, 700c


@dataclass
class Motor:
    """Getriebelose Nabe (DD), grob an einer 4-kg-Klasse orientiert. Werte unsicher."""
    kt: float = 1.3             # Nm/A
    r_wicklung: float = 0.30    # Ohm, effektiv
    t_schlepp: float = 0.4      # Nm, Eisenverluste/Rastmoment, wirkt IMMER (auch ohne Strom)
    t_max: float = 35.0         # Nm
    p_boost_max: float = 500.0  # W mechanisch
    p_rekup_max: float = 1000.0 # W mechanisch
    v_rekup_min: float = 4 / 3.6
    eta_regler: float = 0.97


@dataclass
class Speicher:
    name: str
    e_gesamt: float     # Wh
    nutzbar: float      # Anteil nutzbar (LTO 10–95 % SoC, Superkondensator V bis V/2)
    eta: float          # Wirkungsgrad je Richtung (inkl. DC/DC falls nötig)
    c_max: float        # max. Leistung = c_max * e_gesamt  [W/Wh]
    wh_pro_kg: float    # Gesamtenergie pro kg Pack (Zellen + BMS + Gehäuse)

    @property
    def e_nutz(self) -> float:
        return self.e_gesamt * self.nutzbar

    @property
    def p_max(self) -> float:
        return self.c_max * self.e_gesamt

    @property
    def masse(self) -> float:
        return self.e_gesamt / self.wh_pro_kg


def lto(e_gesamt: float) -> Speicher:
    # Zellen ~90 Wh/kg, Pack-Faktor ~0,8; 10C Dauer-Laderate (zellabhängig!)
    return Speicher(f"LTO {e_gesamt:.0f} Wh", e_gesamt, 0.85, 0.97, 10.0, 72.0)


def superkondensator(e_gesamt: float) -> Speicher:
    # Zellen ~6 Wh/kg, Modul-Faktor ~0,8; braucht DC/DC wegen Spannungshub -> eta 0,98*0,96
    return Speicher(f"Superkond. {e_gesamt:.0f} Wh", e_gesamt, 0.75, 0.94, 100.0, 4.8)


def unbegrenzt() -> Speicher:
    return Speicher("unbegrenzt (Bedarfsanalyse)", 1e6, 1.0, 0.97, 1e6, 1e12)


# --------------------------------------------------------------------------- Strecke

# (Länge m, Steigung, Ampelpositionen relativ zum Abschnittsbeginn)
STADT = [
    (1200, 0.00, [300, 650, 1000, 1200]),
    (600, 0.04, [600]),
    (1500, 0.00, [350, 700, 1100, 1500]),
    (300, 0.06, []),
    (800, 0.00, [400, 800]),
    (300, -0.06, [300]),
    (1200, 0.00, [400, 800, 1200]),
    (600, -0.04, [600]),
    (1500, 0.00, [350, 750, 1100, 1500]),
]  # 8 km, 20 Ampeln, +/-42 Hm, Start = Ziel


class Strecke:
    def __init__(self, abschnitte):
        self.grenzen, self.steigungen, self.ampeln = [], [], []
        s = 0.0
        for laenge, steigung, ampeln in abschnitte:
            self.ampeln += [s + a for a in ampeln]
            s += laenge
            self.grenzen.append(s)
            self.steigungen.append(steigung)
        self.laenge = s
        self.hm = sum(l * max(st, 0) for l, st, _ in abschnitte)

    def steigung(self, s: float) -> float:
        for grenze, st in zip(self.grenzen, self.steigungen):
            if s < grenze:
                return st
        return self.steigungen[-1]


# --------------------------------------------------------------------------- Simulation

@dataclass
class Ergebnis:
    fahrerarbeit_kj: float = 0.0
    fahrzeit_s: float = 0.0
    rekup_wh: float = 0.0        # im Speicher angekommen
    boost_wh: float = 0.0        # aus dem Speicher entnommen
    boost_mech_wh: float = 0.0   # am Rad angekommen
    reibbremse_wh: float = 0.0   # in der Reibbremse verheizt
    p_rekup_peak: float = 0.0    # W elektrisch in den Speicher
    p_boost_peak: float = 0.0    # W elektrisch aus dem Speicher
    zeit_kraftlimit_s: float = 0.0  # Fahrer am Übersetzungslimit (wünscht sich kleineren Gang)
    schiebe_m: float = 0.0       # Meter, die geschoben werden müssen
    soc_min: float = math.inf
    soc_max: float = -math.inf


def simuliere(strecke: Strecke, fahrer: Fahrer, rad: Rad, motor: Motor | None,
              speicher: Speicher | None, runden: int = 8, soc_start: float = 0.5,
              boost: bool = True) -> Ergebnis:
    """Gibt das Ergebnis der LETZTEN Runde zurück (eingeschwungen)."""
    m = fahrer.masse + rad.masse_ohne_speicher + (speicher.masse if speicher else 0.0)
    soc = speicher.e_nutz * soc_start if speicher else 0.0  # Wh im nutzbaren Fenster
    unendlich = speicher is not None and speicher.e_gesamt >= 1e6
    f_schlepp = motor.t_schlepp / rad.r if motor else 0.0

    for runde in range(runden):
        e = Ergebnis()
        s, v, ampel_idx = 0.0, 0.0, 0
        while s < strecke.laenge:
            st = strecke.steigung(s)
            f_wid = m * G * rad.crr + 0.5 * RHO * rad.cda * v * v + m * G * st + f_schlepp
            ziel = strecke.ampeln[ampel_idx] if ampel_idx < len(strecke.ampeln) else None
            f_fahrer = f_motor = f_bremse = 0.0

            a_noetig = v * v / (2 * (ziel - s)) if ziel is not None and ziel > s else 0.0
            if ziel is not None and a_noetig >= fahrer.a_brems:
                # Anhalten: genau so verzögern, dass man an der Ampel steht
                f_bremse = m * a_noetig - f_wid
                if f_bremse < 0:
                    f_fahrer, f_bremse = -f_bremse, 0.0
            elif v > fahrer.v_bergab_max and f_wid < 0:
                f_bremse = -f_wid  # bergab Geschwindigkeit halten
            else:
                knopf = boost and motor is not None and (v < fahrer.v_reise - 0.3 or st >= 0.02)
                f_fahrer_max = min(fahrer.f_max, fahrer.p_max / max(v, 1.0))
                f_motor_max = min(motor.t_max / rad.r, motor.p_boost_max / max(v, 1.0)) if knopf else 0.0
                if v < fahrer.v_reise:
                    f_fahrer, f_motor = f_fahrer_max, f_motor_max
                else:  # Reisetempo halten, Motor nur am Berg
                    f_fahrer = min(max(f_wid, 0.0), f_fahrer_max)
                    f_motor = min(max(f_wid - f_fahrer, 0.0), f_motor_max)
                if f_fahrer >= fahrer.f_max - 1e-9 and f_motor == 0.0 and f_wid > 0:
                    e.zeit_kraftlimit_s += DT

            # ---- Boost: Energie aus dem Speicher
            if f_motor > 0 and speicher is not None:
                i = f_motor * rad.r / motor.kt
                p_el = (f_motor * v + i * i * motor.r_wicklung) / motor.eta_regler / speicher.eta
                if p_el > speicher.p_max:
                    f_motor *= speicher.p_max / p_el
                    i = f_motor * rad.r / motor.kt
                    p_el = (f_motor * v + i * i * motor.r_wicklung) / motor.eta_regler / speicher.eta
                if not unendlich and soc - p_el * DT / 3600 < 0:
                    f_motor, p_el = 0.0, 0.0
                soc -= p_el * DT / 3600
                e.boost_wh += p_el * DT / 3600
                e.boost_mech_wh += f_motor * v * DT / 3600
                e.p_boost_peak = max(e.p_boost_peak, p_el)
            else:
                f_motor = 0.0

            # ---- Rekuperation: Bremshebel -> erst Motor, Rest Reibbremse
            f_rekup = 0.0
            if f_bremse > 0 and motor is not None and speicher is not None and v > motor.v_rekup_min:
                # Kraft mit max. Nettoleistung (darunter fressen Kupferverluste alles)
                f_opt = v * motor.kt ** 2 / (2 * rad.r ** 2 * motor.r_wicklung)
                f_rekup = min(f_bremse, motor.t_max / rad.r, motor.p_rekup_max / v, f_opt)
                i = f_rekup * rad.r / motor.kt
                p_netto = f_rekup * v - i * i * motor.r_wicklung
                p_in = p_netto * motor.eta_regler * speicher.eta if p_netto > 0 else 0.0
                platz = (speicher.e_nutz - soc) * 3600 / DT if not unendlich else math.inf
                grenze = min(speicher.p_max, platz)
                if p_in > grenze:
                    f_rekup *= grenze / p_in
                    p_in = grenze
                if p_in <= 0:
                    f_rekup = 0.0
                soc += p_in * DT / 3600
                e.rekup_wh += p_in * DT / 3600
                e.p_rekup_peak = max(e.p_rekup_peak, p_in)
            e.reibbremse_wh += (f_bremse - f_rekup) * v * DT / 3600

            # ---- Bewegung
            e.fahrerarbeit_kj += f_fahrer * v * DT / 1000
            a = (f_fahrer + f_motor - f_wid - f_bremse) / m
            v_neu = v + a * DT
            if v_neu < 0.5 and a <= 0 and f_bremse == 0 and (ziel is None or ziel - s > 20):
                s += 1.1 * DT  # kommt nicht mehr hoch: absteigen und schieben (4 km/h)
                v = 0.0
                e.schiebe_m += 1.1 * DT
                e.fahrzeit_s += DT
                continue
            if ziel is not None and (v_neu <= 0.05 and ziel - s < 20 or s + v * DT >= ziel):
                s, v = ziel, 0.0  # an der Ampel
                ampel_idx += 1
                e.fahrzeit_s += DT  # Standzeit zählt nicht zur Fahrzeit
                continue
            v = max(v_neu, 0.0)
            s += v * DT
            e.fahrzeit_s += DT
            e.soc_min, e.soc_max = min(e.soc_min, soc), max(e.soc_max, soc)
    return e


# --------------------------------------------------------------------------- Auswertung

def zeile(name: str, masse_rad: float, e: Ergebnis, ref: Ergebnis | None) -> str:
    rel = f"{100 * (e.fahrerarbeit_kj / ref.fahrerarbeit_kj - 1):+.0f} %" if ref else "–"
    return (f"| {name} | {masse_rad:.1f} | {e.fahrerarbeit_kj:.0f} | {rel} | {e.fahrzeit_s / 60:.1f} | "
            f"{e.rekup_wh:.1f} | {e.boost_wh:.1f} | {e.reibbremse_wh:.1f} | "
            f"{e.p_rekup_peak:.0f} | {e.zeit_kraftlimit_s:.0f} | {e.schiebe_m:.0f} |")


def main() -> None:
    strecke = Strecke(STADT)
    print(f"Strecke: {strecke.laenge / 1000:.1f} km, {len(strecke.ampeln)} Ampeln, "
          f"{strecke.hm:.0f} Hm hoch/runter, Start = Ziel\n")
    ref_rad = Rad(masse_ohne_speicher=10.0)
    for masse in (75.0, 100.0, 120.0):
        fahrer = Fahrer(masse=masse)
        print(f"### Fahrer {masse:.0f} kg\n")
        print("| Variante | Rad kg | Fahrer kJ | vs. Singlespeed | Fahrzeit min | Rekup Wh | "
              "Boost Wh | Reibbremse Wh | Rekup-Peak W | s am Gang-Limit | m schieben |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        ref = simuliere(strecke, fahrer, ref_rad, None, None, runden=1)
        print(zeile("Singlespeed ohne Motor", ref_rad.masse_ohne_speicher, ref, None))

        bedarf = simuliere(strecke, fahrer, Rad(), Motor(), unbegrenzt())
        print(zeile("Boost frei, Speicher unbegrenzt", Rad().masse_ohne_speicher, bedarf, ref))

        for sp in (lto(30), lto(60), lto(100), superkondensator(15), superkondensator(40)):
            r = Rad()
            e = simuliere(strecke, fahrer, r, Motor(), sp)
            print(zeile(sp.name, r.masse_ohne_speicher + sp.masse, e, ref))

        leer = simuliere(strecke, fahrer, Rad(), Motor(), lto(60), soc_start=0.0, runden=1, boost=False)
        print(zeile("Boost aus (nur Ballast + Schleppmoment)", Rad().masse_ohne_speicher + lto(60).masse,
                    leer, ref))
        deckung = bedarf.rekup_wh / bedarf.boost_wh if bedarf.boost_wh else 0
        print(f"\nDeckungsgrad Rekup/Boost-Bedarf bei freiem Boost: {100 * deckung:.0f} %  "
              f"(Hub im Speicher über eine Runde: {bedarf.soc_max - bedarf.soc_min:.1f} Wh)\n")
    sensitivitaet(strecke)


def sensitivitaet(strecke: Strecke) -> None:
    """Fahrer 100 kg, LTO 60 Wh: Wie stark hängt das Ergebnis an den unsichersten Annahmen?"""
    print("### Sensitivität (Fahrer 100 kg, LTO 60 Wh)\n")
    print("| Variante | Fahrer vs. Singlespeed | Rekup Wh | Fahrzeit min (Singlespeed) |")
    print("|---|---|---|---|")
    besser = Motor(kt=1.6, r_wicklung=0.2)
    faelle = [
        ("Basis (Schlepp 0,4 Nm, kt 1,3, R 0,3 Ω)", Motor(), Rad(), Fahrer()),
        ("Schleppmoment 0,15 Nm", Motor(t_schlepp=0.15), Rad(), Fahrer()),
        ("Schleppmoment 0,8 Nm", Motor(t_schlepp=0.8), Rad(), Fahrer()),
        ("weniger Kupferverluste (kt 1,6, R 0,2 Ω)", besser, Rad(), Fahrer()),
        ("weniger Kupferverluste + Schlepp 0,15 Nm", replace(besser, t_schlepp=0.15), Rad(), Fahrer()),
        ("dito + Rad 1,5 kg leichter", replace(besser, t_schlepp=0.15), Rad(masse_ohne_speicher=12.5), Fahrer()),
        ("sanft bremsen 1,0 m/s²", Motor(), Rad(), Fahrer(a_brems=1.0)),
        ("hart bremsen 2,5 m/s²", Motor(), Rad(), Fahrer(a_brems=2.5)),
    ]
    for name, motor, rad, fahrer in faelle:
        ref = simuliere(strecke, fahrer, Rad(masse_ohne_speicher=10.0), None, None, runden=1)
        e = simuliere(strecke, fahrer, rad, motor, lto(60))
        print(f"| {name} | {100 * (e.fahrerarbeit_kj / ref.fahrerarbeit_kj - 1):+.1f} % | {e.rekup_wh:.1f} | "
              f"{e.fahrzeit_s / 60:.1f} ({ref.fahrzeit_s / 60:.1f}) |")
    print()


if __name__ == "__main__":
    main()
