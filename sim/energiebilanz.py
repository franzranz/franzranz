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
    p_anfahr: float = 150.0         # W in den ersten 10 s nach dem Losfahren (Antritt)
    f_max: float = 100.0            # N am Rad, Grenze durch Singlespeed-Übersetzung (Wiegetritt)
    v_reise: float = 22 / 3.6       # m/s
    v_bergab_max: float = 28 / 3.6  # m/s, darüber wird bergab gebremst
    a_brems: float = 1.5            # m/s², normales Bremsen an der Ampel
    t_ampel: float = 15.0           # s Standzeit
    ausroll_m: float = 0.0          # m vor der Ampel aufhören zu treten (0 = bis zum Bremspunkt treten)


@dataclass
class Rad:
    masse_ohne_speicher: float = 14.0  # kg inkl. Motor, Regler, Kabel
    crr: float = 0.006                 # Rollwiderstand Stadtreifen
    cda: float = 0.55                  # m², aufrecht
    r: float = 0.34                    # m, 700c
    # Optional: Zweigang-Nabe statt Singlespeed (Alternative ohne Motor)
    gang_klein: float | None = None    # Übersetzungsfaktor des Anfahrgangs, z. B. 0,73 = 27 % leichter
    v_schalt: float = 15 / 3.6         # m/s, darüber direkter Gang
    eta_klein: float = 0.94            # Wirkungsgrad im Anfahrgang (Planetengetriebe)
    eta_direkt: float = 0.98           # Wirkungsgrad im direkten Gang

    def gang(self, v: float) -> tuple[float, float]:
        """(Kraftfaktor am Rad, Wirkungsgrad) für die aktuelle Geschwindigkeit."""
        if self.gang_klein is None:
            return 1.0, 1.0
        if v < self.v_schalt:
            return 1.0 / self.gang_klein, self.eta_klein
        return 1.0, self.eta_direkt


@dataclass
class Motor:
    """Nabenmotor. Default = grobe Schätzung einer 4-kg-DD-Nabe; echte Kandidaten siehe MOTOREN."""
    kt: float = 1.3             # Nm/A am Rad (= 9,55 / Kv)
    r_wicklung: float = 0.30    # Ohm (Phase-Phase), Kupferverlust = (T/kt)² * R
    t_schlepp: float = 0.4      # Nm, Hysterese/Rastmoment, wirkt IMMER (auch ohne Strom)
    k_wirbel: float = 0.0       # Nm pro rad/s, Wirbelstrom-Schleppmoment
    t_max: float = 35.0         # Nm
    p_boost_max: float = 500.0  # W mechanisch
    p_rekup_max: float = 1000.0 # W mechanisch
    v_rekup_min: float = 4 / 3.6
    eta_regler: float = 0.97
    eta_getriebe: float = 1.0   # je Richtung (Getriebenabe ~0,9)
    kv: float | None = None     # U/min pro Volt am Rad; begrenzt Boost über die Gegenspannung
    masse: float = 4.0          # kg
    name: str = "Schätzung DD 4 kg"

    def schlepp(self, v: float, r: float) -> float:
        """Schleppkraft am Rad in N."""
        return (self.t_schlepp + self.k_wirbel * v / r) / r


def motor_aus_datenblatt(name: str, kv: float, r_ll: float, t_schlepp: float, k_wirbel: float,
                         eta_getriebe: float, masse: float, **kw) -> Motor:
    return Motor(kt=9.55 / kv, r_wicklung=r_ll, t_schlepp=t_schlepp, k_wirbel=k_wirbel,
                 eta_getriebe=eta_getriebe, kv=kv, masse=masse, name=name, **kw)


