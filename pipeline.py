"""
Sports Match-Fixing Detection Pipeline
Stage 1: Data collection & odds normalization
Stage 2: Anomaly detection via Isolation Forest
Stage 3: Classification & confidence scoring
"""

import requests
import json
import numpy as np
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional
import os

# ── Config ────────────────────────────────────────────────────────────────────
API_KEY = os.getenv("ODDS_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.the-odds-api.com/v4"
SPORT    = "soccer_epl"          # English Premier League — one sport as TA suggested
REGIONS  = "uk,eu,us"
MARKETS  = "h2h"                 # head-to-head (1X2)


# ── Data model ────────────────────────────────────────────────────────────────
@dataclass
class NormalizedMatch:
    match_id: str
    sport: str
    home_team: str
    away_team: str
    commence_time: str
    bookmaker_count: int
    # Implied probabilities (averaged across bookmakers, overround-removed)
    prob_home: float
    prob_draw: float
    prob_away: float
    # Spread metrics (disagreement between bookmakers)
    spread_home: float
    spread_draw: float
    spread_away: float
    max_prob_home: float
    max_prob_away: float
    min_prob_home: float
    min_prob_away: float
    # Anomaly output
    anomaly_score: float = 0.0
    is_suspicious: bool  = False
    confidence: float    = 0.0
    flags: str           = ""


# ── Stage 1: Data collection & normalization ──────────────────────────────────
def fetch_odds(sport: str = SPORT) -> list[dict]:
    """Fetch live/upcoming odds from The Odds API."""
    url = f"{BASE_URL}/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "decimal",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    print(f"  API requests remaining: {resp.headers.get('x-requests-remaining', '?')}")
    return resp.json()


def decimal_to_implied_prob(decimal_odd: float) -> float:
    """Convert decimal odds to implied probability."""
    return 1.0 / decimal_odd if decimal_odd > 0 else 0.0


def remove_overround(probs: list[float]) -> list[float]:
    """Normalize probabilities to sum to 1.0 (remove bookmaker margin)."""
    total = sum(probs)
    return [p / total for p in probs] if total > 0 else probs


def normalize_match(raw: dict) -> Optional[NormalizedMatch]:
    """
    For each match, aggregate odds across bookmakers and compute:
    - Mean implied probability per outcome
    - Spread (std dev) per outcome — high spread = bookmakers disagree
    """
    bookmakers = raw.get("bookmakers", [])
    if len(bookmakers) < 2:
        return None  # Need at least 2 books to detect line divergence

    home_probs, draw_probs, away_probs = [], [], []

    for bm in bookmakers:
        for market in bm.get("markets", []):
            if market["key"] != "h2h":
                continue
            outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
            home = outcomes.get(raw["home_team"])
            away = outcomes.get(raw["away_team"])
            draw = outcomes.get("Draw")
            if not (home and away and draw):
                continue
            raw_probs = [
                decimal_to_implied_prob(home),
                decimal_to_implied_prob(draw),
                decimal_to_implied_prob(away),
            ]
            norm = remove_overround(raw_probs)
            home_probs.append(norm[0])
            draw_probs.append(norm[1])
            away_probs.append(norm[2])

    if not home_probs:
        return None

    return NormalizedMatch(
        match_id       = raw["id"],
        sport          = raw["sport_key"],
        home_team      = raw["home_team"],
        away_team      = raw["away_team"],
        commence_time  = raw["commence_time"],
        bookmaker_count= len(home_probs),
        prob_home      = float(np.mean(home_probs)),
        prob_draw      = float(np.mean(draw_probs)),
        prob_away      = float(np.mean(away_probs)),
        spread_home    = float(np.std(home_probs)),
        spread_draw    = float(np.std(draw_probs)),
        spread_away    = float(np.std(away_probs)),
        max_prob_home  = float(max(home_probs)),
        max_prob_away  = float(max(away_probs)),
        min_prob_home  = float(min(home_probs)),
        min_prob_away  = float(min(away_probs)),
    )


# ── Stage 2: Anomaly detection (Isolation Forest) ─────────────────────────────
def run_anomaly_detection(matches: list[NormalizedMatch]) -> list[NormalizedMatch]:
    """
    Feature vector per match:
    [spread_home, spread_draw, spread_away,
     prob_home, prob_away,
     max-min home range, max-min away range]

    Isolation Forest: anomalies are matches that are easy to isolate
    (unusual combinations of odds spread + implied probability)
    """
    from sklearn.ensemble import IsolationForest

    if len(matches) < 3:
        print("  Not enough matches for anomaly detection (need ≥3)")
        return matches

    features = np.array([
        [
            m.spread_home,
            m.spread_draw,
            m.spread_away,
            m.prob_home,
            m.prob_away,
            m.max_prob_home - m.min_prob_home,
            m.max_prob_away - m.min_prob_away,
        ]
        for m in matches
    ])

    clf = IsolationForest(
        contamination=0.15,   # assume ~15% of matches may be suspicious
        random_state=42,
        n_estimators=100,
    )
    clf.fit(features)

    raw_scores = clf.score_samples(features)   # more negative = more anomalous
    predictions = clf.predict(features)        # -1 = anomaly, 1 = normal

    # Normalize scores to [0, 1] confidence range
    min_s, max_s = raw_scores.min(), raw_scores.max()
    for i, m in enumerate(matches):
        normalized = (raw_scores[i] - min_s) / (max_s - min_s + 1e-9)
        m.anomaly_score = float(raw_scores[i])
        m.is_suspicious = predictions[i] == -1
        # Confidence: higher when score is more extreme
        m.confidence = float(1.0 - normalized) if m.is_suspicious else float(normalized)

    return matches


# ── Stage 3: Classification & flagging ────────────────────────────────────────
THRESHOLDS = {
    "high_spread":      0.03,   # >3% std dev across bookmakers = unusual
    "extreme_favorite": 0.80,   # >80% implied prob = very lopsided
    "low_bookmakers":   3,      # fewer books = less market scrutiny
}

def classify_and_flag(matches: list[NormalizedMatch]) -> list[NormalizedMatch]:
    """Add human-readable flags explaining why a match is suspicious."""
    for m in matches:
        flags = []
        if m.spread_home > THRESHOLDS["high_spread"] or m.spread_away > THRESHOLDS["high_spread"]:
            flags.append("HIGH_BOOKMAKER_DISAGREEMENT")
        if m.prob_home > THRESHOLDS["extreme_favorite"] or m.prob_away > THRESHOLDS["extreme_favorite"]:
            flags.append("EXTREME_FAVORITE")
        if m.bookmaker_count < THRESHOLDS["low_bookmakers"]:
            flags.append("LOW_MARKET_COVERAGE")
        if m.max_prob_home - m.min_prob_home > 0.10:
            flags.append("LARGE_HOME_LINE_RANGE")
        if m.max_prob_away - m.min_prob_away > 0.10:
            flags.append("LARGE_AWAY_LINE_RANGE")
        m.flags = ", ".join(flags) if flags else "NONE"
    return matches


# ── Stage 4: Report generation ─────────────────────────────────────────────────
def generate_report(matches: list[NormalizedMatch]) -> dict:
    suspicious = [m for m in matches if m.is_suspicious]
    suspicious.sort(key=lambda m: m.confidence, reverse=True)

    def fix_types(d):
        return {k: (bool(v) if isinstance(v, (bool, np.bool_)) else
                    float(v) if isinstance(v, (np.floating,)) else v)
                for k, v in d.items()}

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sport": SPORT,
        "total_matches_analyzed": len(matches),
        "suspicious_matches_found": len(suspicious),
        "flagged_matches": [fix_types(asdict(m)) for m in suspicious],
        "all_matches": [fix_types(asdict(m)) for m in matches],
    }
    return report


