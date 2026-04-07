import { useEffect, useState } from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import { api, User } from "./api/client";
import HomePage from "./pages/HomePage";
import UploadPage from "./pages/UploadPage";
import MaterialPage from "./pages/MaterialPage";
import FlashcardsPage from "./pages/FlashcardsPage";
import ChatPage from "./pages/ChatPage";
import QuizPage from "./pages/QuizPage";
import LoginPage from "./pages/LoginPage";
import ReviewPage from "./pages/ReviewPage";
import StatsPage from "./pages/StatsPage";

const STORAGE_KEY = "studybot_user";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (u: User) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
    setUser(u);
    navigate("/");
  };

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
    navigate("/");
  };

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
        <header className="header">
          <h1>StudyBot</h1>
        </header>
        <LoginPage onLogin={handleLogin} />
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
          <Link to="/review" className="btn btn-secondary">
            Review
          </Link>
          <Link to="/stats" className="btn btn-secondary">
            Stats
          </Link>
          <Link to="/upload" className="btn btn-primary">
            + Upload
          </Link>
          <button className="btn btn-secondary" onClick={handleLogout}>
            Logout
          </button>
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
        <Route path="/materials/:id/quiz" element={<QuizPage userId={user.id} />} />
        <Route path="/review" element={<ReviewPage userId={user.id} />} />
        <Route path="/stats" element={<StatsPage userId={user.id} />} />
      </Routes>
    </div>
  );
}
