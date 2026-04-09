import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, UserStats } from "../api/client";

export default function StatsPage() {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Loading stats...</p>
      </div>
    );
  }

  if (!stats) {
    return <p>Failed to load stats.</p>;
  }

  const tile = (label: string, value: string | number, sub?: string) => (
    <div className="card" style={{ padding: 16 }}>
      <div style={{ fontSize: 12, color: "#94a3b8", textTransform: "uppercase" }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, marginTop: 4 }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>{sub}</div>}
    </div>
  );

  return (
    <div>
      <h2>Your progress</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: 12,
          marginTop: 16,
        }}
      >
        {tile("Materials", stats.materials_count)}
        {tile(
          "Flashcards",
          stats.flashcards_count,
          `${stats.flashcards_learned} learned`
        )}
        {tile("Due now", stats.flashcards_due, "ready to review")}
        {tile("Quiz attempts", stats.quiz_attempts)}
        {tile("Avg quiz score", `${stats.quiz_avg_pct}%`)}
      </div>

      {stats.flashcards_due > 0 && (
        <div style={{ marginTop: 16 }}>
          <Link to="/review" className="btn btn-primary">
            Review {stats.flashcards_due} card{stats.flashcards_due === 1 ? "" : "s"} now
          </Link>
        </div>
      )}

      <h3 style={{ marginTop: 32 }}>Recent quiz attempts</h3>
      {stats.recent_attempts.length === 0 ? (
        <p style={{ color: "#94a3b8" }}>No quiz attempts yet.</p>
      ) : (
        <div className="card">
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", color: "#94a3b8", fontSize: 12 }}>
                <th style={{ padding: "8px 0" }}>When</th>
                <th>Quiz</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_attempts.map((a, i) => {
                const pct = a.total > 0 ? Math.round((a.score / a.total) * 100) : 0;
                return (
                  <tr key={i} style={{ borderTop: "1px solid #1e293b" }}>
                    <td style={{ padding: "8px 0" }}>
                      {new Date(a.completed_at).toLocaleString()}
                    </td>
                    <td>#{a.quiz_id}</td>
                    <td>
                      {a.score}/{a.total} ({pct}%)
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
