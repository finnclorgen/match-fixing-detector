import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Match-Fixing Detection Dashboard",
  description: "EPL odds anomaly detection — suspicion ranking and bookmaker divergence analysis",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
