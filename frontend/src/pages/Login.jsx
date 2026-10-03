import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      const user = await login(form.email, form.password);
      navigate(location.state?.from || (user.role === "admin" ? "/admin" : "/"), { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="auth">
      <form className="auth-card stack" onSubmit={submit}>
        <h1 className="h2">Welcome back</h1>
        <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required autoComplete="email" /></label>
        <label>Password<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required autoComplete="current-password" /></label>
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy}>{busy ? "Logging in..." : "Login"}</button>
        <p className="muted small">New here? <Link to="/register">Create an account</Link></p>
      </form>
    </div>
  );
}
