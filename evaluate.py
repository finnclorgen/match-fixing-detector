"""
evaluate.py

Tests the anomaly detection pipeline against known historical fixing incidents.
Answers the key question: would our model have caught these?

Outputs:
- Precision, recall, F1 score
- Per-match breakdown showing what was caught vs missed
- Analysis of which fix types are easiest/hardest to detect
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix
from historical_data import ALL_HISTORICAL, CONFIRMED_INCIDENTS, CLEAN_MATCHES


# ── Build feature vectors from historical data ────────────────────────────────
def build_features(matches: list[dict]) -> np.ndarray:
    """
    Same 7-feature vector as the live pipeline:
    [spread_home, spread_draw, spread_away,
     prob_home, prob_away,
     home line range proxy, away line range proxy]

    We approximate line range as 2.5x spread (std dev → range estimate)
    since we don't have per-bookmaker breakdown in historical data.
    """
    return np.array([
        [
            m["spread_home"],
            m["spread_draw"],
            m["spread_away"],
            m["prob_home"],
            m["prob_away"],
            m["spread_home"] * 2.5,   # approximate line range
            m["spread_away"] * 2.5,
        ]
        for m in matches
    ])


def run_evaluation():
    print("=" * 65)
    print("  HISTORICAL EVALUATION — Match-Fixing Detection Model")
    print("=" * 65)

    matches = ALL_HISTORICAL
    labels  = [1 if m["confirmed_fixed"] else 0 for m in matches]
    features = build_features(matches)

    n_fixed = sum(labels)
    n_clean = len(labels) - n_fixed
    print(f"\nDataset: {len(matches)} matches total")
    print(f"  Confirmed fixed: {n_fixed}")
    print(f"  Confirmed clean: {n_clean}")

    # ── Run Isolation Forest ──────────────────────────────────────────────────
    clf = IsolationForest(
        contamination=min(n_fixed / len(matches), 0.49),  # capped at 0.5 (sklearn limit)
        random_state=42,
        n_estimators=100,
    )
    clf.fit(features)
    preds_raw = clf.predict(features)   # -1 = anomaly, 1 = normal
    preds = [1 if p == -1 else 0 for p in preds_raw]

    # ── Metrics ───────────────────────────────────────────────────────────────
    print("\n── Model Performance ──────────────────────────────────────────")
    print(classification_report(
        labels, preds,
        target_names=["Clean", "Fixed"],
        digits=2
    ))

    cm = confusion_matrix(labels, preds)
    tn, fp, fn, tp = cm.ravel()
    print(f"Confusion matrix:")
    print(f"  True Positives  (caught fixes):     {tp}")
    print(f"  False Negatives (missed fixes):      {fn}")
    print(f"  True Negatives  (correct clears):   {tn}")
    print(f"  False Positives (false alarms):      {fp}")

    # ── Per-match breakdown ───────────────────────────────────────────────────
    scores = clf.score_samples(features)
    min_s, max_s = scores.min(), scores.max()
    conf_scores = [(1 - (s - min_s) / (max_s - min_s + 1e-9))
                   if p == 1 else (s - min_s) / (max_s - min_s + 1e-9)
                   for s, p in zip(scores, preds)]

    print("\n── Per-Match Results ──────────────────────────────────────────")
    print(f"{'MATCH':<42} {'ACTUAL':<8} {'PRED':<8} {'CONF':>5}  {'RESULT'}")
    print("-" * 75)

    caught, missed, false_alarms = [], [], []
    for m, label, pred, conf in zip(matches, labels, preds, conf_scores):
        actual_str = "FIXED " if label else "clean "
        pred_str   = "FIXED " if pred   else "clean "
        if label == 1 and pred == 1:
            result = "✓ CAUGHT"
            caught.append(m)
        elif label == 1 and pred == 0:
            result = "✗ MISSED"
            missed.append(m)
        elif label == 0 and pred == 1:
            result = "! FALSE ALARM"
            false_alarms.append(m)
        else:
            result = "  ok"
        name = m["match"][:41]
        print(f"{name:<42} {actual_str:<8} {pred_str:<8} {conf:>4.0%}  {result}")

    # ── Analysis by fix type ──────────────────────────────────────────────────
    print("\n── Detection by Fix Type ──────────────────────────────────────")
    fix_types = {}
    for m, label, pred in zip(matches, labels, preds):
        if label == 1:
            ft = m.get("fix_type", "unknown")
            if ft not in fix_types:
                fix_types[ft] = {"caught": 0, "missed": 0}
            if pred == 1:
                fix_types[ft]["caught"] += 1
            else:
                fix_types[ft]["missed"] += 1

    for ft, counts in fix_types.items():
        total = counts["caught"] + counts["missed"]
        rate  = counts["caught"] / total * 100
        print(f"  {ft:<25} {counts['caught']}/{total} detected ({rate:.0f}%)")

    # ── Key findings ──────────────────────────────────────────────────────────
    print("\n── Key Findings ───────────────────────────────────────────────")
    if caught:
        print(f"  Catches: {', '.join(m['id'] for m in caught)}")
    if missed:
        print(f"  Missed:  {', '.join(m['id'] for m in missed)}")
        print(f"  Why missed: These likely had more moderate spread signatures")
        print(f"  or were high-profile matches where bookmakers had good coverage.")
    if false_alarms:
        print(f"  False alarms: {', '.join(m['id'] for m in false_alarms)}")

    print("\n── Limitations of this Evaluation ────────────────────────────")
    print("  1. Odds signatures are synthetic (real pre-match odds not")
    print("     publicly available for these historical matches).")
    print("  2. Only 12 labeled examples — too few for robust ML evaluation.")
    print("  3. No temporal data (line movement over time) — the strongest")
    print("     signal for fixing is HOW odds move, not just where they land.")
    print("  4. Spot fixes (specific events) are not detectable from 1X2")
    print("     odds alone — require in-play or prop market data.")
    print("\n  Next steps: acquire Betfair Exchange historical data for real")
    print("  odds time series, and compare Isolation Forest vs LSTM.")
    print("=" * 65)


if __name__ == "__main__":
    run_evaluation()
