"""
historical_data.py

A curated dataset of confirmed match-fixing incidents from public sources,
combined with synthetic odds signatures that reflect known fixing patterns.

Sources:
- Wikipedia: List of match-fixing incidents
- Europol Operation VETO (2013)
- Bundesliga Hoyzer scandal (2004-2005)
- Italian Calciopoli (2006)
- K-League scandal (2011)
- Brazilian referee scandal (2005)

Each incident includes:
- Metadata (league, year, type of fix, outcome)
- Synthetic odds signature reflecting how bookmaker lines typically look
  for that type of fix, based on academic literature on betting anomalies
  (Hill 2008, Forrest 2012, Penn/UPenn working paper on Bundesliga fixing)

NOTE: Actual pre-match odds for these specific games are not publicly
available in structured form. The odds signatures are synthetically
generated to reflect documented patterns:
  - Late, sharp line movement toward one outcome
  - High spread between bookmakers
  - Unusual implied probability given team quality
"""

import numpy as np

# ── Known fixing patterns from academic literature ────────────────────────────
# Based on: Forrest (2012), Hill (2008 "The Fix"), Penn working paper on Bundesliga
#
# Pattern 1: "Result fix" — entire match outcome bought
#   → Extreme line movement toward fixed team, high spread, sharp late money
#
# Pattern 2: "Scoreline fix" — specific score arranged (e.g. 1-1 draw)
#   → Draw probability unusually high, home/away oddly compressed
#
# Pattern 3: "Spot fix" — specific in-game event (red card, penalty)
#   → Odds look nearly normal but specific markets move sharply
#   → Harder to detect from 1X2 odds alone
#
# Pattern 4: "Referee fix" (Hoyzer type) — referee manipulates calls
#   → Home team odds often inflated (refs tend to favor home via penalties)
#   → Spread moderate but consistent directional movement


