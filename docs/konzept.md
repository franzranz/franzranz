# Rekuperations-Singlespeed – Konzept, Machbarkeit, Urteil (Stand 2026-10-13)

Prototyp, Einzelstück, Privatgelände (StVZO bewusst ausgeklammert). Ziel des Nutzers: **das Anfahren am Singlespeed
leichter machen, ohne Gangschaltung**. Energie nur aus Rekuperation über den Bremshebel, kein Ladestecker.

## Urteil

**Machbar: bedingt. Sinnvoll für das Ziel: nein, außer „nie laden / kein Lithium“ ist eine harte Anforderung oder
es ist ausdrücklich ein Lernprojekt.** Drei unabhängige Gutachten (Antriebsingenieur, Anwalt des Nutzerziels,
Advocatus Diaboli) kommen zum gleichen Ergebnis; alle drei setzen das Konzept auf einen der letzten beiden Plätze.

- Das System verschiebt Arbeit vom Anfahren ins Rollen. Auf flacher Strecke (Ampel alle 400 m, Fahrer 100 kg):
  **−27 % Anfahrarbeit pro Start bei +3,3 % Gesamtarbeit** (beste Nabe), −19 % bei +6,2 % (lieferbare Nabe).
  Nur wo vor Ampeln Gefälle liegen, werden es −40 bis −60 % pro Start bei etwa ±0 gesamt.
- Kosten: +4,3–5,4 kg, grob 1.000–1.600 € plus Rad, viel Elektronik- und Firmwarearbeit, ungeprüfte Motordaten,
  Wunschmotor (SX1 Regen-Mod) zeitweise nicht lieferbar.
- Pro Ampelstopp landen auf der Ebene nur 0,18–0,25 Wh im Speicher. Mehr gibt die Physik kaum her
  (Bewegungsenergie bei 115 kg und 22 km/h: 0,6 Wh).

### Rangfolge der Optionen für das Ziel „leichter anfahren“

1. **Kürzer übersetzen** (Ritzel +2–3 Zähne, 10–25 €, 0 g): gleiche Kraftentlastung wie eine Nabe (−12 bis −20 %
   Pedalkraft), Gesamtarbeit ±0. Kosten: höhere Trittfrequenz bei Reisetempo. Erster Versuch, immer.
2. **Mehrgang-Nabe** ohne Zug (Sturmey-Archer S2 Kickshift, 120 mm, netto +0,4–0,6 kg) oder Shimano Nexus 3
   (+0,9 kg, mit Zug): 27 % kürzerer Anfahrgang, Reisegang bleibt. Gesamtarbeit +2 bis +6 % (Nabenwirkungsgrad angenommen).
3. **Leichtes Singlespeed-E-Bike oder Nachrüstsatz mit Akku** (z. B. Coboc ONE 13,1–13,7 kg; Swytch-Klasse +3,5–4 kg,
   187–378 Wh): beim gleichen Mehrgewicht 60- bis 120-mal mehr Energie, hilft auch am Berg. Nachteil: Ladestecker.
4. **E-Bike mit Akku + Rekuperation + Brake-by-Wire als eigenes Projekt:** nicht neu (Stromer, BionX, Bridgestone
   Dual Drive rekuperieren über den Bremshebel), Rekuperation bringt mit Akku 3–10 %. Echtes Brake-by-Wire ohne
   hydraulische Rückfallebene ist für einen Prototyp von Laien ein Sicherheits-No-Go. Lohnt nur als Lernprojekt.
5. **Rekup-only-Singlespeed** (dieses Konzept): nur unter den oben genannten Bedingungen und nach bestandenem Vorversuch.

## Was das Konzept braucht, wenn man es trotzdem baut

| Baugruppe | Wahl | Begründung / Status |
|---|---|---|
| Motor | Vorderrad, Getriebenabe ohne Freilauf (Shengyi SX1 Front Regen-Mod, 2,95 kg) | Hinterrad unmöglich: alle rekuperationsfähigen Hinterradnaben brauchen ≥ 135 mm, Singlespeed hat 120 mm. SX1: Km² ~13, Schlepp ~11 W bei 22 km/h (Listing, nicht gemessen; unklar ob mit gesperrter Kupplung). Lieferbarkeit unklar. |
| Motor, Alternative | Grin All-Axle V3 Front (DD, 4,05 kg) | lieferbar, aber Km² 6,3 und schwerer → in jeder Rechnung schlechter |
| Motor, später | Kompakt-Getriebenaben < 2,5 kg mit Rekuperation (Sonceboz/MMT, ~2027, vermutlich OEM) | würden den Gewichtsnachteil halbieren |
| Regler | VESC (z. B. Flipsky 75100), Firmware vedderb/bldc | Modus „Current No Reverse Brake ADC2“ für Bremssensor, Rekup-Abregelung bei Überspannung eingebaut, Boost-Logik per LispBM |
| Speicher | 13 × Skeleton SCA0300 EVO in Serie, 37 → 22 V, ~2,8 Wh nutzbar, ~1,0 kg | LTO-Kleinzellen laden nur 3–5C → für ~800 W zu schwer; Superkondensator passt zum Puffer von wenigen Wh |
| Bremse Motorrad | Hydraulische Scheibe + analoger Hall-Sensor am Hebel, Rekuperation im Leerweg | Reibbremse bleibt Pflicht: Rekup fällt aus bei vollem Speicher, < ~5 km/h und Elektronikfehler |
| Boost | Speicherinhalt gleichmäßig über ~10 s abgeben, Moment auf 20 Nm deckeln | „alles sofort“ verheizt 37–45 % der entnommenen Energie im Motor; 20 Nm wegen Traktion am Vorderrad (nasse Haltelinie) |
| Gabel | Stahl oder Alu mit Rekup-tauglicher Drehmomentstütze, keine Carbongabel | gesperrte Kupplung = wechselndes Drehmoment, Grin warnt vor Achsbruch |

