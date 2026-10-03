import React from "react";
import { inr } from "../services/api.js";

export default function OrderSummary({ subtotal, deliveryFee, tax, total, note }) {
  return (
    <div className="summary">
      <div className="row"><span>Subtotal</span><span>{inr(subtotal)}</span></div>
      <div className="row"><span>Delivery fee</span><span>{inr(deliveryFee)}</span></div>
      <div className="row"><span>Tax</span><span>{inr(tax)}</span></div>
      <div className="row total"><span>Total</span><span>{inr(total)}</span></div>
      {note && <p className="muted small">{note}</p>}
    </div>
  );
}
