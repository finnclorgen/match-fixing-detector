"use client";

import { Match } from "@/lib/types";
import FlagBadge from "./FlagBadge";
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from "recharts";

interface Props {
  match: Match;
  rank: number;
}

function ConfidenceRing({ pct }: { pct: number }) {
  const r = 28;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  const color = pct >= 80 ? "#ef4444" : pct >= 50 ? "#f59e0b" : "#10b981";
  return (
    <svg width={72} height={72} className="flex-shrink-0">
      <circle cx={36} cy={36} r={r} fill="none" stroke="#1a1a24" strokeWidth={8} />
      <circle
        cx={36} cy={36} r={r} fill="none"
        stroke={color} strokeWidth={8}
        strokeDasharray={`${dash} ${circ - dash}`}
        strokeLinecap="round"
        transform="rotate(-90 36 36)"
      />
      <text x={36} y={36} textAnchor="middle" dominantBaseline="central"
        fill={color} fontSize={13} fontWeight={700}>
        {pct}%
      </text>
    </svg>
  );
}

export default function FlaggedMatchCard({ match, rank }: Props) {
  const flags = match.flags === "NONE" ? [] : match.flags.split(",").map((f) => f.trim());
  const pct = Math.round(match.confidence * 100);

  const radarData = [
    { feature: "Home Spread", value: +(match.spread_home * 100).toFixed(2) },
    { feature: "Draw Spread", value: +(match.spread_draw * 100).toFixed(2) },
    { feature: "Away Spread", value: +(match.spread_away * 100).toFixed(2) },
    { feature: "Home Range", value: +((match.max_prob_home - match.min_prob_home) * 100).toFixed(2) },
    { feature: "Away Range", value: +((match.max_prob_away - match.min_prob_away) * 100).toFixed(2) },
  ];

  const date = new Date(match.commence_time).toLocaleDateString("en-GB", {
    weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });

  return (
    <div className="card p-5 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <span className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: "var(--text-muted)" }}>
            #{rank} · {date}
          </span>
          <h3 className="text-base font-bold leading-tight">
            {match.home_team} <span className="text-red-400">vs</span> {match.away_team}
          </h3>
          <span className="text-xs" style={{ color: "var(--text-muted)" }}>
            {match.bookmaker_count} bookmakers · score {match.anomaly_score.toFixed(4)}
          </span>
        </div>
        <ConfidenceRing pct={pct} />
      </div>

      {/* Flags */}
      {flags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {flags.map((f) => <FlagBadge key={f} flag={f} />)}
        </div>
      )}

      {/* Probability bars */}
      <div className="flex flex-col gap-2">
        {[
          { label: "Home", value: match.prob_home, color: "#3b82f6" },
          { label: "Draw", value: match.prob_draw, color: "#6b7280" },
          { label: "Away", value: match.prob_away, color: "#8b5cf6" },
        ].map(({ label, value, color }) => (
          <div key={label} className="flex items-center gap-2 text-xs">
            <span className="w-8 text-right" style={{ color: "var(--text-muted)" }}>{label}</span>
            <div className="flex-1 rounded-full h-2" style={{ background: "var(--surface-2)" }}>
              <div className="h-2 rounded-full" style={{ width: `${(value * 100).toFixed(1)}%`, background: color }} />
            </div>
            <span className="w-10 font-mono">{(value * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>

      {/* Radar */}
      <div className="h-44">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid stroke="#2a2a38" />
            <PolarAngleAxis dataKey="feature" tick={{ fill: "#64748b", fontSize: 10 }} />
            <Radar name="Spread %" dataKey="value" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
            <Tooltip
              contentStyle={{ background: "#111118", border: "1px solid #2a2a38", borderRadius: 8, fontSize: 12 }}
              formatter={(v: number) => [`${v}%`, "Spread"]}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
