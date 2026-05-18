# Sports Match-Fixing Detection Platform

An open-source alternative to expensive B2B sports integrity software.

## Pipeline Overview

```
Raw Odds Data → Normalize → Anomaly Detection → Classification → Report
   (Stage 1)    (Stage 1)      (Stage 2)          (Stage 3)     (Stage 4)
```

### Stage 1 — Data Collection & Normalization
- Fetches live odds from multiple bookmakers via [The Odds API](https://the-odds-api.com)
- Converts decimal odds → implied probabilities
- Removes bookmaker overround (margin) to get true market probabilities
- Computes per-outcome spread (std dev across bookmakers) as a divergence signal

### Stage 2 — Anomaly Detection
- Runs **Isolation Forest** on a 7-feature vector per match
- Features: spread per outcome, mean probability, home/away line range
- Matches that are "easy to isolate" in feature space = statistically unusual

### Stage 3 — Classification & Confidence Scoring
- Rule-based flags: `HIGH_BOOKMAKER_DISAGREEMENT`, `EXTREME_FAVORITE`, `LOW_MARKET_COVERAGE`, `LARGE_LINE_RANGE`
- Confidence score derived from normalized Isolation Forest anomaly score

### Stage 4 — Report Generation
- Outputs JSON report with all matches + flagged matches ranked by confidence

## Quickstart

```bash
pip install -r requirements.txt

# Demo mode (synthetic EPL data, no API key needed)
python demo.py

# Live mode (requires free API key from the-odds-api.com)
export ODDS_API_KEY=your_key_here
python pipeline.py
```

## Scope (per TA feedback)
Currently scoped to **English Premier League (EPL)** for the MVP.
Evaluation against known fixing incidents is the next milestone.

## Roadmap
- [ ] Historical odds backfill for backtesting against known incidents
- [ ] LSTM sequence model for temporal line movement patterns
- [ ] LLM enrichment: pull news/injury context to filter false positives
- [ ] Public dashboard (React frontend)
- [ ] Expand beyond EPL to other leagues
