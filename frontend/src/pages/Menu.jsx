import React, { useState } from "react";
import MenuCard from "../components/MenuCard.jsx";
import { useMenu } from "../hooks/useMenu.js";

export default function Menu() {
  const { categories, items, loading, error } = useMenu();
  const [active, setActive] = useState("all");
  const shown = categories.filter((c) => active === "all" || c.id === active);
  return (
    <div className="container page">
      <h1 className="h1">Our Menu</h1>
      <div className="tabs">
        <button className={`tab ${active === "all" ? "on" : ""}`} onClick={() => setActive("all")}>All</button>
        {categories.map((c) => (
          <button key={c.id} className={`tab ${active === c.id ? "on" : ""}`} onClick={() => setActive(c.id)}>{c.name}</button>
        ))}
      </div>
      {loading && <p>Loading menu...</p>}
      {error && <p className="error">{error}</p>}
      {shown.map((c) => {
        const list = items.filter((i) => i.category_id === c.id);
        if (!list.length) return null;
        return (
          <section key={c.id} className="group">
            <h2 className="h3">{c.name}</h2>
            <div className="grid">{list.map((i) => <MenuCard key={i.id} item={i} />)}</div>
          </section>
        );
      })}
    </div>
  );
}