# Kennwerte aus Grin-Listings (ebikes.ca, per Suchmaschinen-Snippet geprüft, Primärseiten nicht abrufbar).
# Getriebewirkungsgrad 0,9 ist eine Annahme. Bei der SX1 ist unklar, ob R Phase-Phase oder pro Phase angegeben ist.
MOTOREN = {
    "all_axle": motor_aus_datenblatt("Grin All-Axle V3 Front (DD, Std)", 10.0, 0.145, 0.60, 0.005, 1.0, 4.05),
    "sx1": motor_aus_datenblatt("Shengyi SX1 Front Regen-Mod (Getriebe, Fast)", 9.8, 0.072, 0.43, 0.009, 0.9, 2.95),
    "ezee": motor_aus_datenblatt("eZee Front Regen (Getriebe, Std)", 8.1, 0.075, 0.58, 0.039, 0.9, 3.78),
}


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

    v_max: float | None = None  # V bei vollem Speicher; Kondensator: U ~ sqrt(E)
    kondensator: bool = False

    @property
    def masse(self) -> float:
        return self.e_gesamt / self.wh_pro_kg

    def spannung(self, soc: float) -> float | None:
        """Busspannung bei 'soc' Wh im nutzbaren Fenster."""
        if self.v_max is None:
            return None
        e_rest = self.e_gesamt * (1 - self.nutzbar)
        if self.kondensator:
            return self.v_max * math.sqrt(max(e_rest + soc, 0.0) / self.e_gesamt)
        return self.v_max * (0.85 + 0.15 * soc / self.e_nutz)  # Batterie: grob flache Kennlinie


def lto(e_gesamt: float) -> Speicher:
    # Zellen ~90 Wh/kg, Pack-Faktor ~0,8; 10C Dauer-Laderate (zellabhängig!)
    return Speicher(f"LTO {e_gesamt:.0f} Wh", e_gesamt, 0.85, 0.97, 10.0, 72.0)


def superkondensator(e_gesamt: float) -> Speicher:
    # Zellen ~6 Wh/kg, Modul-Faktor ~0,8; braucht DC/DC wegen Spannungshub -> eta 0,98*0,96
    return Speicher(f"Superkond. {e_gesamt:.0f} Wh", e_gesamt, 0.75, 0.94, 1000.0, 4.8)


def skeleton_13s() -> Speicher:
    """13 x Skeleton SCA0300 EVO in Serie: 4,84 Wh, 37 V, nutzbar bis 0,6 * Vmax (3,1 Wh), ~1,0 kg fertig."""
    return Speicher("Superkond. 13S Skeleton (3,1 Wh nutzbar)", 4.84, 0.64, 0.98, 500.0, 4.84,
                    v_max=37.05, kondensator=True)


def unbegrenzt() -> Speicher:
    return Speicher("unbegrenzt (Bedarfsanalyse)", 1e6, 1.0, 0.97, 1e6, 1e12)


@dataclass
class Boost:
    """Wann und wie stark der Boost-Knopf zieht."""
    name: str = "Ampel + Berg"
    nur_anfahren: bool = False   # nur nach Stillstand, nie am Berg
    dauer: float = math.inf      # s nach dem Losfahren
    t_max: float | None = None   # Nm, None = Motorgrenze
    p_max: float | None = None   # W mechanisch, None = Motorgrenze
    v_ab: float = 0.0            # m/s, Boost erst ab dieser Geschwindigkeit
    gleichmaessig: bool = False  # Energie im Speicher gleichmäßig auf 'dauer' verteilen


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