# ── Main ──────────────────────────────────────────────────────────────────────
def run_pipeline() -> dict:
    print("=" * 60)
    print("  MATCH-FIXING DETECTION PIPELINE")
    print("=" * 60)

    print("\n[Stage 1] Fetching odds data...")
    raw_data = fetch_odds()
    print(f"  Fetched {len(raw_data)} matches")

    print("\n[Stage 1] Normalizing odds...")
    matches = [normalize_match(m) for m in raw_data]
    matches = [m for m in matches if m is not None]
    print(f"  Normalized {len(matches)} matches")

    print("\n[Stage 2] Running anomaly detection...")
    matches = run_anomaly_detection(matches)

    print("\n[Stage 3] Classifying & flagging...")
    matches = classify_and_flag(matches)

    print("\n[Stage 4] Generating report...")
    report = generate_report(matches)

    suspicious = report["suspicious_matches_found"]
    total = report["total_matches_analyzed"]
    print(f"\n  ✓ Done — {suspicious}/{total} matches flagged as suspicious")
    print("=" * 60)

    return report


if __name__ == "__main__":
    report = run_pipeline()
    output_path = "report.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {output_path}")

    # Print top suspicious matches
    flagged = report["flagged_matches"]
    if flagged:
        print(f"\nTop suspicious matches:")
        for m in flagged[:5]:
            print(f"  [{m['confidence']:.0%}] {m['home_team']} vs {m['away_team']} — {m['flags']}")
    else:
        print("\nNo suspicious matches found.")
