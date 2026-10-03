import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import OrderSummary from "../components/OrderSummary.jsx";
import { api, inr } from "../services/api.js";

export default function OrderConfirmation() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { api.order(id).then(setOrder).catch((e) => setError(e.message)); }, [id]);

  if (error) return <div className="container page"><p className="error">{error}</p></div>;
  if (!order) return <div className="container page"><p>Loading...</p></div>;
  return (
    <div className="container page narrow center-text">
      <div className="tick">✔</div>
      <h1 className="h1">Thank you, {order.customer_name}!</h1>
      <p>Your order <strong>{order.order_number}</strong> is placed. Pay with cash when it arrives.</p>
      <ul className="plain stack left">
        {order.items.map((i) => <li key={i.id} className="row"><span>{i.quantity} × {i.item_name}</span><span>{inr(i.subtotal)}</span></li>)}
      </ul>
      <OrderSummary subtotal={order.subtotal} deliveryFee={order.delivery_fee} tax={order.tax_amount} total={order.total_amount} />
      <p className="muted small">Delivering to: {order.delivery_address}</p>
      <div className="actions center">
        <Link to="/orders" className="btn">View My Orders</Link>
        <Link to="/menu" className="btn btn-outline">Order More</Link>
      </div>
    </div>
  );
}
