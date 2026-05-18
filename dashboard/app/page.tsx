"use client";

import { useState, useEffect } from "react";
import { Report } from "@/lib/types";
import SummaryCards from "@/components/SummaryCards";
import FlaggedMatchCard from "@/components/FlaggedMatchCard";
import MatchTable from "@/components/MatchTable";
import AnomalyScatterChart from "@/components/AnomalyScatterChart";
import SpreadBarChart from "@/components/SpreadBarChart";
import PipelineBadge from "@/components/PipelineBadge";

type DataSource = "live" | "demo";

export default function Dashboard() {
  const [source, setSource] = useState<DataSource>("live");
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const file = source === "live" ? "/data/report.json" : "/data/demo_report.json";
    fetch(file)
      .then((r) => r.json())
      .then((data: Report) => { setReport(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [source]);

  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      {/* Nav */}
      <header className="sticky top-0 z-10 border-b" style={{ background: "rgba(10,10,15,0.85)", backdropFilter: "blur(12px)", borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-red-500 text-xl">⚑</span>
            <span className="font-bold tracking-tight">Match-Fixing Detector</span>
            <span className="hidden sm:inline text-xs px-2 py-0.5 rounded-full border font-medium" style={{ color: "var(--text-muted)", borderColor: "var(--border)" }}>
              EPL · Isolation Forest
            </span>
          </div>
          <div className="flex items-center gap-1 p-1 rounded-lg" style={{ background: "var(--surface-2)" }}>
            {(["live", "demo"] as DataSource[]).map((s) => (
              <button
                key={s}
                onClick={() => setSource(s)}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                  source === s
                    ? "bg-red-600 text-white shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {s === "live" ? "Live EPL" : "Demo Data"}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-8">
        {/* Pipeline banner */}
        <PipelineBadge />

        {loading && (
          <div className="flex items-center justify-center py-24">
            <div className="w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && !report && (
          <div className="card p-8 text-center" style={{ color: "var(--text-muted)" }}>
            Failed to load report data.
          </div>
        )}

        {!loading && report && (
          <>
            {/* Summary */}
            <section>
              <SectionHeading>Overview</SectionHeading>
              <SummaryCards report={report} />
            </section>

            {/* Flagged matches */}
            {report.flagged_matches.length > 0 && (
              <section>
                <SectionHeading>
                  Flagged Matches
                  <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-red-900/60 text-red-300 border border-red-800 font-normal">
                    {report.flagged_matches.length} suspicious
                  </span>
                </SectionHeading>
                <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {report.flagged_matches.map((m, i) => (
                    <FlaggedMatchCard key={m.match_id} match={m} rank={i + 1} />
                  ))}
                </div>
              </section>
            )}

            {report.flagged_matches.length === 0 && (
              <div className="card p-8 text-center">
                <p className="text-2xl mb-2">✓</p>
                <p className="font-semibold" style={{ color: "var(--green)" }}>No suspicious matches detected</p>
                <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>All {report.total_matches_analyzed} matches appear normal</p>
              </div>
            )}

            {/* Charts */}
            <section>
              <SectionHeading>Anomaly Analysis</SectionHeading>
              <div className="grid lg:grid-cols-2 gap-4">
                <AnomalyScatterChart matches={report.all_matches} />
                <SpreadBarChart matches={report.all_matches} />
              </div>
            </section>

            {/* Full table */}
            <section>
              <SectionHeading>All Matches</SectionHeading>
              <MatchTable matches={report.all_matches} />
            </section>

            {/* Footer */}
            <p className="text-center text-xs pb-4" style={{ color: "var(--text-muted)" }}>
              Report generated {new Date(report.generated_at).toLocaleString()} · {report.sport}
            </p>
          </>
        )}
      </main>
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-sm font-semibold uppercase tracking-wider mb-3 flex items-center gap-2" style={{ color: "var(--text-muted)" }}>
      {children}
    </h2>
  );
}
