# Rekuperations-Singlespeed – Konzept & Lastenheft (Stand 2026-10-13)

Prototyp, Einzelstück, nur Privatgelände. StVZO/Pedelec-Regeln bewusst ausgeklammert.

## Festgelegt

| Punkt | Entscheidung |
|---|---|
| Einsatz | Stadt, mäßige Steigungen, viele Ampeln |
| Fahrergewicht | beliebig, Auslegung bis 120 kg |
| Radgewicht | Ziel < 14–15 kg |
| Antrieb | Singlespeed, Alu-Rahmen, keine Schaltung |
| Motor | Nabenmotor mit Rekuperation, vorne oder hinten offen |
| Boost | Knopf/Daumenhebel, Motor zieht auch ohne Treten |
| Laden | **nur** über den Bremshebel am Motorrad, kein Stecker, kein generatives Treten |
| Bremse Motorrad | Hebel mit Analogsensor: erst Rekuperation, dann hydraulische Scheibe am selben Rad |
| Bremse anderes Rad | normale Hydraulik-Scheibe |
| Speicher | technologieoffen → Ergebnis: **LTO** (siehe unten) |
| Winter | vorerst egal |

Die Reibbremse am Motorrad ist kein Rechtsthema, sondern Physik: Rekuperation liefert keine Bremskraft bei vollem Speicher,
unter ~4 km/h (Kupferverluste fressen alles), über dem Motor-Drehmomentlimit und bei Elektronikfehler.

## Simulationsergebnis (`sim/energiebilanz.py`, Rohdaten in `sim-ergebnis.md`)

Synthetische Stadtstrecke: 8 km, 20 Ampeln, 42 Hm hoch und wieder runter. Eingeschwungener Zustand
(nie eingesteckt → Boost kann nur verbrauchen, was die Bremse vorher geladen hat).

- **Ertrag:** 6–9 Wh pro 8 km, also ~1 Wh/km. Ein freier Boost würde 22–36 Wh wollen → Rekuperation deckt ~25 %.
- **Netto für den Fahrer:** Arbeit −6 % bis +5 % gegenüber einem 10-kg-Singlespeed ohne Motor, je nach Motorgüte.
  Im Basisfall ±0. Das System bezahlt im Wesentlichen sein eigenes Gewicht und Schleppmoment.
- **Was es wirklich bringt:** Anfahren. Die Zeit, in der der Fahrer am Übersetzungslimit hängt, geht von 30–56 s auf 0.
  Fahrzeit 0,5–5 % kürzer. Für längere Steigungen reicht die Energie nicht: der Speicher pendelt nahe leer.
- **Speicher:** LTO 30–60 Wh reicht. Superkondensatoren sind in jeder Zeile schlechter (+2,3 kg für 15 Wh).
- **Größte Hebel:** (1) Kupferverluste des Motors bei hohem Drehmoment, (2) Schleppmoment ohne Strom, (3) Gewicht.
  Der Wirkungsgrad des Motortreibers (97–98 %) ist kein Hebel.
- Rekuperation ist im Modell eher optimistisch (gebremst wird immer, nie ausgerollt).

Alle Motorparameter sind geschätzt. Nächster Schritt: echte Kennwerte (Kt, Wicklungswiderstand, Schleppmoment)
der Kandidaten einsetzen, z. B. aus dem Motorsimulator von ebikes.ca.

## Komponenten-Shortlist

| Baugruppe | Favorit | Alternative | Status |
|---|---|---|---|
| Motor | Grin GMAC, hinten, Getriebe ohne Freilauf, rekuperationsfähig, ~3,8 kg | Grin All-Axle DD vorne, ~4,05 kg, Steckachse | Kennwerte fehlen; Entscheidung nach Simulation mit echten Daten |
| Motor (später) | Sonceboz/MMT/eBikeLabs Kompakt-Getriebenabe, < 2,5 kg, 70 Nm, Rekup | – | angekündigt für ~2027, vermutlich nur OEM |
| Regler | VESC-Hardware (z. B. Flipsky 75100) mit Firmware vedderb/bldc, Modus „Current No Reverse Brake ADC2“ | EBiCS-Firmware auf Lishui-Regler | Modus in Foren mehrfach genutzt, Wizard-Bugs bekannt |
| Speicher | LTO, ~16s (≈38 V), 30–60 Wh, ≥10C Ladestrom, ~0,4–0,8 kg | – | passende kleine Zellen (1,3–2 Ah, hohe Rate) noch zu finden |
| BMS | LTO-fähig (Zellspannung 1,5–2,8 V), mit Balancer | vesc_bms_fw | LTO-Support noch prüfen |
| Bremssensor | linearer Hall-Sensor + Magnet am Hebel (analog!) | Drucksensor in der Hydraulikleitung | Schaltsensoren (an/aus) ungeeignet: Rekup 0/100 % ruckt |
| Boost | Daumenhebel analog auf ADC1 | Taster mit Rampe in Firmware | Taster mit 500 W Sprung = Schlupf + Kupferverluste |
| Bremsen | 2× Hydraulik-Scheibe | – | – |

## Gewichtsbudget (Schätzung)

Leichtes Alu-Singlespeed mit Hydraulik-Scheiben ~9,5 kg, Nabenmotor +3,9 kg (gegenüber normaler Nabe),
Regler 0,2 kg, Kabel/Sensoren/Hebel 0,3 kg, LTO 0,4–0,8 kg → **≈ 14,3–14,7 kg**.
Unter 14 kg geht mit heute frei kaufbaren Nabenmotoren kaum (Vergleich: Fixie Inc. Backspin mit Zehus-Nabe 13,3 kg,
aber geschlossenes System mit 172-Wh-Akku und Ladebuchse).

## Offene Punkte

- Vorne/hinten: hängt an Kupferverlusten und Schleppmoment GMAC vs. All-Axle.
- Bremsverzögerung, die die Rekuperation allein abdecken soll.
- Boost-Strategie: jeder Ampelstart oder Energie für Steigungen sparen?
- Konkrete LTO-Zelle und BMS.
- Was der Unterschied zu Pi-Pop und Zehus/Fixie Inc. sein soll.