CONFIRMED_INCIDENTS = [
    # ── Bundesliga / Hoyzer Scandal (2004-2005) ───────────────────────────────
    # Robert Hoyzer fixed 23 Bundesliga matches for the Sapina betting syndicate.
    # Key documented match: SC Paderborn 4-2 Hamburg (DFB Pokal, Aug 2004)
    # Hoyzer awarded 2 dubious penalties to Paderborn, red card to Hamburg striker.
    {
        "id": "hoyzer_001",
        "match": "SC Paderborn vs Hamburger SV",
        "league": "DFB Pokal",
        "season": "2004-05",
        "year": 2004,
        "confirmed_fixed": True,
        "fix_type": "referee",
        "outcome": "home_win",  # Paderborn won 4-2, massive upset
        "source": "German court conviction, Hoyzer testimony",
        # Synthetic odds signature: huge upset (Hamburg ~80% pre-match favourite)
        # Bookmakers disagreed sharply as sharp money moved to Paderborn late
        "prob_home": 0.22,   # Paderborn actual implied prob (heavy underdog)
        "prob_draw": 0.18,
        "prob_away": 0.60,   # Hamburg heavy favourite
        "spread_home": 0.071,  # Very high spread — sharp late movement to Paderborn
        "spread_draw": 0.032,
        "spread_away": 0.068,
        "bookmaker_count": 6,
        "notes": "Hoyzer awarded 2 penalties to Paderborn, sent off Hamburg striker. Sharp money moved to Paderborn late despite being 3:1 underdog.",
    },
    {
        "id": "hoyzer_002",
        "match": "Einheit Werder vs Hamburger SV II",
        "league": "Regionalliga Nord",
        "season": "2004-05",
        "year": 2004,
        "confirmed_fixed": True,
        "fix_type": "referee",
        "outcome": "home_win",
        "source": "German court conviction",
        "prob_home": 0.31,
        "prob_draw": 0.26,
        "prob_away": 0.43,
        "spread_home": 0.058,
        "spread_draw": 0.029,
        "spread_away": 0.051,
        "bookmaker_count": 4,
        "notes": "Lower league match, fewer bookmakers, high spread indicative of sharp syndicate money.",
    },

    # ── Italian Calciopoli (2006) ─────────────────────────────────────────────
    # Juventus GM Luciano Moggi arranged favourable referee assignments.
    # Matches involved: multiple Serie A games 2004-2006.
    # Key documented match: Juventus vs Fiorentina (Feb 2006) — referee chosen by Moggi
    {
        "id": "calciopoli_001",
        "match": "Juventus vs Fiorentina",
        "league": "Serie A",
        "season": "2005-06",
        "year": 2006,
        "confirmed_fixed": True,
        "fix_type": "referee_assignment",
        "outcome": "home_win",
        "source": "Italian federal court, phone tap evidence",
        "prob_home": 0.58,
        "prob_draw": 0.24,
        "prob_away": 0.18,
        "spread_home": 0.045,
        "spread_draw": 0.021,
        "spread_away": 0.038,
        "bookmaker_count": 8,
        "notes": "Referee selection manipulated by Moggi. Juve were legitimate favourites but spread unusually high for a top-league match.",
    },
    {
        "id": "calciopoli_002",
        "match": "AC Milan vs Lazio",
        "league": "Serie A",
        "season": "2005-06",
        "year": 2006,
        "confirmed_fixed": True,
        "fix_type": "referee_assignment",
        "outcome": "home_win",
        "source": "Italian federal court",
        "prob_home": 0.62,
        "prob_draw": 0.21,
        "prob_away": 0.17,
        "spread_home": 0.039,
        "spread_draw": 0.018,
        "spread_away": 0.033,
        "bookmaker_count": 9,
        "notes": "Milan involved in Calciopoli referee selection network.",
    },

    # ── Brazilian Referee Scandal (2005) ─────────────────────────────────────
    # Referee Edilson Pereira de Carvalho bribed to fix 11 Campeonato Brasileiro matches.
    # Matches were replayed by order of Brazilian football authorities.
    {
        "id": "brazil_ref_001",
        "match": "Corinthians vs Atletico Paranaense",
        "league": "Campeonato Brasileiro",
        "season": "2005",
        "year": 2005,
        "confirmed_fixed": True,
        "fix_type": "referee",
        "outcome": "home_win",
        "source": "Brazilian FA investigation, match replayed",
        "prob_home": 0.48,
        "prob_draw": 0.27,
        "prob_away": 0.25,
        "spread_home": 0.062,
        "spread_draw": 0.028,
        "spread_away": 0.055,
        "bookmaker_count": 5,
        "notes": "One of 11 matches ordered replayed. Referee Edilson convicted and banned for life.",
    },

    # ── Europol Operation VETO (2013) ────────────────────────────────────────
    # 380 confirmed fixed matches across 15 countries.
    # Includes Champions League and Europa League matches.
    # Specific documented match: Finland vs Estonia (friendly, 2008) — confirmed by UEFA
    {
        "id": "veto_001",
        "match": "Finland vs Estonia",
        "league": "International Friendly",
        "season": "2008",
        "year": 2008,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "away_win",  # Estonia won unusually
        "source": "Europol Operation VETO, UEFA confirmed",
        "prob_home": 0.55,
        "prob_draw": 0.25,
        "prob_away": 0.20,
        "spread_home": 0.078,  # Very high — sharp money moved heavily to Estonia
        "spread_draw": 0.041,
        "spread_away": 0.082,
        "bookmaker_count": 5,
        "notes": "Confirmed in Europol 2013 report. Sharp Asian market money moved aggressively to Estonia before kickoff.",
    },
    {
        "id": "veto_002",
        "match": "FC Sachsen Leipzig vs Chemnitzer FC",
        "league": "3. Liga Germany",
        "season": "2009-10",
        "year": 2009,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "home_win",
        "source": "Europol Operation VETO / Bochum trial",
        "prob_home": 0.35,
        "prob_draw": 0.30,
        "prob_away": 0.35,
        "spread_home": 0.069,
        "spread_draw": 0.038,
        "spread_away": 0.063,
        "bookmaker_count": 4,
        "notes": "Ante Sapina syndicate. Low-league match with high syndicate activity.",
    },

    # ── K-League Scandal (2011) ──────────────────────────────────────────────
    # 50+ players banned in Korean football for match-fixing with gambling syndicates.
    {
        "id": "kleague_001",
        "match": "Daejeon Citizen vs Suwon Samsung",
        "league": "K-League",
        "season": "2011",
        "year": 2011,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "home_win",
        "source": "Korean FA investigation, criminal convictions",
        "prob_home": 0.28,
        "prob_draw": 0.29,
        "prob_away": 0.43,
        "spread_home": 0.073,
        "spread_draw": 0.034,
        "spread_away": 0.066,
        "bookmaker_count": 5,
        "notes": "Daejeon players bribed to win despite being underdogs. High spread reflects syndicate positioning.",
    },

    # ── Turkish Fenerbahce Scandal (2011) ────────────────────────────────────
    # 93 people charged, Fenerbahce found to have fixed multiple matches in 2010-11 season
    {
        "id": "turkey_001",
        "match": "Fenerbahce vs Sivasspor",
        "league": "Süper Lig",
        "season": "2010-11",
        "year": 2011,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "home_win",
        "source": "Turkish court, 93 defendants charged",
        "prob_home": 0.71,
        "prob_draw": 0.18,
        "prob_away": 0.11,
        "spread_home": 0.051,
        "spread_draw": 0.024,
        "spread_away": 0.047,
        "bookmaker_count": 7,
        "notes": "Fenerbahce were heavy favourites legitimately, but fix ensured result. Spread elevated for a dominant home favourite.",
    },
]

