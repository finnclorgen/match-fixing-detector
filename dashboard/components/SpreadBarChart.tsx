"use client";

import { Match } from "@/lib/types";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Cell, Legend,
} from "recharts";

interface Props {
  matches: Match[];
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number }>; label?: string }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="card p-3 text-xs">
      <p className="font-semibold mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: "var(--text-muted)" }}>
          {p.name}: <span className="text-white">{p.value.toFixed(2)}%</span>
        </p>
      ))}
    </div>
  );
};

export default function SpreadBarChart({ matches }: Props) {
  const data = [...matches]
    .sort((a, b) => b.spread_home - a.spread_home)
    .map((m) => ({
      name: `${m.home_team.split(" ")[0]} v ${m.away_team.split(" ")[0]}`,
      "Home Spread": +(m.spread_home * 100).toFixed(3),
      "Away Spread": +(m.spread_away * 100).toFixed(3),
      "Draw Spread": +(m.spread_draw * 100).toFixed(3),
      suspicious: m.is_suspicious,
    }));

  return (
    <div className="card p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">Bookmaker Spread by Match</h2>
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>sorted by home spread</span>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 10, bottom: 60, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a38" vertical={false} />
            <XAxis
              dataKey="name"
              tick={{ fill: "#64748b", fontSize: 10 }}
              angle={-40}
              textAnchor="end"
              interval={0}
            />
            <YAxis tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
            <ReferenceLine y={3} stroke="#f59e0b" strokeDasharray="4 4" strokeOpacity={0.6}
              label={{ value: "3% threshold", fill: "#f59e0b", fontSize: 10, position: "insideTopRight" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11, color: "#64748b", paddingTop: 8 }} />
            <Bar dataKey="Home Spread" radius={[3, 3, 0, 0]}>
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.suspicious ? "#ef4444" : "#3b82f6"} fillOpacity={entry.suspicious ? 0.9 : 0.7} />
              ))}
            </Bar>
            <Bar dataKey="Away Spread" fill="#8b5cf6" fillOpacity={0.7} radius={[3, 3, 0, 0]} />
            <Bar dataKey="Draw Spread" fill="#6b7280" fillOpacity={0.5} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
