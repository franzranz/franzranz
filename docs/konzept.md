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
- **Netto für den Fahrer:** Arbeit −7 % bis +5 % gegenüber einem 10-kg-Singlespeed ohne Motor, je nach Motorgüte.
  Im Basisfall ±1 %. Das System bezahlt im Wesentlichen sein eigenes Gewicht und Schleppmoment.
- **Was es wirklich bringt:** Anfahren. Die Zeit, in der der Fahrer am Übersetzungslimit hängt, geht von 27–53 s auf 0.
  Fahrzeit 1–5 % kürzer. Für längere Steigungen reicht die Energie nicht: der Speicher pendelt nahe leer.
- **Speicher:** LTO 30–60 Wh reicht. Superkondensatoren sind in jeder Zeile schlechter (+2,3 kg für 15 Wh).
- **Größte Hebel:** (1) Kupferverluste des Motors bei hohem Drehmoment, (2) Schleppmoment ohne Strom, (3) Gewicht.
  Der Wirkungsgrad des Motortreibers (97–98 %) ist kein Hebel.
- Rekuperation ist im Modell eher optimistisch (gebremst wird immer, nie ausgerollt).

Alle Motorparameter sind geschätzt. Nächster Schritt: echte Kennwerte (Kt, Wicklungswiderstand, Schleppmoment)
der Kandidaten einsetzen, z. B. aus dem Motorsimulator von ebikes.ca.

## Boost nur zum Anfahren (`sim/anfahren.py`, Rohdaten in `sim-anfahren.md`)

Entscheidung: Boost nur nach Stillstand, nie am Berg. Kostet praktisch nichts, weil der Berg-Boost im Dauerbetrieb
ohnehin leer lief. Pro Ampelstopp kommen 0,28–0,43 Wh in den Speicher (75–120 kg), das ist das Budget pro Start.

Vergleich (100 kg, 300 W Antritt, getriebelose Nabe):

| Strategie | Boost-Dauer | am Rad ankommend | 0→20 km/h (ohne Motor 8,6 s) | Fahrerarbeit gesamt |
|---|---|---|---|---|
| Alles sofort, volles Moment 35 Nm | 2,8 s | 53 % | 5,0 s | ±0 % |
| Speicherinhalt gleichmäßig über 10 s | 5,5 s | 61 % | 5,0 s | −0,7 % |
| Erst ab 8 km/h, 35 Nm | 2,3 s | 64 % | 5,5 s | −1,1 % |
| Sanft 15 Nm bis Reisetempo | 6,3 s | 75 % | 6,1 s | −2,0 % |

- „Volle Power 10 s“ gibt es nicht: Die Energie einer Bremsung ist bei vollem Moment nach ~3 s verbraucht.
- „Alles sofort“ fühlt sich am stärksten an, verheizt aber die Hälfte im Motor (Kupferverluste ∝ Moment²,
  bei niedriger Drehzahl kommt kaum mechanische Leistung heraus).
- Leistungsgrenze (500 vs. 1000 W) ist beim Anfahren egal; was zählt, ist das Moment (Phasenstrom).
- Sanft dosiert spart gegenüber „alles sofort“ 1,4–2,4 Prozentpunkte Fahrerarbeit und ist 0,6–1,3 s langsamer
  auf 20 km/h. Alle Unterschiede sind klein,
  weil pro Start nur ~0,4 Wh im Spiel sind.
- Gilt für die getriebelose Nabe. Bei einer Getriebenabe ist der Nachteil von „alles sofort“ kleiner (zu prüfen).

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