### Ungelöste technische Risiken

- **Kaltstart / leerer Speicher:** VESC braucht ≥ 14 V. Bei leerem Kondensator ist der Regler aus, und die
  Body-Dioden richten die Motorspannung gleich → ungeregeltes Bremsen des Vorderrads. Lösung (z. B. Hilfsakku oder
  Trennschalter) widerspricht teilweise „kein Akku“.
- **Eigenverbrauch:** Regler und Sensorik 1–3 W kosten 3–9 Prozentpunkte der Anfahrentlastung; ~60 mA Ruhestrom leeren
  das Spannungsfenster in ~2 h.
- **Fehlerfall:** kurzgeschlossener MOSFET bremst das Vorderrad kräftig.
- **Schleppmoment:** entscheidet über Plus oder Minus (Schlepp × 2 ≈ +4–6 Prozentpunkte), ist aber nicht gemessen.

## Vorversuch mit Abbruchkriterien (bevor Zielmotor und Speicher gekauft werden)

Stufe 0 – fast kostenlos, 2 Wochen:
1. **Strecke loggen** (Handy-GPS, 3 typische Fahrten). Abbruch von A, wenn < 1,5 aktiv gebremste Stopps pro km aus
   ≥ 15 km/h und kaum Ampeln nach Gefällen.
2. **Ritzel +2–3 Zähne.** Ist das Anfahren danach „leicht genug“ (≥ 7/10) und die Trittfrequenz bei Reisetempo
   ≤ 90/min akzeptabel → Problem gelöst, Projekt beendet.
3. **4,5 kg Ballast an der Gabel** 2 Wochen fahren und tragen. Inakzeptabel → A und C beendet.

Stufe 1 – Funktionsmuster, 300–500 €, Teile für Option 3 weiter nutzbar (gebrauchtes Vorderrad mit Nabenmotor,
VESC 75100, kleiner Li-Ion-Akku als Speicher-Ersatz, analoger Daumenhebel, Hall-Bremssensor, Drehmomentstütze):
- K1 Rekuperation: ≥ 0,15 Wh pro Stopp aus 22 km/h auf der Ebene (Modell 0,18–0,25).
- K2 Schleppmoment: Abbruch bei > 15 W bei 22 km/h (Auslauftest gegen normales Laufrad); Ziel ≤ 6–8 W.
- K3 Spürbarkeit (entscheidend): Boost per LispBM auf den Ertrag des letzten Stopps begrenzt, je 10 Starts mit/ohne
  in zufälliger Reihenfolge bei gleicher, bequemer Anstrengung. Abbruch, wenn 0→20 km/h nicht ≥ 1,5 s schneller wird.
- K4 Traktion: 10 Starts auf nasser Haltelinie/Pflaster mit 20 Nm ohne Durchdrehen.
- K5 Eigenverbrauch ≤ 2 W, Kaltstart ohne Hilfsbatterie gelöst.
- K6 Bremsmischung: ruckfrei nach ≤ 20–40 Arbeitsstunden, kein Aussetzer in 20 Testbremsungen.
- K7 Rahmen: Rad hochgerechnet ≤ 15,0 kg, Prototypkosten ≤ 1.600 €, K1–K3 nach 500 € und 4 Wochenenden gemessen.

## Belege und Rechnung

- Simulation: `sim/energiebilanz.py` (Modell), `sim/anfahren.py` (Boost-Strategien), `sim/machbarkeit.py`
  (echte Motoren, Ampelabstand, Ausrollen, Alternativen). Ergebnisse in `sim-ergebnis.md`, `sim-anfahren.md`,
  `sim-machbarkeit.md`. Energieerhaltung je Runde < 1 % Fehler; externer Code-Review ohne kritische Befunde.
- Modellgrenzen: Fahrer tritt immer mit voller Kraft (Motor macht schneller, nicht leichter; „s am Kraftlimit = 0“
  ist dadurch geschönt), keine Trittfrequenz-Kosten (bevorzugt kürzere Übersetzung leicht), Traktion nicht modelliert,
  Nabenwirkungsgrade angenommen, Motordaten nur aus Grin-Listings (Suchmaschinen-Snippets), synthetische Strecke.
- Stand der Technik: Pi-Pop (Superkondensator, kein Akku, 18–21,7 kg, Tests ~5/10), Anod Hybrid (Boost-Knopf,
  Gen 2 mit 216 Wh und Ladung), Zehus/Fixie Inc. Backspin (Singlespeed 13,3–13,5 kg mit Akku), Stromer/BionX/
  Bridgestone (Rekuperation über Bremshebel). Stufenloses analoges Brake-Blending: nur Patente, kein Serienrad.
