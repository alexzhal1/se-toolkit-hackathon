import { useState } from "react";
import { api } from "../api/client";

interface Props {
  userId: number;
  onCreated: () => void;
}

export default function UploadPage({ userId, onCreated }: Props) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      setError("Please enter some study material.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      await api.createMaterial(userId, title || content.substring(0, 50), content);
      onCreated();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>Upload Study Material</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Title (optional)</label>
          <input
            id="title"
            type="text"
            placeholder="e.g. Chapter 5: Photosynthesis"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="content">Study Material *</label>
          <textarea
            id="content"
            rows={12}
            placeholder="Paste your study material here..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>

        {error && <p style={{ color: "#ef4444", marginBottom: 12 }}>{error}</p>}

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Saving..." : "Save Material"}
        </button>
      </form>
    </div>
  );
}
