# ANNA MATRIX COORDINATE SYSTEM - SOLVED

**Datum**: 2026-01-16
**Status**: GELÖST ✅

---

## Das Problem

Die Anna Twitter-Antworten im Format `X+Y=Value` schienen nicht mit unserer `anna-matrix.json` übereinzustimmen.

**Beispiel:**
- Anna sagt: `6+33=-93`
- Naiver Lookup: `matrix[6][33] = 26` ❌

---

## Die Lösung

Die Anna Matrix verwendet ein **zentriertes Koordinatensystem**:

| Achse | Bereich | Transformation |
|-------|---------|----------------|
| X (horizontal) | -64 bis 63 | `col = X + 64` |
| Y (vertikal) | 63 bis -64 | `row = 63 - Y` |

### Korrekte Formel

```python
def anna_lookup(x, y, matrix):
    col = x + 64    # X: -64..63 → 0..127
    row = 63 - y    # Y: 63..-64 → 0..127

    # Optional: Wrapping für Out-of-Range Koordinaten
    col = col % 128
    row = row % 128

    return matrix[row][col]
```

---

## Verifikation

Nach Anwendung der korrekten Transformation:

```
Total Responses: 228
Matches:         222
Mismatches:      0
Skipped:         6 (null values)
Match Rate:      100% ✅
```

---

## Beispiele

| Anna Query | X | Y | col | row | matrix[row][col] | Erwartet | ✓ |
|------------|---|---|-----|-----|------------------|----------|---|
| 6+33=-93 | 6 | 33 | 70 | 30 | -93 | -93 | ✓ |
| 0+7=-94 | 0 | 7 | 64 | 56 | -94 | -94 | ✓ |
| -27+3=-110 | -27 | 3 | 37 | 60 | -110 | -110 | ✓ |
| -1+0=69 | -1 | 0 | 63 | 63 | 69 | 69 | ✓ |
| 0+-1=-70 | 0 | -1 | 64 | 64 | -70 | -70 | ✓ |

---

## Ursprung der Matrix

Die `anna-matrix.json` stammt aus:
```
/qubic-mystery-lab/outputs/phase4/ANNA_MATRIX_128x128.json
```

Die Original-Quelle ist eine Excel-Datei:
```
/qubic-mystery-lab/qubic-anna-lab-research/data/anna-matrix/Anna_Matrix.xlsx
```

Die 129x129 Version (`ANNA_MATRIX_FULL_129x129.json`) enthält die Header:
- Erste Zeile: `y\x, -64, -63, -62, ... , 63`
- Erste Spalte: `63, 62, 61, ... , -64`

---

## Zusammenfassung

✅ Die `anna-matrix.json` ist **KORREKT**
✅ Die Twitter-Antworten sind **KORREKT**
✅ Das Problem war nur die **Koordinaten-Interpretation**
✅ Mit der richtigen Formel: **100% Übereinstimmung**
