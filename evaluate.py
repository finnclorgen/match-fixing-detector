"""
evaluate.py

Ranking-based evaluation of the match-fixing detection pipeline.

Reframes the task as retrieval rather than binary classification.
With only 7 labeled positives, precision/recall at a fixed threshold
is unreliable (flips with a single mis-classified match). Ranking
metrics measure what actually matters: are confirmed fixes near the
top of the suspicious list?

Metrics
-------
  ROC-AUC          P(fix ranked above clean for a random pair)
  Avg Precision    Area under the precision-recall curve
  NDCG@K           Quality of top-K results, with log-position discount
  Recall@K         Fraction of all fixes found in the top-K

Two datasets
------------
  Original  (12 matches: 7 fixed, 5 clean) — honest but low-sample
  Augmented (+35 synthetic variants)        — more stable estimates

Two scorers
-----------
  Isolation Forest  — the main unsupervised model
  Spread-rule       — rank by max(spread_home, spread_away); interpretable
                      single-feature baseline that requires no model
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, average_precision_score
from historical_data import CONFIRMED_INCIDENTS, CLEAN_MATCHES, augment_incidents


# ── Feature extraction ────────────────────────────────────────────────────────

def build_features(matches: list[dict]) -> np.ndarray:
    """Same 7-feature vector as the live pipeline."""
    return np.array([
        [
            m["spread_home"],
            m["spread_draw"],
            m["spread_away"],
            m["prob_home"],
            m["prob_away"],
            m["spread_home"] * 2.5,   # approximate line range proxy
            m["spread_away"] * 2.5,
        ]
        for m in matches
    ])


# ── Ranking metrics ───────────────────────────────────────────────────────────

def ndcg_at_k(labels: list[int], scores, k: int) -> float:
    """
    NDCG@K — measures whether positives appear near the top.

    DCG@K  = Σ rel_i / log2(i+1)  for i in 1..K
    NDCG@K = DCG@K / IDCG@K       (IDCG = ideal ordering)
    """
    order  = np.argsort(scores)[::-1]
    ranked = np.array(labels, dtype=float)[order[:k]]
    ideal  = sorted(ranked, reverse=True)

    def dcg(rels):
        return sum(r / np.log2(i + 2) for i, r in enumerate(rels))

    idcg = dcg(ideal)
    return float(dcg(ranked) / idcg) if idcg > 0 else 0.0


def recall_at_k(labels: list[int], scores, k: int) -> float:
    order = np.argsort(scores)[::-1]
    top_k = np.array(labels)[order[:k]]
    n_pos = sum(labels)
    return float(top_k.sum() / n_pos) if n_pos > 0 else 0.0


# ── Scorers ───────────────────────────────────────────────────────────────────

def isolation_forest_scores(matches: list[dict]) -> np.ndarray:
    """
    Fit Isolation Forest and return suspicion scores (higher = more anomalous).

    contamination=0.15 only sets the predict() threshold; it does not affect
    score_samples(), so ranking is independent of this parameter.
    """
    features = build_features(matches)
    clf = IsolationForest(contamination=0.15, random_state=42, n_estimators=100)
    clf.fit(features)
    return -clf.score_samples(features)   # negate: more negative raw → more suspicious


def spread_rule_scores(matches: list[dict]) -> np.ndarray:
    """Baseline: rank by the larger of home/away spread (no model needed)."""
    return np.array([max(m["spread_home"], m["spread_away"]) for m in matches])


# ── Report helpers ────────────────────────────────────────────────────────────

def print_metrics_block(name: str, labels: list[int], scores) -> None:
    n      = len(labels)
    n_pos  = sum(labels)
    auc    = roc_auc_score(labels, scores)
    ap     = average_precision_score(labels, scores)
    rand_ap = n_pos / n

    print(f"\n── {name}")
    print(f"   ROC-AUC        {auc:.3f}   (random: 0.500)")
    print(f"   Avg Precision  {ap:.3f}   (random: {rand_ap:.3f})")
    for k in [k for k in (3, 5, 10, n) if k <= n]:
        tag = f"@{k}" if k < n else "@all"
        print(
            f"   NDCG{tag:<5}      {ndcg_at_k(labels, scores, k):.3f}   "
            f"Recall{tag:<5} {recall_at_k(labels, scores, k):.3f}"
        )


def print_ranked_list(matches, labels, if_scores, base_scores) -> None:
    if_rank   = np.argsort(np.argsort(-np.array(if_scores)))   + 1
    base_rank = np.argsort(np.argsort(-np.array(base_scores))) + 1
    order     = np.argsort(-np.array(if_scores))

    print(f"\n── Ranked List (sorted by Isolation Forest score) ───────────────")
    print(f"   {'MATCH':<44} IF   RULE  LABEL")
    print(f"   {'─'*44} {'─'*3}  {'─'*4}  {'─'*5}")
    for idx in order:
        name = matches[idx]["match"][:43]
        tag  = "FIXED" if labels[idx] else "clean"
        print(f"   {name:<44} {if_rank[idx]:<4} {base_rank[idx]:<5} {tag}")


def print_fix_type_analysis(matches, labels, if_scores) -> None:
    order    = np.argsort(-np.array(if_scores))
    rank_map = {idx: r + 1 for r, idx in enumerate(order)}

    ranked_fixes = sorted(
        [(rank_map[i], m) for i, m in enumerate(matches) if labels[i]],
        key=lambda x: x[0],
    )

    print(f"\n── Confirmed Fix Rankings ────────────────────────────────────────")
    print(f"   {'MATCH':<44} RANK  TYPE")
    print(f"   {'─'*44} {'─'*4}  {'─'*20}")
    for rank, m in ranked_fixes:
        print(f"   {m['match'][:43]:<44} {rank:<5} {m.get('fix_type', 'unknown')}")

    # Group by fix type
    by_type: dict[str, list[int]] = {}
    for rank, m in ranked_fixes:
        ft = m.get("fix_type", "unknown")
        by_type.setdefault(ft, []).append(rank)

    n = len(matches)
    print(f"\n── Detection by Fix Type (n={n} total matches) ───────────────────")
    for ft, ranks in sorted(by_type.items()):
        avg      = sum(ranks) / len(ranks)
        top_half = sum(1 for r in ranks if r <= n // 2)
        print(f"   {ft:<25}  avg rank {avg:.1f}   {top_half}/{len(ranks)} in top half")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_evaluation():
    print("=" * 65)
    print("  RANKING EVALUATION — Match-Fixing Detection Model")
    print("=" * 65)

    # ── Build datasets ────────────────────────────────────────────
    synthetic = augment_incidents(CONFIRMED_INCIDENTS, n_per=5)
    orig_all  = CONFIRMED_INCIDENTS + CLEAN_MATCHES
    aug_all   = CONFIRMED_INCIDENTS + synthetic + CLEAN_MATCHES

    labels_orig = [1 if m["confirmed_fixed"] else 0 for m in orig_all]
    labels_aug  = [1 if m["confirmed_fixed"] else 0 for m in aug_all]

    print(f"\nOriginal dataset : {len(orig_all):>3} matches  "
          f"({sum(labels_orig)} fixed, {len(CLEAN_MATCHES)} clean)")
    print(f"Augmented dataset: {len(aug_all):>3} matches  "
          f"({sum(labels_aug)} fixed "
          f"[{len(CONFIRMED_INCIDENTS)} real + {len(synthetic)} synthetic], "
          f"{len(CLEAN_MATCHES)} clean)")
    print()
    print("  Augmented variants add noise to known incidents to give more")
    print("  stable metric estimates. The model trains unsupervised on all")
    print("  data; labels are never seen during fit().")

    # ── Compute scores ────────────────────────────────────────────
    if_orig    = isolation_forest_scores(orig_all)
    base_orig  = spread_rule_scores(orig_all)
    if_aug     = isolation_forest_scores(aug_all)
    base_aug   = spread_rule_scores(aug_all)

    # ── Original dataset results ──────────────────────────────────
    sep = "═" * 65
    print(f"\n{sep}")
    print(f"  ORIGINAL DATASET  (n={len(orig_all)}, n_pos={sum(labels_orig)})")
    print(sep)

    print_metrics_block("Isolation Forest", labels_orig, if_orig)
    print_metrics_block("Baseline: max(spread_home, spread_away)", labels_orig, base_orig)
    print_ranked_list(orig_all, labels_orig, if_orig, base_orig)
    print_fix_type_analysis(orig_all, labels_orig, if_orig)

    # ── Augmented dataset results ─────────────────────────────────
    print(f"\n{sep}")
    print(f"  AUGMENTED DATASET  (n={len(aug_all)}, n_pos={sum(labels_aug)})")
    print(f"  More stable metric estimates — more positive examples.")
    print(sep)

    print_metrics_block("Isolation Forest", labels_aug, if_aug)
    print_metrics_block("Baseline: max(spread_home, spread_away)", labels_aug, base_aug)

    # ── Limitations ───────────────────────────────────────────────
    print(f"\n── Limitations ───────────────────────────────────────────────")
    print(f"  1. Only {sum(labels_orig)} real labeled positives — too few for reliable")
    print(f"     binary metrics. Ranking metrics are more appropriate here.")
    print(f"  2. Augmented variants share structure with originals (not")
    print(f"     independent), so augmented metrics overestimate generalization.")
    print(f"  3. Odds signatures are synthetic — actual pre-match odds for")
    print(f"     these historical matches are not publicly available.")
    print(f"  4. IF is unsupervised: it detects statistical outliers, not")
    print(f"     fixing patterns specifically. The spread-rule is a fair")
    print(f"     baseline because it uses the same dominant signal (spread).")
    print(f"  5. No temporal data. The strongest real-world signal is HOW")
    print(f"     odds move over time, not just where they land at kickoff.")
    print(f"\n  Next steps: acquire Betfair Exchange historical data for real")
    print(f"  odds time series; compare Isolation Forest vs LSTM on temporal")
    print(f"  line-movement features.")
    print("=" * 65)


if __name__ == "__main__":
    run_evaluation()
