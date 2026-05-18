export interface Match {
  match_id: string;
  sport: string;
  home_team: string;
  away_team: string;
  commence_time: string;
  bookmaker_count: number;
  prob_home: number;
  prob_draw: number;
  prob_away: number;
  spread_home: number;
  spread_draw: number;
  spread_away: number;
  max_prob_home: number;
  max_prob_away: number;
  min_prob_home: number;
  min_prob_away: number;
  anomaly_score: number;
  is_suspicious: boolean;
  confidence: number;
  flags: string;
}

export interface Report {
  generated_at: string;
  sport: string;
  total_matches_analyzed: number;
  suspicious_matches_found: number;
  flagged_matches: Match[];
  all_matches: Match[];
}
