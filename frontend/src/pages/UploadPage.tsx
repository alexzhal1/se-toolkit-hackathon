import { useState, useRef } from "react";
import { api } from "../api/client";

interface Props {
  userId: number;
  onCreated: () => void;
}

export default function UploadPage({ userId, onCreated }: Props) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file && !content.trim()) {
      setError("Please enter text or upload a file.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      if (file) {
        await api.uploadFile(userId, title, file);
      } else {
        await api.createMaterial(userId, title || content.substring(0, 50), content);
      }
      onCreated();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      const ext = selected.name.split(".").pop()?.toLowerCase();
      if (ext !== "pdf" && ext !== "docx") {
        setError("Only .pdf and .docx files are supported.");
        return;
      }
      setFile(selected);
      setContent("");
      setError("");
    }
  };

  const clearFile = () => {
    setFile(null);
    if (fileRef.current) fileRef.current.value = "";
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
          <label>Upload File (.pdf, .docx)</label>
          <div className="file-upload-area">
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              id="file-input"
              style={{ display: "none" }}
            />
            {file ? (
              <div className="file-selected">
                <span>{file.name}</span>
                <button type="button" className="btn btn-secondary" onClick={clearFile} style={{ padding: "4px 12px", fontSize: 12 }}>
                  Remove
                </button>
              </div>
            ) : (
              <label htmlFor="file-input" className="file-drop-label">
                Click to select a .pdf or .docx file
              </label>
            )}
          </div>
        </div>

        {!file && (
          <div className="form-group">
            <label htmlFor="content">Or paste text directly</label>
            <textarea
              id="content"
              rows={12}
              placeholder="Paste your study material here..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>
        )}

        {error && <p style={{ color: "#ef4444", marginBottom: 12 }}>{error}</p>}

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Uploading..." : "Save Material"}
        </button>
      </form>
    </div>
  );
}
