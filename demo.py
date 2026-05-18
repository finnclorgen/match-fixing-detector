"""
demo.py — Run the full pipeline on synthetic data (no API key needed).
Replace fetch_odds() with the real API call once you have a key.
"""

import json
import numpy as np
from pipeline import (
    NormalizedMatch,
    run_anomaly_detection,
    classify_and_flag,
    generate_report,
)
from datetime import datetime, timezone, timedelta


def make_match(i, home, away, home_probs, draw_probs, away_probs):
    """Helper: build a NormalizedMatch from lists of per-bookmaker probs."""
    return NormalizedMatch(
        match_id=f"match_{i:03d}",
        sport="soccer_epl",
        home_team=home,
        away_team=away,
        commence_time=(datetime.now(timezone.utc) + timedelta(days=i % 7)).isoformat(),
        bookmaker_count=len(home_probs),
        prob_home=float(np.mean(home_probs)),
        prob_draw=float(np.mean(draw_probs)),
        prob_away=float(np.mean(away_probs)),
        spread_home=float(np.std(home_probs)),
        spread_draw=float(np.std(draw_probs)),
        spread_away=float(np.std(away_probs)),
        max_prob_home=float(max(home_probs)),
        max_prob_away=float(max(away_probs)),
        min_prob_home=float(min(home_probs)),
        min_prob_away=float(min(away_probs)),
    )


def generate_synthetic_matches():
    """
    Simulate a realistic mix of EPL matches:
    - Most are 'normal' with tight bookmaker consensus
    - A few are 'suspicious' with high spread / weird line movement
    """
    rng = np.random.default_rng(42)
    fixtures = [
        ("Manchester City",    "Arsenal"),
        ("Liverpool",          "Chelsea"),
        ("Tottenham",          "Manchester United"),
        ("Newcastle",          "Aston Villa"),
        ("Brighton",           "Fulham"),
        ("Brentford",          "Crystal Palace"),
        ("Everton",            "Nottingham Forest"),
        ("Wolves",             "Bournemouth"),
        ("West Ham",           "Burnley"),
        ("Luton",              "Sheffield United"),
        ("Leicester",          "Southampton"),
        ("Ipswich",            "Middlesbrough"),
        ("Coventry",           "Leeds"),
        ("Sunderland",         "Birmingham"),
        ("Preston",            "Stoke"),
    ]

    matches = []
    for i, (home, away) in enumerate(fixtures):
        n_books = rng.integers(4, 10)

        # ── Suspicious matches (injected anomalies) ──────────────────────────
        if i in [2, 7, 11]:   # Tottenham/ManU, Wolves/Bournemouth, Ipswich/Middlesbrough
            # Wide spread: bookmakers wildly disagree on home probability
            base_home = rng.uniform(0.25, 0.65)
            home_probs = np.clip(rng.normal(base_home, 0.09, n_books), 0.05, 0.90).tolist()
            base_away = rng.uniform(0.15, 0.45)
            away_probs = np.clip(rng.normal(base_away, 0.08, n_books), 0.05, 0.90).tolist()
            draw_probs = np.clip(1 - np.array(home_probs) - np.array(away_probs), 0.05, 0.60).tolist()

        elif i == 4:  # Brighton: extreme favorite (unusual for mid-table)
            home_probs = np.clip(rng.normal(0.87, 0.01, n_books), 0.80, 0.95).tolist()
            away_probs = np.clip(rng.normal(0.06, 0.01, n_books), 0.02, 0.12).tolist()
            draw_probs = np.clip(1 - np.array(home_probs) - np.array(away_probs), 0.02, 0.15).tolist()

        elif i == 9:  # Luton: very few bookmakers covering it
            n_books = 2
            home_probs = [0.38, 0.52]   # huge disagreement with only 2 books
            away_probs = [0.40, 0.27]
            draw_probs = [0.22, 0.21]

        # ── Normal matches: tight bookmaker consensus ─────────────────────────
        else:
            base_home = rng.uniform(0.28, 0.58)
            base_away = rng.uniform(0.18, 0.42)
            home_probs = np.clip(rng.normal(base_home, 0.008, n_books), 0.10, 0.80).tolist()
            away_probs = np.clip(rng.normal(base_away, 0.008, n_books), 0.10, 0.80).tolist()
            draw_probs = np.clip(1 - np.array(home_probs) - np.array(away_probs), 0.10, 0.40).tolist()

        matches.append(make_match(i, home, away, home_probs, draw_probs, away_probs))

    return matches


def run_demo():
    print("=" * 60)
    print("  MATCH-FIXING DETECTION — DEMO MODE (synthetic data)")
    print("=" * 60)

    print("\n[Stage 1] Generating synthetic EPL odds data...")
    matches = generate_synthetic_matches()
    print(f"  Generated {len(matches)} matches across {len(set(m.bookmaker_count for m in matches))} bookmaker-count variants")

    print("\n[Stage 2] Running Isolation Forest anomaly detection...")
    matches = run_anomaly_detection(matches)

    print("\n[Stage 3] Classifying & flagging...")
    matches = classify_and_flag(matches)

    print("\n[Stage 4] Generating report...")
    report = generate_report(matches)

    # Save
    with open("demo_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print results
    total = report["total_matches_analyzed"]
    flagged = report["flagged_matches"]
    print(f"\n  ✓ {len(flagged)}/{total} matches flagged as suspicious\n")
    print("-" * 60)
    print(f"{'MATCH':<38} {'CONF':>5}  FLAGS")
    print("-" * 60)
    for m in flagged:
        label = f"{m['home_team']} vs {m['away_team']}"
        print(f"{label:<38} {m['confidence']:>4.0%}  {m['flags']}")
    print("-" * 60)

    # Also print all matches for reference
    print(f"\nAll matches (sorted by suspicion):")
    all_m = sorted(report["all_matches"], key=lambda x: x["confidence"] if x["is_suspicious"] else 0, reverse=True)
    for m in all_m:
        tag = "🚨 FLAGGED" if m["is_suspicious"] else "  ✓ ok    "
        label = f"{m['home_team']} vs {m['away_team']}"
        print(f"  {tag}  {label:<38}  spread_H={m['spread_home']:.4f}  prob_H={m['prob_home']:.2f}")

    print(f"\nFull report saved to demo_report.json")
    return report


if __name__ == "__main__":
    run_demo()