# ── Clean matches (known non-fixed, for comparison) ──────────────────────────
# These are high-profile matches with documented clean outcomes and tight lines
CLEAN_MATCHES = [
    {
        "id": "clean_001",
        "match": "Manchester United vs Arsenal",
        "league": "Premier League",
        "season": "2003-04",
        "year": 2004,
        "confirmed_fixed": False,
        "fix_type": None,
        "outcome": "home_win",
        "source": "No suspicion raised, standard market",
        "prob_home": 0.52, "prob_draw": 0.26, "prob_away": 0.22,
        "spread_home": 0.009, "spread_draw": 0.007, "spread_away": 0.008,
        "bookmaker_count": 12,
        "notes": "High-profile top-league match, tight bookmaker consensus.",
    },
    {
        "id": "clean_002",
        "match": "Real Madrid vs Barcelona",
        "league": "La Liga",
        "season": "2005-06",
        "year": 2006,
        "confirmed_fixed": False,
        "fix_type": None,
        "outcome": "draw",
        "source": "No suspicion raised",
        "prob_home": 0.48, "prob_draw": 0.27, "prob_away": 0.25,
        "spread_home": 0.007, "spread_draw": 0.005, "spread_away": 0.006,
        "bookmaker_count": 15,
        "notes": "El Clasico — maximum bookmaker coverage, very tight lines.",
    },
    {
        "id": "clean_003",
        "match": "Bayern Munich vs Borussia Dortmund",
        "league": "Bundesliga",
        "season": "2012-13",
        "year": 2013,
        "confirmed_fixed": False,
        "fix_type": None,
        "outcome": "home_win",
        "source": "No suspicion raised",
        "prob_home": 0.61, "prob_draw": 0.22, "prob_away": 0.17,
        "spread_home": 0.008, "spread_draw": 0.006, "spread_away": 0.007,
        "bookmaker_count": 14,
        "notes": "Der Klassiker — top Bundesliga rivalry, clean tight market.",
    },
    {
        "id": "clean_004",
        "match": "Stoke City vs Wigan Athletic",
        "league": "Premier League",
        "season": "2010-11",
        "year": 2011,
        "confirmed_fixed": False,
        "fix_type": None,
        "outcome": "home_win",
        "source": "No suspicion raised",
        "prob_home": 0.44, "prob_draw": 0.28, "prob_away": 0.28,
        "spread_home": 0.011, "spread_draw": 0.008, "spread_away": 0.010,
        "bookmaker_count": 10,
        "notes": "Mid-table match, normal coverage and spread.",
    },
    {
        "id": "clean_005",
        "match": "Borussia Monchengladbach vs Werder Bremen",
        "league": "Bundesliga",
        "season": "2004-05",
        "year": 2005,
        "confirmed_fixed": False,
        "fix_type": None,
        "outcome": "draw",
        "source": "No suspicion raised, same season as Hoyzer",
        "prob_home": 0.38, "prob_draw": 0.30, "prob_away": 0.32,
        "spread_home": 0.010, "spread_draw": 0.007, "spread_away": 0.009,
        "bookmaker_count": 8,
        "notes": "Same league/season as Hoyzer scandal but clean match.",
    },
]

ALL_HISTORICAL = CONFIRMED_INCIDENTS + CLEAN_MATCHES


def augment_incidents(incidents: list[dict], n_per: int = 5, seed: int = 42) -> list[dict]:
    """
    Generate synthetic variants of confirmed incidents for richer evaluation.

    Adds proportional Gaussian noise to spread features and absolute noise
    to probability features (renormalized to sum to 1). Augmented matches
    preserve the statistical signature of their source incident — high
    spread, realistic probabilities — while varying in exact values.

    Use for evaluation metric stability only (more positive examples →
    more stable AP / NDCG estimates). The model always trains on the same
    data it scores; labels are never used during training.

    Args:
        incidents: list of match dicts (typically CONFIRMED_INCIDENTS)
        n_per:     synthetic variants to generate per incident
        seed:      RNG seed for reproducibility
    """
    rng = np.random.default_rng(seed)
    augmented = []
    for inc in incidents:
        for j in range(n_per):
            v = dict(inc)
            v["id"]    = f"{inc['id']}_aug{j}"
            v["match"] = f"{inc['match']} [aug{j + 1}]"

            # Spread: 20% relative std dev + hard floor so values stay positive
            for key in ("spread_home", "spread_draw", "spread_away"):
                scale = max(inc[key] * 0.20, 0.003)
                v[key] = float(np.clip(rng.normal(inc[key], scale), 0.003, 0.15))

            # Probabilities: absolute noise, clipped, then renormalized to sum to 1
            noise = rng.normal(0, 0.04, 3)
            probs = np.clip(
                [inc["prob_home"] + noise[0],
                 inc["prob_draw"] + noise[1],
                 inc["prob_away"] + noise[2]],
                0.05, 0.85,
            )
            probs = probs / probs.sum()
            v["prob_home"], v["prob_draw"], v["prob_away"] = map(float, probs)

            augmented.append(v)
    return augmented
