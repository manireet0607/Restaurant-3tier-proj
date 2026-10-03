import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import OrderSummary from "../components/OrderSummary.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useCart } from "../context/CartContext.jsx";
import { api } from "../services/api.js";
import { useFees } from "./Cart.jsx";

export default function Checkout() {
  const { user } = useAuth();
  const { lines, subtotal, clear } = useCart();
  const fees = useFees(subtotal, lines.length > 0);
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: user?.name || "", phone: user?.phone || "", address: "", notes: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  if (!lines.length) {
    return <div className="container page"><p>Your cart is empty. <Link to="/menu">Go to the menu</Link></p></div>;
  }

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      // Only item ids and quantities are sent. Prices and totals are decided by the server.
      const order = await api.createOrder({
        customer_name: form.name, customer_phone: form.phone, delivery_address: form.address,
        special_instructions: form.notes || null, payment_method: "cod",
        items: lines.map((l) => ({ menu_item_id: l.id, quantity: l.quantity })),
      });
      clear();
      navigate(`/order-confirmation/${order.id}`, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container page">
      <h1 className="h1">Checkout</h1>
      <div className="two-col">
        <form className="stack" onSubmit={submit}>
          <label>Full name<input value={form.name} onChange={set("name")} required minLength={2} /></label>
          <label>Phone number<input type="tel" value={form.phone} onChange={set("phone")} required placeholder="98765 43210" /></label>
          <label>Delivery address<textarea rows={3} value={form.address} onChange={set("address")} required minLength={10} /></label>
          <label>Special instructions (optional)<textarea rows={2} value={form.notes} onChange={set("notes")} maxLength={300} /></label>
          <div className="pay"><strong>Payment:</strong> Cash on Delivery</div>
          {error && <p className="error">{error}</p>}
          <button className="btn btn-lg" disabled={busy}>{busy ? "Placing order..." : "Place Order"}</button>
        </form>
        <aside>
          <OrderSummary subtotal={subtotal} deliveryFee={fees.deliveryFee} tax={fees.tax} total={fees.total} note="Final amount is confirmed by our server." />
        </aside>
      </div>
    </div>
  );
}
