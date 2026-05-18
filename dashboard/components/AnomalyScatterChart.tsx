"use client";

import { Match } from "@/lib/types";
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Cell,
} from "recharts";

interface Props {
  matches: Match[];
}

const CustomDot = (props: { cx?: number; cy?: number; payload?: Match }) => {
  const { cx = 0, cy = 0, payload } = props;
  const suspicious = payload?.is_suspicious;
  return (
    <circle
      cx={cx} cy={cy} r={suspicious ? 7 : 5}
      fill={suspicious ? "#ef4444" : "#3b82f6"}
      fillOpacity={suspicious ? 0.9 : 0.6}
      stroke={suspicious ? "#fca5a5" : "transparent"}
      strokeWidth={1.5}
    />
  );
};

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: Match }> }) => {
  if (!active || !payload?.length) return null;
  const m = payload[0].payload;
  return (
    <div className="card p-3 text-xs" style={{ minWidth: 180 }}>
      <p className="font-semibold mb-1">{m.home_team} vs {m.away_team}</p>
      <p style={{ color: "var(--text-muted)" }}>Anomaly: <span className="text-white">{m.anomaly_score.toFixed(4)}</span></p>
      <p style={{ color: "var(--text-muted)" }}>Confidence: <span className="text-white">{(m.confidence * 100).toFixed(0)}%</span></p>
      <p style={{ color: "var(--text-muted)" }}>Home Spread: <span className="text-white">{(m.spread_home * 100).toFixed(2)}%</span></p>
      {m.is_suspicious && (
        <p className="mt-1 text-red-400 font-semibold">⚠ Flagged suspicious</p>
      )}
    </div>
  );
};

export default function AnomalyScatterChart({ matches }: Props) {
  const data = matches.map((m) => ({
    ...m,
    x: m.anomaly_score,
    y: m.confidence * 100,
  }));

  return (
    <div className="card p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold">Anomaly Score vs Confidence</h2>
        <div className="flex items-center gap-4 text-xs" style={{ color: "var(--text-muted)" }}>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500" /> Suspicious
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500" /> Clean
          </span>
        </div>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a38" />
            <XAxis
              dataKey="x" type="number" name="Anomaly Score"
              tick={{ fill: "#64748b", fontSize: 11 }}
              label={{ value: "Anomaly Score →", position: "insideBottom", offset: -10, fill: "#64748b", fontSize: 11 }}
            />
            <YAxis
              dataKey="y" type="number" name="Confidence %" unit="%"
              tick={{ fill: "#64748b", fontSize: 11 }}
            />
            <ReferenceLine
              x={-0.5}
              stroke="#ef4444" strokeDasharray="4 4" strokeOpacity={0.5}
              label={{ value: "Suspicious threshold", fill: "#ef4444", fontSize: 10, position: "insideTopLeft" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Scatter data={data} shape={<CustomDot />}>
              {data.map((entry) => (
                <Cell key={entry.match_id} fill={entry.is_suspicious ? "#ef4444" : "#3b82f6"} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
