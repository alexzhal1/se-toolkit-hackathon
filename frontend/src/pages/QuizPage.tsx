import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, Quiz } from "../api/client";
import Markdown from "../components/Markdown";

export default function QuizPage() {
  const { id } = useParams<{ id: string }>();
  const materialId = parseInt(id || "0");
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [answers, setAnswers] = useState<Record<number, number[]>>({});
  const [submitted, setSubmitted] = useState(false);

  const arraysEqual = (a: number[], b: number[]) => {
    if (a.length !== b.length) return false;
    const sa = [...a].sort((x, y) => x - y);
    const sb = [...b].sort((x, y) => x - y);
    return sa.every((v, i) => v === sb[i]);
  };

  useEffect(() => {
    api
      .getQuiz(materialId)
      .then((q) => setQuiz(q))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [materialId]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const newQuiz = await api.generateQuiz(materialId);
      setQuiz(newQuiz);
      setAnswers({});
      setSubmitted(false);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleSelect = (questionId: number, optionIndex: number, isMulti: boolean) => {
    if (submitted) return;
    setAnswers((prev) => {
      const current = prev[questionId] || [];
      if (isMulti) {
        const next = current.includes(optionIndex)
          ? current.filter((i) => i !== optionIndex)
          : [...current, optionIndex];
        return { ...prev, [questionId]: next };
      }
      return { ...prev, [questionId]: [optionIndex] };
    });
  };

  const handleSubmit = async () => {
    if (!quiz) return;
    setSubmitted(true);
    try {
      await api.submitQuiz(quiz.id, answers);
    } catch (err) {
      console.error("Failed to record quiz attempt", err);
    }
  };

  const handleReset = () => {
    setAnswers({});
    setSubmitted(false);
  };

  const score = quiz
    ? quiz.questions.filter((q) => arraysEqual(answers[q.id] || [], q.correct_answer_indices)).length
    : 0;

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Loading quiz...</p>
      </div>
    );
  }

  return (
    <div>
      <Link to={`/materials/${materialId}`} className="back-link">
        &larr; Back to material
      </Link>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2>Quiz</h2>
        <button className="btn btn-primary" onClick={handleGenerate} disabled={generating}>
          {generating ? "Generating..." : quiz ? "Regenerate" : "Generate Quiz"}
        </button>
      </div>

      {generating && (
        <div className="loading">
          <div className="spinner" />
          <p>AI is creating questions, this may take a minute...</p>
        </div>
      )}

      {!generating && !quiz && (
        <div className="empty-state">
          <h2>No quiz yet</h2>
          <p>Click "Generate Quiz" to create one from your study material.</p>
        </div>
      )}

      {!generating && quiz && (
        <div>
          {submitted && (
            <div className="card" style={{ background: "#0f3a2e", borderColor: "#10b981" }}>
              <h3>Score: {score} / {quiz.questions.length}</h3>
              <p>{score === quiz.questions.length ? "Perfect!" : "Review the explanations below."}</p>
              <button className="btn btn-secondary" onClick={handleReset} style={{ marginTop: 12 }}>
                Try again
              </button>
            </div>
          )}

          {quiz.questions.map((q, i) => {
            const userAnswer = answers[q.id] || [];
            const isCorrect = arraysEqual(userAnswer, q.correct_answer_indices);

            return (
              <div key={q.id} className="card">
                <h3 style={{ marginBottom: 4 }}>
                  {i + 1}. <Markdown>{q.question_text}</Markdown>
                </h3>
                {q.is_multi && (
                  <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>
                    Multiple answers — select all that apply
                  </p>
                )}

                <div className="quiz-options">
                  {q.options.map((opt, idx) => {
                    const selected = userAnswer.includes(idx);
                    const isCorrectOpt = q.correct_answer_indices.includes(idx);
                    let className = "quiz-option";
                    if (submitted) {
                      if (isCorrectOpt) className += " correct";
                      else if (selected) className += " wrong";
                    } else if (selected) {
                      className += " selected";
                    }
                    const marker = q.is_multi
                      ? selected ? "☑" : "☐"
                      : selected ? "●" : "○";
                    return (
                      <button
                        key={idx}
                        className={className}
                        onClick={() => handleSelect(q.id, idx, q.is_multi)}
                        disabled={submitted}
                      >
                        <span className="quiz-option-letter">
                          {marker} {String.fromCharCode(65 + idx)}.
                        </span>
                        <span><Markdown>{opt}</Markdown></span>
                      </button>
                    );
                  })}
                </div>

                {submitted && q.explanation && (
                  <div className="quiz-explanation" style={{ marginTop: 12 }}>
                    <strong>{isCorrect ? "✓ Correct" : "✗ Incorrect"}.</strong>{" "}
                    <Markdown>{q.explanation}</Markdown>
                  </div>
                )}
              </div>
            );
          })}

          {!submitted && (
            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={quiz.questions.some((q) => !(answers[q.id] && answers[q.id].length > 0))}
              style={{ marginTop: 16 }}
            >
              Submit
            </button>
          )}
        </div>
      )}
    </div>
  );
}
