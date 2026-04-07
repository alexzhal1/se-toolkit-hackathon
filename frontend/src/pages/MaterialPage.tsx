import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api, Material } from "../api/client";
import Markdown from "../components/Markdown";

export default function MaterialPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [material, setMaterial] = useState<Material | null>(null);
  const [loading, setLoading] = useState(true);
  const [explaining, setExplaining] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!id) return;
    api
      .getMaterial(parseInt(id))
      .then(setMaterial)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  const handleExplain = async () => {
    if (!material) return;
    setExplaining(true);
    try {
      const updated = await api.explainMaterial(material.id);
      setMaterial(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setExplaining(false);
    }
  };

  const handleDelete = async () => {
    if (!material || !confirm("Are you sure you want to delete this material?")) return;
    setDeleting(true);
    try {
      await api.deleteMaterial(material.id);
      navigate("/");
    } catch (err) {
      console.error(err);
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Loading material...</p>
      </div>
    );
  }

  if (!material) {
    return <p>Material not found.</p>;
  }

  return (
    <div>
      <Link to="/" className="back-link">
        &larr; Back to materials
      </Link>

      <h2 style={{ marginBottom: 8 }}>{material.title}</h2>
      <p style={{ fontSize: 12, color: "#64748b", marginBottom: 16 }}>
        {new Date(material.created_at).toLocaleString()}
      </p>

      <h3 style={{ marginBottom: 8 }}>Original Material</h3>
      <div className="material-content">{material.content}</div>

      <div className="actions">
        <button
          className="btn btn-primary"
          onClick={handleExplain}
          disabled={explaining}
        >
          {explaining
            ? "Generating explanation..."
            : material.explanation
            ? "Re-explain"
            : "Explain with AI"}
        </button>

        <Link to={`/materials/${material.id}/flashcards`} className="btn btn-secondary">
          Flashcards
        </Link>

        <Link to={`/materials/${material.id}/chat`} className="btn btn-secondary">
          Ask AI
        </Link>

        <Link to={`/materials/${material.id}/quiz`} className="btn btn-secondary">
          Quiz
        </Link>

        <button className="btn btn-danger" onClick={handleDelete} disabled={deleting}>
          {deleting ? "Deleting..." : "Delete"}
        </button>
      </div>

      {material.explanation && (
        <div style={{ marginTop: 24 }}>
          <h3 style={{ marginBottom: 8 }}>AI Explanation</h3>
          <div className="explanation">
            <Markdown>{material.explanation}</Markdown>
          </div>
        </div>
      )}
    </div>
  );
}
