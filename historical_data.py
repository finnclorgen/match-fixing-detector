"""
historical_data.py

A curated dataset of confirmed match-fixing incidents from public sources,
combined with synthetic odds signatures that reflect known fixing patterns.

Sources:
- Wikipedia: List of match-fixing incidents
- Europol Operation VETO (2013)
- Bochum District Court (2011) — Ante Sapina / Marijo Cvrtak conviction
- Bundesliga Hoyzer scandal (2004-2005) — German court conviction 2006
- Italian Calciopoli (2006) — Italian federal court
- Italian Totonero (1980) — FIGC sports tribunal
- Italian Calcioscommesse (2011-12) — Cremona prosecutor
- K-League scandal (2011) — criminal convictions, lifetime bans
- Brazilian referee scandal (2005) — Brazilian FA
- Turkish Fenerbahce scandal (2011) — UEFA sanction
- Wilson Raj Perumal: Lapland District Court (Finland, 2011); FIFA investigation
- Norwegian Euro qualifying 2007 — Bochum conviction; UEFA/CAS (Kevin Sammut)

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

    # ── Bochum Prosecution / Operation VETO — Sapina & Cvrtak (2009-11) ─────
    # Ante Sapina and Marijo Cvrtak convicted by Bochum District Court May 2011,
    # sentenced to 5.5 years each. 22+ counts of fraud and attempted fraud.
    # These are UEFA Champions League and World Cup qualifying matches —
    # the highest-profile confirmed fixed matches in European history.
    {
        "id": "sapina_001",
        "match": "Liechtenstein vs Finland",
        "league": "2010 FIFA World Cup Qualifying (UEFA Group 4)",
        "season": "2009-10",
        "year": 2009,
        "confirmed_fixed": True,
        "fix_type": "referee",
        "outcome": "draw",   # 1-1; both goals second half as contracted
        "source": "Bochum District Court conviction May 2011; referee Novo Panic banned for life by UEFA",
        "prob_home": 0.08,   # Liechtenstein: tiny nation, massive underdog
        "prob_draw": 0.17,
        "prob_away": 0.75,   # Finland heavy favourite
        "spread_home": 0.042,
        "spread_draw": 0.063,  # draw spread very high — sharp late money on draw
        "spread_away": 0.055,
        "bookmaker_count": 6,
        "notes": "Referee Novo Panic paid €40,000 to ensure two second-half goals (1-1). Both goals scored in second half as arranged. Sapina named in conviction. WC qualifying match flagged by Sportradar.",
    },
    {
        "id": "sapina_002",
        "match": "Debrecen vs Fiorentina",
        "league": "UEFA Champions League Group Stage",
        "season": "2009-10",
        "year": 2009,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "away_win",   # Fiorentina won 4-3; Debrecen scored 3 second-half goals as arranged
        "source": "Bochum District Court conviction May 2011; Sapina guilty plea",
        "prob_home": 0.27,   # Debrecen (Hungarian side) considerable underdogs in UCL
        "prob_draw": 0.22,
        "prob_away": 0.51,   # Fiorentina (Serie A) favourites
        "spread_home": 0.049,
        "spread_draw": 0.031,
        "spread_away": 0.043,
        "bookmaker_count": 14,   # UCL match — wide bookmaker coverage
        "notes": "Fix targeted second-half scoreline for over/scoreline betting markets. Fiorentina led 4-0 at half-time; Debrecen scored three second-half goals as contracted. Named in Sapina's confession to Bochum prosecutors.",
    },
    {
        "id": "sapina_003",
        "match": "Norway vs Malta",
        "league": "UEFA Euro 2008 Qualifying (Group A)",
        "season": "2006-07",
        "year": 2007,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "home_win",   # Norway 4-0; three late goals inflated margin for handicap betting
        "source": "Bochum District Court conviction (Cvrtak, 26 counts); CAS upheld UEFA 10-year ban on Kevin Sammut Aug 2012",
        "prob_home": 0.73,   # Norway strong favourites at home vs Malta
        "prob_draw": 0.17,
        "prob_away": 0.10,
        "spread_home": 0.064,
        "spread_draw": 0.038,
        "spread_away": 0.057,
        "bookmaker_count": 7,
        "notes": "Cvrtak met Malta players in Oslo hotel pre-match; €200,000 wagered. Three late goals inflated margin consistent with Asian handicap fix. Malta midfielder Kevin Sammut received €6,000 bribe; 10-year UEFA ban upheld by CAS. Norway win was legitimate favourite; fix was on goal margin.",
    },

    # ── Hoyzer Scandal — Additional Confirmed Matches (2004) ─────────────────
    # DFB ordered a replay of LR Ahlen vs Burghausen — the highest DFB evidentiary
    # threshold, indicating a fully confirmed manipulation. Same Sapina/Hoyzer syndicate.
    {
        "id": "hoyzer_003",
        "match": "LR Ahlen vs SV Wacker Burghausen",
        "league": "2. Bundesliga",
        "season": "2004-05",
        "year": 2004,
        "confirmed_fixed": True,
        "fix_type": "referee",
        "outcome": "home_win",   # Ahlen 1-0; replay ordered (Burghausen won replay 3-1)
        "source": "German court conviction 2006; DFB ordered replay 27 April 2005",
        "prob_home": 0.38,
        "prob_draw": 0.29,
        "prob_away": 0.33,   # Roughly even match
        "spread_home": 0.056,
        "spread_draw": 0.027,
        "spread_away": 0.049,
        "bookmaker_count": 5,
        "notes": "Hoyzer awarded Ahlen a questionable penalty. DFB ordered replay, the strongest possible confirmation that manipulation was proven. Burghausen won the replay 3-1. Same Sapina–Hoyzer syndicate as Paderborn/Hamburg.",
    },

    # ── Wilson Raj Perumal Fixes (2010) ──────────────────────────────────────
    # Perumal convicted by Lapland District Court (Finland) Jul 2011, upheld by
    # Court of Appeal. FIFA confirmed two specific international friendlies.
    {
        "id": "perumal_001",
        "match": "South Africa vs Guatemala",
        "league": "International Friendly (pre-2010 World Cup)",
        "season": "2010",
        "year": 2010,
        "confirmed_fixed": True,
        "fix_type": "referee",
        "outcome": "home_win",   # South Africa won 5-0; three penalties awarded, two appeared incorrect
        "source": "FIFA investigation; referee Ibrahim Chaibou (Niger) banned; Perumal admitted arranging referee via Football4U International",
        "prob_home": 0.60,   # South Africa (WC hosts) vs Guatemala
        "prob_draw": 0.23,
        "prob_away": 0.17,
        "spread_home": 0.057,
        "spread_draw": 0.027,
        "spread_away": 0.050,
        "bookmaker_count": 4,   # Friendly — limited coverage
        "notes": "FIFA concluded match 'manipulated for betting fraud purposes'. Referee Chaibou awarded three penalties, two of which appeared incorrect. Perumal's company Football4U arranged the referee appointment. Score 5-0 was exaggerated by the fix.",
    },
    {
        "id": "perumal_002",
        "match": "Bahrain vs Togo",
        "league": "International Friendly",
        "season": "2010",
        "year": 2010,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "home_win",   # 3-0 Bahrain; 'Togo' team was entirely impostors
        "source": "FIFA confirmed; Togo Football Federation confirmed players were impostors; Bahrain FA confirmed Perumal's company Football4U organised the match",
        "prob_home": 0.44,   # Bahrain vs Togo — relatively even pre-match
        "prob_draw": 0.29,
        "prob_away": 0.27,
        "spread_home": 0.069,
        "spread_draw": 0.044,
        "spread_away": 0.073,   # Extreme spread — market uncertainty about actual participants
        "bookmaker_count": 3,
        "notes": "Real Togo squad was on a bus returning from Botswana at kickoff. Perumal fielded 11 impostors; result (Bahrain 3-0) and goals manipulated for Asian betting markets. 5 additional goals were ruled offside. Unique case: fix achieved by substituting an entire national team. Togo FA president confirmed players were 'completely fake'.",
    },

    # ── Italian Totonero (1980) ───────────────────────────────────────────────
    # Players bribed by Alvaro Trinca's betting syndicate. FIGC sports tribunal
    # imposed bans and relegated AC Milan and Lazio. Key confirmed match:
    {
        "id": "totonero_001",
        "match": "AC Milan vs Lazio",
        "league": "Serie A",
        "season": "1979-80",
        "year": 1980,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "home_win",   # AC Milan won 2-1
        "source": "FIGC sports tribunal; AC Milan and Lazio relegated to Serie B; players Albertosi, Marini (Milan), Giordano, Manfredonia, Cacciatori, Wilson (Lazio) suspended",
        "prob_home": 0.44,
        "prob_draw": 0.27,
        "prob_away": 0.29,
        "spread_home": 0.058,
        "spread_draw": 0.031,
        "spread_away": 0.052,
        "bookmaker_count": 3,   # Pre-internet era; Italian pools (Totocalcio) era
        "notes": "Bribed by Alvaro Trinca's Totocalcio-based syndicate. Confirmed players: Enrico Albertosi and Giorgio Marini (Milan), Bruno Giordano, Lionello Manfredonia, Massimo Cacciatori, Giuseppe Wilson (Lazio). Criminal court acquitted all (no match-fixing law existed in 1980); FIGC tribunal sanctions enforced regardless. Paolo Rossi received 2-year ban for related Perugia incident.",
    },

    # ── Italian Calcioscommesse (2011-12) ─────────────────────────────────────
    # Cremona prosecutor's investigation uncovered systematic fixing in Lega Pro.
    # Most dramatic confirmed incident: players drugged at halftime.
    {
        "id": "calcioscom_001",
        "match": "Cremonese vs Paganese",
        "league": "Lega Pro Prima Divisione",
        "season": "2010-11",
        "year": 2010,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "draw",   # Fix: Cremonese players drugged at HT (winning 2-0) to sabotage result
        "source": "Italian criminal investigation; doping tests confirmed sleeping drug administered; goalkeeper Marco Paoloni banned 5 years",
        "prob_home": 0.42,
        "prob_draw": 0.30,
        "prob_away": 0.28,
        "spread_home": 0.040,
        "spread_draw": 0.019,
        "spread_away": 0.034,
        "bookmaker_count": 3,   # Lega Pro (Serie C) — limited bookmaker coverage
        "notes": "Five Cremonese players administered sleeping drug at halftime (Cremonese were leading 2-0). Players suddenly fell ill in second half. Doping tests confirmed substance. Goalkeeper Paoloni suspected of administering drug to teammates to sabotage match for betting purposes. Unusual internal-sabotage fix type.",
    },

    # ── K-League Additional Confirmed Match (2011) ────────────────────────────
    {
        "id": "kleague_002",
        "match": "Daejeon Citizen vs Pohang Steelers",
        "league": "Korean League Cup",
        "season": "2011",
        "year": 2011,
        "confirmed_fixed": True,
        "fix_type": "result",
        "outcome": "away_win",   # Daejeon lost 0-3; players bribed to lose
        "source": "Criminal indictment; multiple Daejeon players convicted; lifetime bans imposed by Korean FA",
        "prob_home": 0.32,   # Daejeon underdogs vs Pohang (strong side)
        "prob_draw": 0.27,
        "prob_away": 0.41,
        "spread_home": 0.065,
        "spread_draw": 0.031,
        "spread_away": 0.059,
        "bookmaker_count": 4,
        "notes": "Daejeon players bribed to lose. Pohang player Kim Jung-kyum given 5-year ban for placing a bet on his own team after receiving a tip-off from a Daejeon player about the fix — a secondary consequence of the manipulation. Part of the wider 2011 K-League scandal (19 fixed matches in 2010 + 2 in 2011).",
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
