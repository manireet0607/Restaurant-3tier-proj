import React from "react";
import { inr } from "../services/api.js";
import { useCart } from "../context/CartContext.jsx";

export default function MenuCard({ item }) {
  const { add } = useCart();
  const veg = item.food_type === "veg";
  return (
    <article className={`card ${item.is_available ? "" : "off"}`}>
      <div className="card-img">
        {item.image_url ? <img src={item.image_url} alt={item.name} loading="lazy" /> : <div className="fallback">龍</div>}
        {!item.is_available && <span className="tag">Not available</span>}
      </div>
      <div className="card-body">
        <div className="card-title">
          <span className={`dot ${veg ? "veg" : "nonveg"}`} title={veg ? "Vegetarian" : "Non-vegetarian"} />
          <h3>{item.name}</h3>
        </div>
        <p className="muted grow">{item.description}</p>
        <div className="card-foot">
          <span className="price">{inr(item.price)}</span>
          <button className="btn btn-sm" disabled={!item.is_available} onClick={() => add(item)}>+ Add to Cart</button>
        </div>
      </div>
    </article>
  );
}
