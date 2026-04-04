import { useEffect, useState } from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import { api, User } from "./api/client";
import HomePage from "./pages/HomePage";
import UploadPage from "./pages/UploadPage";
import MaterialPage from "./pages/MaterialPage";
import FlashcardsPage from "./pages/FlashcardsPage";
import ChatPage from "./pages/ChatPage";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Simple auth: use a stored or generated user ID
    const storedId = localStorage.getItem("studybot_telegram_id");
    const telegramId = storedId ? parseInt(storedId) : Math.floor(Math.random() * 1_000_000_000);

    if (!storedId) {
      localStorage.setItem("studybot_telegram_id", String(telegramId));
    }

    api
      .auth(telegramId, "Student")
      .then(setUser)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Loading...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container">
        <p>Failed to connect. Please refresh the page.</p>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <Link to="/" style={{ textDecoration: "none" }}>
          <h1>StudyBot</h1>
        </Link>
        <nav>
          <Link to="/" className="btn btn-secondary">
            Materials
          </Link>
          <Link to="/upload" className="btn btn-primary">
            + Upload
          </Link>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<HomePage userId={user.id} />} />
        <Route
          path="/upload"
          element={<UploadPage userId={user.id} onCreated={() => navigate("/")} />}
        />
        <Route path="/materials/:id" element={<MaterialPage />} />
        <Route path="/materials/:id/flashcards" element={<FlashcardsPage />} />
        <Route path="/materials/:id/chat" element={<ChatPage />} />
      </Routes>
    </div>
  );
}