def flach_mit_ampeln(abstand: float, laenge: float = 8000.0):
    """Flache Strecke, Ampel alle 'abstand' Meter."""
    n = int(laenge // abstand)
    return [(abstand, 0.0, [abstand])] * n


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
    starts: int = 0                   # alle Starts aus dem Stand
    starts_flach: int = 0             # davon auf der Ebene und bis 20 km/h gekommen
    anfahrzeit_summe_s: float = 0.0   # 0 -> 20 km/h, nur Starts auf der Ebene
    boost_zeit_s: float = 0.0         # Sekunden mit Motorkraft > 0
    kupfer_boost_wh: float = 0.0      # im Motor verheizt beim Boost
    soc_anfang: float = 0.0
    soc_ende: float = 0.0
    anfahr_fahrer_j: float = 0.0      # Fahrerarbeit 0 -> 20 km/h, nur Starts auf der Ebene
    anfahr_motor_j: float = 0.0       # Motorarbeit am Rad im selben Fenster

    @property
    def anfahr_fahrer_j_pro_start(self) -> float:
        return self.anfahr_fahrer_j / self.starts_flach if self.starts_flach else 0.0

    @property
    def motoranteil_anfahren(self) -> float:
        summe = self.anfahr_fahrer_j + self.anfahr_motor_j
        return self.anfahr_motor_j / summe if summe else 0.0

    @property
    def anfahrzeit_s(self) -> float:
        return self.anfahrzeit_summe_s / self.starts_flach if self.starts_flach else 0.0

    @property
    def eta_boost(self) -> float:
        return self.boost_mech_wh / self.boost_wh if self.boost_wh else 0.0


def simuliere(strecke: Strecke, fahrer: Fahrer, rad: Rad, motor: Motor | None,
              speicher: Speicher | None, runden: int = 8, soc_start: float = 0.5,
              boost: bool = True, strategie: Boost = Boost(), soc_wh: float | None = None) -> Ergebnis:
    """Gibt das Ergebnis der LETZTEN Runde zurück."""
    m = fahrer.masse + rad.masse_ohne_speicher + (speicher.masse if speicher else 0.0)
    soc = speicher.e_nutz * soc_start if speicher else 0.0  # Wh im nutzbaren Fenster
    if soc_wh is not None and speicher is not None:
        soc = soc_wh
    unendlich = speicher is not None and speicher.e_gesamt >= 1e6

    for runde in range(runden):
        e = Ergebnis(soc_anfang=soc)
        s, v, ampel_idx = 0.0, 0.0, 0
        t_start, soc_beim_start, gemessen = 0.0, soc, strecke.steigung(0.0) != 0
        e.starts = 1
        bremst = False  # Hysterese: einmal für die Ampel gebremst, bis zum Stillstand
        while s < strecke.laenge:
            st = strecke.steigung(s)
            f_schlepp = motor.schlepp(v, rad.r) if motor else 0.0
            f_wid = m * G * rad.crr + 0.5 * RHO * rad.cda * v * v + m * G * st + f_schlepp
            ziel = strecke.ampeln[ampel_idx] if ampel_idx < len(strecke.ampeln) else None
            f_fahrer = f_motor = f_bremse = 0.0
            antrieb = False

            rest = ziel - s if ziel is not None else math.inf
            a_noetig = v * v / (2 * rest) if rest > 0.01 else 0.0
            bremst = bremst or (ziel is not None and a_noetig >= fahrer.a_brems)
            if bremst:
                # Anhalten: genau so verzögern, dass man an der Ampel steht
                f_bremse = m * a_noetig - f_wid
                if f_bremse < 0:
                    f_fahrer, f_bremse = -f_bremse, 0.0
            elif v > fahrer.v_bergab_max and f_wid < 0:
                f_bremse = -f_wid  # bergab Geschwindigkeit halten
            elif ziel is not None and rest < fahrer.ausroll_m and v > 3.0:
                pass  # ausrollen: weder treten noch boosten
            else:
                antrieb = True
                if strategie.nur_anfahren:
                    knopf = t_start <= strategie.dauer and strategie.v_ab <= v < fahrer.v_reise - 0.3
                else:
                    knopf = v < fahrer.v_reise - 0.3 or st >= 0.02
                knopf = knopf and boost and motor is not None and st >= 0  # bergab nie boosten
                p_fahrer = fahrer.p_anfahr if t_start <= 10.0 else fahrer.p_max
                kraft_faktor, eta_gang = rad.gang(v)
                f_fahrer_max = min(fahrer.f_max * kraft_faktor, p_fahrer * eta_gang / max(v, 1.0))
                f_motor_max = 0.0
                if knopf:
                    t_cap = strategie.t_max if strategie.t_max is not None else motor.t_max
                    p_cap = strategie.p_max if strategie.p_max is not None else motor.p_boost_max
                    f_motor_max = min(t_cap / rad.r, p_cap / max(v, 1.0))
                    u_bus = speicher.spannung(soc) if speicher is not None else None
                    if motor.kv is not None and u_bus is not None:
                        # Strom durch Gegenspannung begrenzt: I = (U - n/Kv) / R
                        n_rad = v / (2 * math.pi * rad.r) * 60
                        i_spannung = max(0.0, (0.95 * u_bus - n_rad / motor.kv) / motor.r_wicklung)
                        f_motor_max = min(f_motor_max, i_spannung * motor.kt * motor.eta_getriebe / rad.r)
                    if strategie.gleichmaessig and speicher is not None:
                        # Kraft, bei der der Speicher genau soc_beim_start / dauer liefert
                        p_ziel = soc_beim_start * 3600 / strategie.dauer * motor.eta_regler * speicher.eta
                        g = motor.eta_getriebe
                        a_q = (rad.r / (motor.kt * g)) ** 2 * motor.r_wicklung
                        f_motor_max = min(f_motor_max, (-v / g + math.sqrt((v / g) ** 2 + 4 * a_q * p_ziel)) / (2 * a_q))
                if v < fahrer.v_reise:
                    f_fahrer, f_motor = f_fahrer_max, f_motor_max
                else:  # Reisetempo halten, Motor nur am Berg
                    f_fahrer = min(max(f_wid, 0.0), f_fahrer_max)
                    f_motor = min(max(f_wid - f_fahrer, 0.0), f_motor_max)

            # ---- Boost: Energie aus dem Speicher
            if f_motor > 0 and speicher is not None:
                g = motor.eta_getriebe
                i = f_motor * rad.r / (motor.kt * g)
                p_el = (f_motor * v / g + i * i * motor.r_wicklung) / motor.eta_regler / speicher.eta
                if p_el > speicher.p_max:
                    f_motor *= speicher.p_max / p_el
                    i = f_motor * rad.r / (motor.kt * g)
                    p_el = (f_motor * v / g + i * i * motor.r_wicklung) / motor.eta_regler / speicher.eta
                if not unendlich and soc - p_el * DT / 3600 < 0:
                    f_motor, p_el = 0.0, 0.0
                soc -= p_el * DT / 3600
                e.boost_wh += p_el * DT / 3600
                if f_motor > 0:
                    e.boost_zeit_s += DT
                    i = f_motor * rad.r / (motor.kt * motor.eta_getriebe)
                    e.kupfer_boost_wh += i * i * motor.r_wicklung * DT / 3600
                e.boost_mech_wh += f_motor * v * DT / 3600
                e.p_boost_peak = max(e.p_boost_peak, p_el)
            else:
                f_motor = 0.0
            if antrieb and f_fahrer >= fahrer.f_max * rad.gang(v)[0] - 1e-9 and f_motor == 0.0 and f_wid > 0:
                e.zeit_kraftlimit_s += DT  # Fahrer am Übersetzungslimit, Motor hilft nicht

            # ---- Rekuperation: Bremshebel -> erst Motor, Rest Reibbremse
            f_rekup = 0.0
            if f_bremse > 0 and motor is not None and speicher is not None and v > motor.v_rekup_min:
                # Kraft mit max. Nettoleistung (darunter fressen Kupferverluste alles)
                g = motor.eta_getriebe
                f_opt = v * motor.kt ** 2 / (2 * rad.r ** 2 * motor.r_wicklung * g)
                f_rekup = min(f_bremse, motor.t_max / rad.r, motor.p_rekup_max / v, f_opt)
                i = f_rekup * rad.r * g / motor.kt
                p_netto = f_rekup * v * g - i * i * motor.r_wicklung
                p_in = p_netto * motor.eta_regler * speicher.eta if p_netto > 0 else 0.0
                platz = (speicher.e_nutz - soc) * 3600 / DT if not unendlich else math.inf
                grenze = min(speicher.p_max, platz)
                if p_in > grenze:
                    # Kraft, bei der genau 'grenze' im Speicher ankommt (Kupferverlust quadratisch)
                    c = (rad.r * g / motor.kt) ** 2 * motor.r_wicklung
                    pn = grenze / (motor.eta_regler * speicher.eta)
                    f_rekup = (v * g - math.sqrt(max((v * g) ** 2 - 4 * c * pn, 0.0))) / (2 * c)
                    p_in = grenze
                if p_in <= 0:
                    f_rekup = 0.0
                soc += p_in * DT / 3600
                e.rekup_wh += p_in * DT / 3600
                e.p_rekup_peak = max(e.p_rekup_peak, p_in)
            e.reibbremse_wh += (f_bremse - f_rekup) * v * DT / 3600

            # ---- Bewegung
            p_tritt = f_fahrer * v / rad.gang(v)[1]  # Fahrerleistung an der Kurbel
            e.fahrerarbeit_kj += p_tritt * DT / 1000
            if not gemessen:  # läuft gerade ein gemessener Start auf der Ebene?
                e.anfahr_fahrer_j += p_tritt * DT
                e.anfahr_motor_j += f_motor * v * DT
            a = (f_fahrer + f_motor - f_wid - f_bremse) / m
            v_neu = v + a * DT
            if ziel is not None and (rest <= 0.01 or v_neu <= 0.05 and rest < 2 or s + max(v_neu, 0.0) * DT >= ziel):
                e.reibbremse_wh += 0.5 * m * max(v_neu, 0.0) ** 2 / 3600  # Rest-Bewegungsenergie
                s, v, bremst = ziel, 0.0, False  # an der Ampel
                ampel_idx += 1
                e.fahrzeit_s += DT  # Standzeit zählt nicht zur Fahrzeit
                t_start, soc_beim_start = 0.0, soc
                gemessen = strecke.steigung(s + 1.0) != 0  # nur Starts auf der Ebene messen
                if s < strecke.laenge:
                    e.starts += 1  # die Zielampel ist kein Start mehr
                continue
            if v_neu < 0.5 and a <= 0 and f_bremse == 0:
                s += 1.1 * DT  # kommt nicht mehr hoch: absteigen und schieben (4 km/h)
                v = 0.0
                e.schiebe_m += 1.1 * DT
                e.fahrzeit_s += DT
                continue
            v = max(v_neu, 0.0)
            s += v * DT
            e.fahrzeit_s += DT
            t_start += DT
            if not gemessen and v >= 20 / 3.6:
                e.starts_flach += 1
                e.anfahrzeit_summe_s += t_start
                gemessen = True
            e.soc_min, e.soc_max = min(e.soc_min, soc), max(e.soc_max, soc)
        e.soc_ende = soc
    return e


def simuliere_stationaer(strecke: Strecke, fahrer: Fahrer, rad: Rad, motor: Motor, speicher: Speicher,
                         **kw) -> Ergebnis:
    """Eingeschwungener Zustand ohne Ladestecker: Start mit leerem Speicher, Runden wiederholen,
    bis sich der Füllstand über eine Runde nicht mehr ändert (Entnahme = Rekuperation, oder Speicher voll)."""
    soc = 0.0
    for _ in range(60):
        e = simuliere(strecke, fahrer, rad, motor, speicher, runden=1, soc_wh=soc, **kw)
        if abs(e.soc_ende - e.soc_anfang) < 0.005:
            break
        soc = e.soc_ende
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
            e = simuliere_stationaer(strecke, fahrer, r, Motor(), sp)
            print(zeile(sp.name, r.masse_ohne_speicher + sp.masse, e, ref))

        ballast = Rad(masse_ohne_speicher=Rad().masse_ohne_speicher + lto(60).masse)
        leer = simuliere(strecke, fahrer, ballast, Motor(), None, runden=1)  # ohne Speicher: kein Boost, keine Rekup
        print(zeile("Boost aus (nur Ballast + Schleppmoment)", ballast.masse_ohne_speicher, leer, ref))
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
        e = simuliere_stationaer(strecke, fahrer, rad, motor, lto(60))
        print(f"| {name} | {100 * (e.fahrerarbeit_kj / ref.fahrerarbeit_kj - 1):+.1f} % | {e.rekup_wh:.1f} | "
              f"{e.fahrzeit_s / 60:.1f} ({ref.fahrzeit_s / 60:.1f}) |")
    print()


if __name__ == "__main__":
    main()
