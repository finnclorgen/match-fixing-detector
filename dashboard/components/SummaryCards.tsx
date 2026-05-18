"use client";

import { Report } from "@/lib/types";

interface Props {
  report: Report;
}

function Card({ label, value, sub, accent }: { label: string; value: string; sub?: string; accent?: string }) {
  return (
    <div className="card p-5 flex flex-col gap-1">
      <span className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
        {label}
      </span>
      <span className="text-3xl font-bold" style={{ color: accent ?? "var(--text)" }}>
        {value}
      </span>
      {sub && <span className="text-xs" style={{ color: "var(--text-muted)" }}>{sub}</span>}
    </div>
  );
}

export default function SummaryCards({ report }: Props) {
  const flagRate = report.total_matches_analyzed > 0
    ? ((report.suspicious_matches_found / report.total_matches_analyzed) * 100).toFixed(0)
    : "0";

  const avgConfidence = report.flagged_matches.length > 0
    ? (report.flagged_matches.reduce((s, m) => s + m.confidence, 0) / report.flagged_matches.length * 100).toFixed(0)
    : "—";

  const topAnomalyScore = report.all_matches.length > 0
    ? Math.min(...report.all_matches.map((m) => m.anomaly_score)).toFixed(3)
    : "—";

  const generatedAt = new Date(report.generated_at).toLocaleString("en-GB", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit", timeZoneName: "short",
  });

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card label="Matches Analysed" value={String(report.total_matches_analyzed)} sub={generatedAt} />
      <Card
        label="Flagged Suspicious"
        value={String(report.suspicious_matches_found)}
        sub={`${flagRate}% of total`}
        accent={report.suspicious_matches_found > 0 ? "var(--red)" : "var(--green)"}
      />
      <Card
        label="Avg Confidence"
        value={`${avgConfidence}%`}
        sub="flagged matches only"
        accent={Number(avgConfidence) > 70 ? "var(--red)" : "var(--amber)"}
      />
      <Card label="Peak Anomaly Score" value={topAnomalyScore} sub="more negative = more unusual" />
    </div>
  );
}
