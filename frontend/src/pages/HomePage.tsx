import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Material } from "../api/client";

export default function HomePage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getMaterials()
      .then(setMaterials)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Loading materials...</p>
      </div>
    );
  }

  if (materials.length === 0) {
    return (
      <div className="empty-state">
        <h2>No materials yet</h2>
        <p>Upload your first study material to get started.</p>
        <Link to="/upload" className="btn btn-primary" style={{ marginTop: 16 }}>
          + Upload Material
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}>Your Materials</h2>
      {materials.map((m) => (
        <Link
          key={m.id}
          to={`/materials/${m.id}`}
          style={{ textDecoration: "none", color: "inherit" }}
        >
          <div className="card">
            <h3>{m.title}</h3>
            <p>{m.content.substring(0, 150)}...</p>
            <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
              {m.explanation && (
                <span style={{ fontSize: 12, color: "#10b981" }}>Explained</span>
              )}
              <span style={{ fontSize: 12, color: "#64748b" }}>
                {new Date(m.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
