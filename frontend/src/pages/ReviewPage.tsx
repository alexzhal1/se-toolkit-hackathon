import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ReviewFlashcard } from "../api/client";
import Markdown from "../components/Markdown";

export default function ReviewPage() {
  const [queue, setQueue] = useState<ReviewFlashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [flipped, setFlipped] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [reviewedCount, setReviewedCount] = useState(0);

  const load = () => {
    setLoading(true);
    api
      .getReviewQueue()
      .then((q) => {
        setQueue(q);
        setFlipped(false);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const current = queue[0];

  const grade = async (quality: number) => {
    if (!current || submitting) return;
    setSubmitting(true);
    try {
      await api.reviewFlashcard(current.id, quality);
      setQueue((prev) => prev.slice(1));
      setFlipped(false);
      setReviewedCount((n) => n + 1);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Loading review queue...</p>
      </div>
    );
  }

  if (!current) {
    return (
      <div className="empty-state">
        <h2>All caught up! 🎉</h2>
        <p>
          {reviewedCount > 0
            ? `You reviewed ${reviewedCount} card${reviewedCount === 1 ? "" : "s"} this session.`
            : "No flashcards are due for review right now."}
        </p>
        <p style={{ marginTop: 12 }}>
          <Link to="/" className="btn btn-primary">
            Back to materials
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2>Review session</h2>
      <p style={{ color: "#94a3b8", marginBottom: 16 }}>
        {queue.length} card{queue.length === 1 ? "" : "s"} due • from{" "}
        <Link to={`/materials/${current.material_id}`}>{current.material_title}</Link>
      </p>

      <div className="flashcard-container">
        <div
          className={`flashcard ${flipped ? "flipped" : ""}`}
          onClick={() => setFlipped((f) => !f)}
        >
          <div className="flashcard-face flashcard-front">
            <Markdown>{current.front}</Markdown>
          </div>
          <div className="flashcard-face flashcard-back">
            <Markdown>{current.back}</Markdown>
          </div>
        </div>
      </div>

      {!flipped ? (
        <p style={{ textAlign: "center", marginTop: 16, color: "#64748b" }}>
          Click the card to reveal the answer
        </p>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: 8,
            marginTop: 16,
          }}
        >
          <button
            className="btn btn-secondary"
            disabled={submitting}
            onClick={() => grade(0)}
            style={{ background: "#7f1d1d" }}
          >
            Again
          </button>
          <button
            className="btn btn-secondary"
            disabled={submitting}
            onClick={() => grade(3)}
            style={{ background: "#92400e" }}
          >
            Hard
          </button>
          <button
            className="btn btn-secondary"
            disabled={submitting}
            onClick={() => grade(4)}
            style={{ background: "#166534" }}
          >
            Good
          </button>
          <button
            className="btn btn-secondary"
            disabled={submitting}
            onClick={() => grade(5)}
            style={{ background: "#0369a1" }}
          >
            Easy
          </button>
        </div>
      )}

      <p
        style={{
          textAlign: "center",
          marginTop: 16,
          fontSize: 12,
          color: "#64748b",
        }}
      >
        Reviewed this session: {reviewedCount} • EF {current.ease_factor.toFixed(2)} •
        reps {current.repetitions}
      </p>
    </div>
  );
}
