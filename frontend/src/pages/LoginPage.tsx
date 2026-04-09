import { useState } from "react";
import { api, User } from "../api/client";

type Mode = "login" | "register";

export default function LoginPage({
  onLogin,
}: {
  onLogin: (user: User, token: string) => void;
}) {
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (mode === "register") {
        const res = await api.register(email.trim(), login.trim(), password);
        onLogin(res.user, res.token);
      } else {
        const res = await api.login(login.trim(), password);
        onLogin(res.user, res.token);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: "60px auto" }}>
      <h2 style={{ marginBottom: 24 }}>
        {mode === "login" ? "Log In" : "Sign Up"}
      </h2>

      {/* Toggle */}
      <div style={{ marginBottom: 24, display: "flex", gap: 8 }}>
        <button
          className={`btn ${mode === "login" ? "btn-primary" : "btn-secondary"}`}
          onClick={() => {
            setMode("login");
            setError("");
          }}
          type="button"
        >
          Log In
        </button>
        <button
          className={`btn ${mode === "register" ? "btn-primary" : "btn-secondary"}`}
          onClick={() => {
            setMode("register");
            setError("");
          }}
          type="button"
        >
          Sign Up
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {mode === "register" && (
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="login">{mode === "register" ? "Username" : "Username or Email"}</label>
          <input
            id="login"
            type="text"
            placeholder={mode === "register" ? "username" : "username or email"}
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            required
            autoFocus={mode !== "register"}
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {error && <p style={{ color: "#ef4444", marginBottom: 12 }}>{error}</p>}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || (mode === "register" && !email.trim()) || !login.trim() || !password.trim()}
        >
          {loading ? (mode === "login" ? "Logging in..." : "Creating account...") : (mode === "login" ? "Log In" : "Sign Up")}
        </button>
      </form>
    </div>
  );
}
