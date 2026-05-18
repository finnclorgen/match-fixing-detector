"use client";

import { useState } from "react";
import { Match } from "@/lib/types";
import FlagBadge from "./FlagBadge";

interface Props {
  matches: Match[];
}

type SortKey = "anomaly_score" | "confidence" | "bookmaker_count" | "spread_home";

export default function MatchTable({ matches }: Props) {
  const [sort, setSort] = useState<SortKey>("anomaly_score");
  const [asc, setAsc] = useState(true);
  const [showOnly, setShowOnly] = useState<"all" | "suspicious" | "clean">("all");

  const toggle = (key: SortKey) => {
    if (sort === key) setAsc((p) => !p);
    else { setSort(key); setAsc(true); }
  };

  const filtered = matches.filter((m) =>
    showOnly === "all" ? true : showOnly === "suspicious" ? m.is_suspicious : !m.is_suspicious
  );

  const sorted = [...filtered].sort((a, b) => {
    const diff = a[sort] - b[sort];
    return asc ? diff : -diff;
  });

  const Th = ({ label, k }: { label: string; k: SortKey }) => (
    <th
      className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wider cursor-pointer select-none whitespace-nowrap"
      style={{ color: sort === k ? "var(--text)" : "var(--text-muted)" }}
      onClick={() => toggle(k)}
    >
      {label} {sort === k ? (asc ? "↑" : "↓") : ""}
    </th>
  );

  return (
    <div className="card flex flex-col gap-0">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 border-b" style={{ borderColor: "var(--border)" }}>
        <h2 className="text-sm font-semibold">All Matches</h2>
        <div className="flex gap-1">
          {(["all", "suspicious", "clean"] as const).map((v) => (
            <button
              key={v}
              onClick={() => setShowOnly(v)}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                showOnly === v
                  ? "bg-red-600 text-white"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {v.charAt(0).toUpperCase() + v.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto scrollbar-thin">
        <table className="w-full text-sm">
          <thead style={{ background: "var(--surface-2)" }}>
            <tr>
              <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wider whitespace-nowrap" style={{ color: "var(--text-muted)" }}>Match</th>
              <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wider whitespace-nowrap" style={{ color: "var(--text-muted)" }}>Status</th>
              <Th label="Anomaly Score" k="anomaly_score" />
              <Th label="Confidence" k="confidence" />
              <Th label="Books" k="bookmaker_count" />
              <Th label="Spread H" k="spread_home" />
              <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>Flags</th>
              <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wider whitespace-nowrap" style={{ color: "var(--text-muted)" }}>H / D / A %</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((m, i) => (
              <tr
                key={m.match_id}
                className="border-t transition-colors"
                style={{
                  borderColor: "var(--border)",
                  background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.015)",
                }}
              >
                <td className="px-3 py-2.5 font-medium whitespace-nowrap">
                  {m.home_team} <span style={{ color: "var(--text-muted)" }}>vs</span> {m.away_team}
                </td>
                <td className="px-3 py-2.5">
                  {m.is_suspicious ? (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-red-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
                      Suspicious
                    </span>
                  ) : (
                    <span className="text-xs font-medium" style={{ color: "var(--text-muted)" }}>Clean</span>
                  )}
                </td>
                <td className="px-3 py-2.5 font-mono text-xs" style={{ color: m.is_suspicious ? "var(--red)" : "var(--text-muted)" }}>
                  {m.anomaly_score.toFixed(4)}
                </td>
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 rounded-full" style={{ background: "var(--surface-2)" }}>
                      <div
                        className="h-1.5 rounded-full"
                        style={{
                          width: `${(m.confidence * 100).toFixed(0)}%`,
                          background: m.is_suspicious ? "#ef4444" : "#10b981",
                        }}
                      />
                    </div>
                    <span className="text-xs font-mono">{(m.confidence * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="px-3 py-2.5 text-xs font-mono" style={{ color: "var(--text-muted)" }}>
                  {m.bookmaker_count}
                </td>
                <td className="px-3 py-2.5 text-xs font-mono" style={{ color: m.spread_home > 0.03 ? "#f59e0b" : "var(--text-muted)" }}>
                  {(m.spread_home * 100).toFixed(2)}%
                </td>
                <td className="px-3 py-2.5">
                  <div className="flex flex-wrap gap-1">
                    {m.flags === "NONE"
                      ? <FlagBadge flag="NONE" />
                      : m.flags.split(",").map((f) => <FlagBadge key={f} flag={f} />)
                    }
                  </div>
                </td>
                <td className="px-3 py-2.5 text-xs font-mono whitespace-nowrap" style={{ color: "var(--text-muted)" }}>
                  {(m.prob_home * 100).toFixed(0)} /{" "}
                  {(m.prob_draw * 100).toFixed(0)} /{" "}
                  {(m.prob_away * 100).toFixed(0)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
