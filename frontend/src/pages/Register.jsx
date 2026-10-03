import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      await register(form);
      navigate("/menu", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="auth">
      <form className="auth-card stack" onSubmit={submit}>
        <h1 className="h2">Create your account</h1>
        <label>Full name<input value={form.name} onChange={set("name")} required minLength={2} /></label>
        <label>Email<input type="email" value={form.email} onChange={set("email")} required autoComplete="email" /></label>
        <label>Phone number<input type="tel" value={form.phone} onChange={set("phone")} required placeholder="98765 43210" /></label>
        <label>Password<input type="password" value={form.password} onChange={set("password")} required minLength={8} autoComplete="new-password" />
          <span className="muted small">At least 8 characters, with letters and numbers.</span></label>
        {error && <p className="error">{error}</p>}
        <button className="btn" disabled={busy}>{busy ? "Creating..." : "Register"}</button>
        <p className="muted small">Already registered? <Link to="/login">Log in</Link></p>
      </form>
    </div>
  );
}
