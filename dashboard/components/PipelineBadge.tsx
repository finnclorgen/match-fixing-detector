"use client";

const STAGES = [
  { n: "1", label: "Fetch Odds", desc: "Live bookmaker data via The Odds API" },
  { n: "2", label: "Anomaly Detection", desc: "Isolation Forest on 7-feature vector" },
  { n: "3", label: "Classify & Flag", desc: "Rule-based flags + confidence scoring" },
  { n: "4", label: "Report", desc: "Ranked JSON output" },
];

export default function PipelineBadge() {
  return (
    <div className="card px-5 py-4">
      <h2 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--text-muted)" }}>
        Pipeline
      </h2>
      <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
        {STAGES.map((s, i) => (
          <div key={s.n} className="flex items-center gap-2">
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-red-600 flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0">
                  {s.n}
                </span>
                <span className="text-xs font-semibold">{s.label}</span>
              </div>
              <span className="text-[10px] pl-7" style={{ color: "var(--text-muted)" }}>{s.desc}</span>
            </div>
            {i < STAGES.length - 1 && (
              <span className="hidden sm:block text-xl font-thin mx-1" style={{ color: "var(--border)" }}>→</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
