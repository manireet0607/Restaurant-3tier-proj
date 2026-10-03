import React, { useCallback, useEffect, useState } from "react";
import { useMenu } from "../hooks/useMenu.js";
import { api, inr, NEXT_STATUSES, STATUS_LABELS } from "../services/api.js";

const blankItem = (categoryId) => ({ category_id: categoryId || "", name: "", description: "", price: "", image_url: "", food_type: "veg", is_available: true });

export default function Admin() {
  const [tab, setTab] = useState("overview");
  const [msg, setMsg] = useState({ type: "", text: "" });
  const { categories, items, reload } = useMenu();
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [open, setOpen] = useState(null);
  const [item, setItem] = useState(null);
  const [cat, setCat] = useState(null);

  const loadAdmin = useCallback(async () => {
    try {
      const [s, o] = await Promise.all([api.adminStats(), api.adminOrders()]);
      setStats(s); setOrders(o);
    } catch (e) { setMsg({ type: "error", text: e.message }); }
  }, []);
  useEffect(() => { loadAdmin(); }, [loadAdmin]);

  // Runs an action, shows the result, and refreshes the data.
  const run = async (fn, ok) => {
    try { await fn(); setMsg({ type: "ok", text: ok }); await Promise.all([reload(), loadAdmin()]); return true; }
    catch (e) { setMsg({ type: "error", text: e.message }); return false; }
  };

  return (
    <div className="container page">
      <h1 className="h1">Admin Dashboard</h1>
      <div className="tabs">
        {["overview", "orders", "menu", "categories"].map((t) => (
          <button key={t} className={`tab ${tab === t ? "on" : ""}`} onClick={() => { setTab(t); setMsg({ type: "", text: "" }); }}>{t}</button>
        ))}
      </div>
      {msg.text && <p className={msg.type === "error" ? "error" : "okmsg"}>{msg.text}</p>}

      {tab === "overview" && (
        <div className="stats">
          <div className="stat"><span>Total orders</span><strong>{stats?.total_orders ?? "-"}</strong></div>
          <div className="stat"><span>Revenue</span><strong>{stats ? inr(stats.revenue) : "-"}</strong></div>
          <div className="stat"><span>Customers</span><strong>{stats?.customers ?? "-"}</strong></div>
          <div className="stat"><span>Menu items</span><strong>{stats?.menu_items ?? "-"}</strong></div>
        </div>
      )}

      {tab === "orders" && (
        <div className="stack">
          {orders.length === 0 && <p>No orders yet.</p>}
          {orders.map((o) => (
            <article key={o.id} className="panel">
              <div className="row wrap">
                <button className="linkbtn" onClick={() => setOpen(open === o.id ? null : o.id)}>{o.order_number}</button>
                <span className={`pill s-${o.order_status}`}>{STATUS_LABELS[o.order_status]}</span>
                <strong>{inr(o.total_amount)}</strong>
              </div>
              {open === o.id && (
                <div className="detail">
                  <p><strong>{o.customer_name}</strong> · {o.customer_phone}</p>
                  <p>{o.delivery_address}</p>
                  {o.special_instructions && <p><em>Note: {o.special_instructions}</em></p>}
                  <ul>{o.items.map((i) => <li key={i.id}>{i.quantity} × {i.item_name} ({inr(i.unit_price)})</li>)}</ul>
                  <p className="muted small">Payment: {o.payment_method.toUpperCase()} ({o.payment_status})</p>
                </div>
              )}
              <div className="actions">
                {NEXT_STATUSES[o.order_status].map((s) => (
                  <button key={s} className={`btn btn-sm ${s === "cancelled" ? "btn-danger" : ""}`}
                    onClick={() => run(() => api.adminSetStatus(o.id, s), "Order updated")}>
                    {s === "cancelled" ? "Cancel order" : `Mark ${STATUS_LABELS[s]}`}
                  </button>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}

      {tab === "menu" && (
        <div className="stack">
          <div><button className="btn" onClick={() => setItem(blankItem(categories[0]?.id))} disabled={!categories.length}>Add food item</button></div>
          {item && (
            <form className="panel stack" onSubmit={async (e) => { e.preventDefault(); if (await run(() => api.adminSaveItem(item), "Saved")) setItem(null); }}>
              <label>Name<input value={item.name} onChange={(e) => setItem({ ...item, name: e.target.value })} required minLength={2} /></label>
              <label>Description<textarea rows={2} value={item.description} onChange={(e) => setItem({ ...item, description: e.target.value })} /></label>
              <label>Price (INR)<input type="number" min="0" step="0.01" value={item.price} onChange={(e) => setItem({ ...item, price: e.target.value })} required /></label>
              <label>Image URL (optional)<input value={item.image_url || ""} onChange={(e) => setItem({ ...item, image_url: e.target.value })} /></label>
              <label>Category
                <select value={item.category_id} onChange={(e) => setItem({ ...item, category_id: e.target.value })}>
                  {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </label>
              <label>Type
                <select value={item.food_type} onChange={(e) => setItem({ ...item, food_type: e.target.value })}>
                  <option value="veg">Vegetarian</option><option value="non_veg">Non-vegetarian</option>
                </select>
              </label>
              <label className="inline"><input type="checkbox" checked={item.is_available} onChange={(e) => setItem({ ...item, is_available: e.target.checked })} /> Available</label>
              <div className="actions"><button className="btn">Save</button><button type="button" className="btn btn-ghost" onClick={() => setItem(null)}>Cancel</button></div>
            </form>
          )}
          {items.map((m) => (
            <div key={m.id} className="panel row wrap">
              <div><strong>{m.name}</strong><div className="muted small">{categories.find((c) => c.id === m.category_id)?.name} · {inr(m.price)}</div></div>
              <div className="actions">
                <label className="inline small"><input type="checkbox" checked={m.is_available} onChange={(e) => run(() => api.adminSetAvailability(m.id, e.target.checked), "Availability updated")} /> Available</label>
                <button className="btn btn-outline btn-sm" onClick={() => setItem({ ...m, image_url: m.image_url || "" })}>Edit</button>
                <button className="btn btn-danger btn-sm" onClick={() => window.confirm(`Delete ${m.name}?`) && run(() => api.adminDeleteItem(m.id), "Item deleted")}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "categories" && (
        <div className="stack">
          <div><button className="btn" onClick={() => setCat({ name: "", description: "" })}>Add category</button></div>
          {cat && (
            <form className="panel stack" onSubmit={async (e) => { e.preventDefault(); if (await run(() => api.adminSaveCategory(cat), "Saved")) setCat(null); }}>
              <label>Name<input value={cat.name} onChange={(e) => setCat({ ...cat, name: e.target.value })} required minLength={2} /></label>
              <label>Description<input value={cat.description || ""} onChange={(e) => setCat({ ...cat, description: e.target.value })} /></label>
              <div className="actions"><button className="btn">Save</button><button type="button" className="btn btn-ghost" onClick={() => setCat(null)}>Cancel</button></div>
            </form>
          )}
          {categories.map((c) => (
            <div key={c.id} className="panel row wrap">
              <strong>{c.name}</strong>
              <div className="actions">
                <button className="btn btn-outline btn-sm" onClick={() => setCat(c)}>Edit</button>
                <button className="btn btn-danger btn-sm" onClick={() => window.confirm(`Delete ${c.name}?`) && run(() => api.adminDeleteCategory(c.id), "Category deleted")}>Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
