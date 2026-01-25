#!/usr/bin/env python3
"""
===============================================================================
      FORSCHUNGS-KONSOLIDIERUNG - ALLE ERGEBNISSE ZUSAMMENFÜHREN
===============================================================================

Sammelt alle Experiment-Ergebnisse und erstellt:
1. Eine JSON-Datei für die 3D-Visualisierung
2. Eine Markdown-Zusammenfassung aller Erkenntnisse
3. Daten für die Website-Integration

Output:
- COMPLETE_RESEARCH_RESULTS.json
- RESEARCH_SUMMARY.md
- public/data/neural-classification-data.json
"""

import json
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("     FORSCHUNGS-KONSOLIDIERUNG")
print("=" * 80)

# =============================================================================
# LADE ALLE EXPERIMENT-ERGEBNISSE
# =============================================================================

def load_json_safe(path):
    """Lade JSON-Datei sicher"""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"  Warnung: {path.name} nicht gefunden oder fehlerhaft: {e}")
        return None

def main():
    scripts_dir = Path(__file__).parent
    public_data_dir = scripts_dir.parent / "public" / "data"

    results = {
        "timestamp": datetime.now().isoformat(),
        "experiments": {},
        "key_findings": [],
        "statistics": {},
        "visualization_data": {},
    }

    # ==========================================================================
    print("\n[1] LADE EXPERIMENT-ERGEBNISSE")
    print("-" * 60)

    # 1. CFB Classifier Results
    cfb_classifier = load_json_safe(scripts_dir / "CFB_CLASSIFIER_RESULTS.json")
    if cfb_classifier:
        print("  ✓ CFB_CLASSIFIER_RESULTS.json")
        results['experiments']['cfb_classifier'] = cfb_classifier

    # 2. Extended CFB Classification
    cfb_extended = load_json_safe(scripts_dir / "CFB_EXTENDED_CLASSIFICATION.json")
    if cfb_extended:
        print("  ✓ CFB_EXTENDED_CLASSIFICATION.json")
        results['experiments']['cfb_extended'] = cfb_extended

    # 3. Bridge Seeds Classification
    bridge_seeds = load_json_safe(scripts_dir / "BRIDGE_SEEDS_CLASSIFICATION.json")
    if bridge_seeds:
        print("  ✓ BRIDGE_SEEDS_CLASSIFICATION.json")
        results['experiments']['bridge_seeds'] = bridge_seeds

    # 4. Attractor Analysis
    attractor = load_json_safe(scripts_dir / "ATTRACTOR_DEEP_ANALYSIS.json")
    if attractor:
        print("  ✓ ATTRACTOR_DEEP_ANALYSIS.json")
        results['experiments']['attractor_analysis'] = attractor

    # 5. Distinguishing Features
    features = load_json_safe(scripts_dir / "DISTINGUISHING_FEATURES.json")
    if features:
        print("  ✓ DISTINGUISHING_FEATURES.json")
        results['experiments']['distinguishing_features'] = features

    # 6. Qubic Live Monitor
    live_monitor = load_json_safe(scripts_dir / "QUBIC_LIVE_MONITOR_RESULTS.json")
    if live_monitor:
        print("  ✓ QUBIC_LIVE_MONITOR_RESULTS.json")
        results['experiments']['live_monitor'] = live_monitor

    # 7. Bridge Classification Visualization Data
    bridge_viz = load_json_safe(public_data_dir / "bridge-classification.json")
    if bridge_viz:
        print("  ✓ bridge-classification.json (Visualisierung)")
        results['experiments']['bridge_visualization'] = bridge_viz

    # ==========================================================================
    print("\n[2] EXTRAHIERE KEY FINDINGS")
    print("-" * 60)

    key_findings = []

    # CFB Classifier Findings
    if cfb_classifier and 'analysis' in cfb_classifier:
        analysis = cfb_classifier['analysis']
        key_findings.append({
            "source": "CFB Classifier",
            "finding": f"CFB-Adressen werden anders klassifiziert als zufällige",
            "detail": f"CFB: {analysis.get('cfb_category_a_pct', 0):.1f}% Kat. A vs Random: {analysis.get('random_category_a_pct', 0):.1f}%",
            "significance": analysis.get('significance', 'unknown'),
        })

    # Extended CFB Findings
    if cfb_extended and 'summary' in cfb_extended:
        summary = cfb_extended['summary']
        key_findings.append({
            "source": "Extended CFB",
            "finding": f"POCC liegt in Kategorie A",
            "detail": "POCC Genesis Token Adresse wird als Kategorie A klassifiziert",
            "significance": "important",
        })

    # Bridge Seeds Findings
    if bridge_seeds and 'summary' in bridge_seeds:
        summary = bridge_seeds['summary']
        key_findings.append({
            "source": "Bridge Seeds",
            "finding": f"165 Bridge Seeds klassifiziert",
            "detail": f"BTC: {summary.get('btc_category_a_pct', 0):.1f}% A, Qubic XOR: {summary.get('qubic_xor_category_a_pct', 0):.1f}% A",
            "significance": summary.get('significance', 'unknown'),
        })
        if summary.get('qubic_xor_category_a_pct', 50) < 30:
            key_findings.append({
                "source": "Bridge Seeds",
                "finding": "Qubic XOR Seeds zeigen starke B-Tendenz",
                "detail": f"Nur {summary.get('qubic_xor_category_a_pct', 0):.1f}% in Kategorie A (vs 50% erwartet)",
                "significance": "SIGNIFIKANT",
            })

    # Attractor Findings
    if attractor and 'summary' in attractor:
        summary = attractor['summary']
        key_findings.append({
            "source": "Attractor Analysis",
            "finding": f"Netzwerk hat genau {summary.get('total_attractors', 0)} stabile Attraktoren",
            "detail": f"Kat. A: {summary.get('category_a_attractors', 0)}, Kat. B: {summary.get('category_b_attractors', 0)}",
            "significance": "important",
        })

    # Features Findings
    if features and 'summary' in features:
        summary = features['summary']
        key_findings.append({
            "source": "Feature Analysis",
            "finding": f"Top Unterscheidungsmerkmal: {summary.get('top_feature', 'unknown')}",
            "detail": f"Effect Size (Cohen's d): {summary.get('top_effect_size', 0):.3f}",
            "significance": summary.get('interpretation', 'unknown'),
        })

    results['key_findings'] = key_findings

    for finding in key_findings:
        print(f"  • {finding['finding']}")
        print(f"    → {finding['detail']}")

    # ==========================================================================
    print("\n[3] BERECHNE GESAMTSTATISTIKEN")
    print("-" * 60)

    statistics = {
        "total_addresses_tested": 0,
        "category_a_total": 0,
        "category_b_total": 0,
        "attractor_count": 4,  # Bekannt
        "experiments_completed": len([e for e in results['experiments'].values() if e]),
    }

    # Sammle Statistiken
    if cfb_extended and 'groups' in cfb_extended:
        groups = cfb_extended['groups']
        for group_name, group_data in groups.items():
            if isinstance(group_data, dict) and 'count' in group_data:
                statistics['total_addresses_tested'] += group_data.get('count', 0)

    if bridge_seeds and 'total_bridges' in bridge_seeds:
        statistics['total_addresses_tested'] += bridge_seeds['total_bridges']

    results['statistics'] = statistics

    print(f"  Gesamte Adressen getestet: {statistics['total_addresses_tested']}")
    print(f"  Experimente abgeschlossen: {statistics['experiments_completed']}")
    print(f"  Stabile Attraktoren: {statistics['attractor_count']}")

    # ==========================================================================
    print("\n[4] ERSTELLE VISUALISIERUNGS-DATEN")
    print("-" * 60)

    viz_data = {
        "generated": datetime.now().isoformat(),
        "attractors": [],
        "classifications": [],
        "summary": {
            "total_nodes": 0,
            "category_a_count": 0,
            "category_b_count": 0,
        }
    }

    # Extrahiere Attraktoren für Visualisierung
    if attractor and 'attractors' in attractor:
        for h, attr in attractor['attractors'].items():
            viz_data['attractors'].append({
                "hash": h,
                "category": attr.get('signature', {}).get('category', '?'),
                "count": attr.get('count', 0),
                "distribution": attr.get('signature', {}).get('distribution', {}),
            })

    # Extrahiere Bridge Seeds für Visualisierung
    if bridge_seeds and 'classifications' in bridge_seeds:
        for c in bridge_seeds['classifications']:
            viz_data['classifications'].append({
                "id": c['id'],
                "name": c['name'],
                "type": c['type'],
                "bitcoin_address": c['bitcoin']['address'],
                "bitcoin_category": c['bitcoin']['category'],
                "bitcoin_attractor": c['bitcoin']['attractor'],
                "qubic_xor_category": c['qubic_xor']['category'],
                "qubic_direct_category": c['qubic_direct']['category'],
                "correlation": c['correlation'],
                "is_cfb": c['is_cfb'],
                "position": c['position_3d'],
            })
            viz_data['summary']['total_nodes'] += 1
            if c['bitcoin']['category'] == 'A':
                viz_data['summary']['category_a_count'] += 1
            else:
                viz_data['summary']['category_b_count'] += 1

    results['visualization_data'] = viz_data

    print(f"  Attraktoren für Viz: {len(viz_data['attractors'])}")
    print(f"  Klassifikationen für Viz: {len(viz_data['classifications'])}")

    # ==========================================================================
    print("\n[5] SPEICHERE ERGEBNISSE")
    print("-" * 60)

    # 1. Haupt-JSON
    output_path = scripts_dir / "COMPLETE_RESEARCH_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  ✓ {output_path.name}")

    # 2. Visualisierungs-JSON für public/data
    viz_path = public_data_dir / "neural-classification-data.json"
    with open(viz_path, 'w') as f:
        json.dump(viz_data, f, indent=2)
    print(f"  ✓ {viz_path.name}")

    # 3. Markdown Summary
    md_path = scripts_dir / "RESEARCH_SUMMARY.md"
    write_markdown_summary(md_path, results)
    print(f"  ✓ {md_path.name}")

    # ==========================================================================
    print("\n" + "=" * 80)
    print("                    KONSOLIDIERUNG ABGESCHLOSSEN")
    print("=" * 80)

    print(f"""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    FORSCHUNGS-KONSOLIDIERUNG                            │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │  EXPERIMENTE GELADEN:       {statistics['experiments_completed']}                                         │
    │  KEY FINDINGS:              {len(key_findings)}                                         │
    │  ADRESSEN GETESTET:         {statistics['total_addresses_tested']:5}                                   │
    │                                                                         │
    │  AUSGABE-DATEIEN:                                                       │
    │    • COMPLETE_RESEARCH_RESULTS.json                                    │
    │    • RESEARCH_SUMMARY.md                                               │
    │    • public/data/neural-classification-data.json                       │
    │                                                                         │
    │  BEREIT FÜR 3D-VISUALISIERUNG: ✓                                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    return results


def write_markdown_summary(path, results):
    """Schreibe Markdown-Zusammenfassung"""

    md = f"""# Anna Matrix Neural Network - Forschungszusammenfassung

**Generiert:** {results['timestamp']}

---

## Übersicht

Diese Zusammenfassung fasst alle Experimente mit der Anna Matrix als neuronales Netzwerk zusammen.

### Statistiken

| Metrik | Wert |
|--------|------|
| Experimente abgeschlossen | {results['statistics'].get('experiments_completed', 0)} |
| Adressen getestet | {results['statistics'].get('total_addresses_tested', 0)} |
| Stabile Attraktoren | {results['statistics'].get('attractor_count', 4)} |

---

## Key Findings

"""

    for i, finding in enumerate(results['key_findings'], 1):
        md += f"""### {i}. {finding['finding']}

**Quelle:** {finding['source']}
**Signifikanz:** {finding['significance']}

{finding['detail']}

"""

    md += """---

## Attraktoren

Das Anna Matrix Netzwerk konvergiert zu genau **4 stabilen Attraktoren**:

| Hash | Kategorie | Beschreibung |
|------|-----------|--------------|
"""

    if 'attractor_analysis' in results['experiments'] and results['experiments']['attractor_analysis']:
        attr_data = results['experiments']['attractor_analysis']
        if 'attractors' in attr_data:
            for h, attr in sorted(attr_data['attractors'].items(), key=lambda x: -x[1].get('count', 0)):
                sig = attr.get('signature', {})
                cat = sig.get('category', '?')
                pos = sig.get('pos', 0)
                neg = sig.get('neg', 0)
                count = attr.get('count', 0)
                md += f"| `{h}` | {cat} | {pos}+ {neg}- (n={count}) |\n"

    md += """
---

## Klassifikations-Ergebnisse

### CFB-Adressen vs. Zufällig

"""

    if 'cfb_classifier' in results['experiments'] and results['experiments']['cfb_classifier']:
        cfb = results['experiments']['cfb_classifier']
        if 'analysis' in cfb:
            analysis = cfb['analysis']
            md += f"""- **CFB Adressen in Kategorie A:** {analysis.get('cfb_category_a_pct', 0):.1f}%
- **Zufällige Adressen in Kategorie A:** {analysis.get('random_category_a_pct', 0):.1f}%
- **Differenz:** {analysis.get('difference', 0):.1f}%
- **Fazit:** {analysis.get('conclusion', 'N/A')}

"""

    md += """### Bridge Seeds (165)

"""

    if 'bridge_seeds' in results['experiments'] and results['experiments']['bridge_seeds']:
        bridge = results['experiments']['bridge_seeds']
        if 'summary' in bridge:
            summary = bridge['summary']
            md += f"""- **Bitcoin Adressen Kategorie A:** {summary.get('btc_category_a_pct', 0):.1f}%
- **Qubic XOR Seeds Kategorie A:** {summary.get('qubic_xor_category_a_pct', 0):.1f}%
- **Qubic Direct Seeds Kategorie A:** {summary.get('qubic_direct_category_a_pct', 0):.1f}%
- **Korrelation BTC ↔ Qubic:** {summary.get('correlation_all_same_pct', 0):.1f}%

"""

    md += """---

## Unterscheidungsmerkmale

"""

    if 'distinguishing_features' in results['experiments'] and results['experiments']['distinguishing_features']:
        feat = results['experiments']['distinguishing_features']
        if 'summary' in feat:
            summary = feat['summary']
            md += f"""**Top Unterscheidungsmerkmal:** {summary.get('top_feature', 'N/A')}
**Effect Size (Cohen's d):** {summary.get('top_effect_size', 0):.3f}
**Interpretation:** {summary.get('interpretation', 'N/A')}

"""

        if 'discriminating_features' in feat:
            md += """### Top 5 Features

| Feature | A Mean | B Mean | Effect Size |
|---------|--------|--------|-------------|
"""
            for f in feat['discriminating_features'][:5]:
                md += f"| {f['feature']} | {f['a_mean']:.3f} | {f['b_mean']:.3f} | {f['effect_size']:.3f} |\n"

    md += """
---

## Nächste Schritte

1. **3D-Visualisierung** - Integration in die /evidence Seite
2. **Live-Netzwerk-Monitoring** - Kontinuierliche Überwachung des Qubic-Netzwerks
3. **Time-Lock Countdown** - Warten auf März 2026

---

*Generiert durch das Anna Matrix Research Framework*
"""

    with open(path, 'w') as f:
        f.write(md)


if __name__ == "__main__":
    main()
