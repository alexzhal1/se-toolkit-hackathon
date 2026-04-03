import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, Flashcard } from "../api/client";

export default function FlashcardsPage() {
  const { id } = useParams<{ id: string }>();
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [current, setCurrent] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const materialId = parseInt(id || "0");

  useEffect(() => {
    api
      .getFlashcards(materialId)
      .then((c) => {
        setCards(c);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [materialId]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const newCards = await api.generateFlashcards(materialId);
      setCards(newCards);
      setCurrent(0);
      setFlipped(false);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const prev = () => {
    setFlipped(false);
    setCurrent((c) => (c > 0 ? c - 1 : cards.length - 1));
  };

  const next = () => {
    setFlipped(false);
    setCurrent((c) => (c < cards.length - 1 ? c + 1 : 0));
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Loading flashcards...</p>
      </div>
    );
  }

  return (
    <div>
      <Link to={`/materials/${materialId}`} className="back-link">
        &larr; Back to material
      </Link>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h2>Flashcards</h2>
        <button className="btn btn-primary" onClick={handleGenerate} disabled={generating}>
          {generating ? "Generating..." : cards.length > 0 ? "Regenerate" : "Generate Flashcards"}
        </button>
      </div>

      {generating && (
        <div className="loading">
          <div className="spinner" />
          <p>AI is creating flashcards...</p>
        </div>
      )}

      {!generating && cards.length === 0 && (
        <div className="empty-state">
          <h2>No flashcards yet</h2>
          <p>Click "Generate Flashcards" to create them from your study material.</p>
        </div>
      )}

      {!generating && cards.length > 0 && (
        <>
          <div className="flashcard-container">
            <div
              className={`flashcard ${flipped ? "flipped" : ""}`}
              onClick={() => setFlipped(!flipped)}
            >
              <div className="flashcard-face flashcard-front">
                {cards[current].front}
              </div>
              <div className="flashcard-face flashcard-back">
                {cards[current].back}
              </div>
            </div>
          </div>

          <div className="flashcard-nav">
            <button className="btn btn-secondary" onClick={prev}>
              &larr; Prev
            </button>
            <span className="flashcard-counter">
              {current + 1} / {cards.length}
            </span>
            <button className="btn btn-secondary" onClick={next}>
              Next &rarr;
            </button>
          </div>

          <p style={{ textAlign: "center", marginTop: 12, fontSize: 13, color: "#64748b" }}>
            Click the card to flip it
          </p>
        </>
      )}
    </div>
  );
}
