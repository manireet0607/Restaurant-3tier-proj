import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import OrderSummary from "../components/OrderSummary.jsx";
import { useCart } from "../context/CartContext.jsx";
import { api, inr } from "../services/api.js";

export function useFees(subtotal, hasItems) {
  const [cfg, setCfg] = useState({ delivery_fee: "0", tax_percent: "0" });
  useEffect(() => { api.config().then(setCfg).catch(() => {}); }, []);
  const deliveryFee = hasItems ? Number(cfg.delivery_fee) : 0;
  const tax = Math.round(subtotal * Number(cfg.tax_percent)) / 100;
  return { deliveryFee, tax, total: subtotal + deliveryFee + tax };
}

export default function Cart() {
  const { lines, subtotal, setQuantity, remove } = useCart();
  const fees = useFees(subtotal, lines.length > 0);
  if (!lines.length) {
    return (
      <div className="container page center-col">
        <h1 className="h1">Your Cart</h1>
        <p className="muted">Your cart is empty.</p>
        <Link to="/menu" className="btn">Browse the Menu</Link>
      </div>
    );
  }
  return (
    <div className="container page">
      <h1 className="h1">Your Cart</h1>
      <div className="two-col">
        <ul className="plain stack">
          {lines.map((l) => (
            <li key={l.id} className="line">
              <div><strong>{l.name}</strong><div className="muted small">{inr(l.price)} each</div></div>
              <div className="qty">
                <button className="btn btn-outline btn-icon" aria-label="Decrease" onClick={() => setQuantity(l.id, l.quantity - 1)}>−</button>
                <span>{l.quantity}</span>
                <button className="btn btn-outline btn-icon" aria-label="Increase" onClick={() => setQuantity(l.id, l.quantity + 1)}>+</button>
              </div>
              <strong>{inr(Number(l.price) * l.quantity)}</strong>
              <button className="btn btn-ghost btn-icon" aria-label="Remove" onClick={() => remove(l.id)}>🗑</button>
            </li>
          ))}
        </ul>
        <aside className="stack">
          <OrderSummary subtotal={subtotal} deliveryFee={fees.deliveryFee} tax={fees.tax} total={fees.total} note="Final amount is confirmed by our server at checkout." />
          <Link to="/checkout" className="btn btn-lg">Proceed to Checkout</Link>
        </aside>
      </div>
    </div>
  );
}
