import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { api, inr, STATUS_LABELS } from "../services/api.js";

export default function MyOrders() {
  const { user } = useAuth();
  const [orders, setOrders] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api.myOrders().then(setOrders).catch((e) => setError(e.message)); }, []);
  return (
    <div className="container page narrow">
      <h1 className="h1">My Profile</h1>
      <div className="profile">
        <div><span className="muted small">Name</span><strong>{user.name}</strong></div>
        <div><span className="muted small">Email</span><strong>{user.email}</strong></div>
        <div><span className="muted small">Phone</span><strong>{user.phone}</strong></div>
      </div>
      <h2 className="h3">Order History</h2>
      {error && <p className="error">{error}</p>}
      {orders && orders.length === 0 && <p>No orders yet. <Link to="/menu">Order now</Link></p>}
      <div className="stack">
        {orders?.map((o) => (
          <article key={o.id} className="order">
            <header className="row"><strong>{o.order_number}</strong><span className={`pill s-${o.order_status}`}>{STATUS_LABELS[o.order_status]}</span></header>
            <ul className="muted">{o.items.map((i) => <li key={i.id}>{i.quantity} × {i.item_name}</li>)}</ul>
            <footer className="row small"><span>{new Date(o.created_at + "Z").toLocaleString("en-IN")}</span><strong>{inr(o.total_amount)}</strong></footer>
          </article>
        ))}
      </div>
    </div>
  );
}
