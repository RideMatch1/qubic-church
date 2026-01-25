# Anna Matrix Neural Network - Forschungszusammenfassung

**Generiert:** 2026-01-24T11:23:48.547470

---

## Übersicht

Diese Zusammenfassung fasst alle Experimente mit der Anna Matrix als neuronales Netzwerk zusammen.

### Statistiken

| Metrik | Wert |
|--------|------|
| Experimente abgeschlossen | 7 |
| Adressen getestet | 1382 |
| Stabile Attraktoren | 4 |

---

## Key Findings

### 1. CFB-Adressen werden anders klassifiziert als zufällige

**Quelle:** CFB Classifier
**Signifikanz:** SIGNIFIKANT

CFB: 27.3% Kat. A vs Random: 49.8%

### 2. POCC liegt in Kategorie A

**Quelle:** Extended CFB
**Signifikanz:** important

POCC Genesis Token Adresse wird als Kategorie A klassifiziert

### 3. 165 Bridge Seeds klassifiziert

**Quelle:** Bridge Seeds
**Signifikanz:** NICHT SIGNIFIKANT

BTC: 50.3% A, Qubic XOR: 18.2% A

### 4. Qubic XOR Seeds zeigen starke B-Tendenz

**Quelle:** Bridge Seeds
**Signifikanz:** SIGNIFIKANT

Nur 18.2% in Kategorie A (vs 50% erwartet)

### 5. Netzwerk hat genau 4 stabile Attraktoren

**Quelle:** Attractor Analysis
**Signifikanz:** important

Kat. A: 2, Kat. B: 2

### 6. Top Unterscheidungsmerkmal: input_balance

**Quelle:** Feature Analysis
**Signifikanz:** STARKE Unterscheidungsmerkmale gefunden

Effect Size (Cohen's d): 2.568

---

## Attraktoren

Das Anna Matrix Netzwerk konvergiert zu genau **4 stabilen Attraktoren**:

| Hash | Kategorie | Beschreibung |
|------|-----------|--------------|
| `33a020d0b94ce744` | A | 85+ 43- (n=274) |
| `6f0807b87bd06a73` | B | 43+ 85- (n=258) |
| `83a33a494bc9ef5d` | B | 42+ 85- (n=252) |
| `73ee64980731ccdd` | A | 85+ 42- (n=216) |

---

## Klassifikations-Ergebnisse

### CFB-Adressen vs. Zufällig

- **CFB Adressen in Kategorie A:** 27.3%
- **Zufällige Adressen in Kategorie A:** 49.8%
- **Differenz:** 22.5%
- **Fazit:** CFB-Adressen werden ANDERS klassifiziert als zufällige!

### Bridge Seeds (165)

- **Bitcoin Adressen Kategorie A:** 50.3%
- **Qubic XOR Seeds Kategorie A:** 18.2%
- **Qubic Direct Seeds Kategorie A:** 23.6%
- **Korrelation BTC ↔ Qubic:** 10.9%

---

## Unterscheidungsmerkmale

**Top Unterscheidungsmerkmal:** input_balance
**Effect Size (Cohen's d):** 2.568
**Interpretation:** STARKE Unterscheidungsmerkmale gefunden

### Top 5 Features

| Feature | A Mean | B Mean | Effect Size |
|---------|--------|--------|-------------|
| input_balance | 18.106 | -18.381 | 2.568 |
| input_neg | 54.705 | 72.912 | 2.555 |
| input_pos | 72.811 | 54.531 | 2.554 |
| hash_high_bytes | 18.203 | 13.633 | 2.553 |
| hash_low_bytes | 13.797 | 18.367 | 2.553 |

---

## Nächste Schritte

1. **3D-Visualisierung** - Integration in die /evidence Seite
2. **Live-Netzwerk-Monitoring** - Kontinuierliche Überwachung des Qubic-Netzwerks
3. **Time-Lock Countdown** - Warten auf März 2026

---

*Generiert durch das Anna Matrix Research Framework*
