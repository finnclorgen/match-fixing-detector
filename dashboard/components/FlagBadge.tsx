"use client";

const FLAG_COLORS: Record<string, string> = {
  HIGH_BOOKMAKER_DISAGREEMENT: "bg-red-900/60 text-red-300 border-red-700",
  LARGE_HOME_LINE_RANGE: "bg-orange-900/60 text-orange-300 border-orange-700",
  LARGE_AWAY_LINE_RANGE: "bg-orange-900/60 text-orange-300 border-orange-700",
  EXTREME_FAVORITE: "bg-blue-900/60 text-blue-300 border-blue-700",
  LOW_MARKET_COVERAGE: "bg-yellow-900/60 text-yellow-300 border-yellow-700",
  NONE: "bg-zinc-800/60 text-zinc-400 border-zinc-700",
};

export default function FlagBadge({ flag }: { flag: string }) {
  const cls = FLAG_COLORS[flag.trim()] ?? "bg-zinc-800/60 text-zinc-400 border-zinc-700";
  const label = flag.trim().replace(/_/g, " ");
  return (
    <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded border ${cls}`}>
      {label}
    </span>
  );
}
