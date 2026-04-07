import { useState } from "react";
import { api, User } from "../api/client";

export default function LoginPage({ onLogin }: { onLogin: (user: User) => void }) {
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token.trim()) return;
    setLoading(true);
    setError("");
    try {
      const user = await api.loginWithToken(token.trim());
      onLogin(user);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: "60px auto" }}>
      <h2 style={{ marginBottom: 8 }}>Log in with Telegram</h2>
      <p style={{ color: "#94a3b8", marginBottom: 24, lineHeight: 1.6 }}>
        1. Open the StudyBot Telegram bot and send <code style={{ background: "#1e293b", padding: "2px 6px", borderRadius: 4 }}>/login</code>
        <br />
        2. Copy the code the bot gives you
        <br />
        3. Paste it below
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="token">Login code</label>
          <input
            id="token"
            type="text"
            placeholder="Paste your code here"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            autoFocus
          />
        </div>

        {error && <p style={{ color: "#ef4444", marginBottom: 12 }}>{error}</p>}

        <button type="submit" className="btn btn-primary" disabled={loading || !token.trim()}>
          {loading ? "Logging in..." : "Log in"}
        </button>
      </form>
    </div>
  );
}
