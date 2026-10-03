import React from "react";
import { Link } from "react-router-dom";
import MenuCard from "../components/MenuCard.jsx";
import { useMenu } from "../hooks/useMenu.js";

export default function Home() {
  const { items, loading, error } = useMenu();
  const featured = items.filter((i) => i.is_available).slice(0, 4);
  return (
    <>
      <section className="hero">
        <div className="container hero-in">
          <span className="kicker">Wok-fired · Fresh · Fast</span>
          <h1>Taste the fire of the <em>Dragon Wok</em></h1>
          <p>Hakka noodles, crispy starters and hand-folded momos, cooked on roaring heat and delivered to your door.</p>
          <div className="actions">
            <Link to="/menu" className="btn btn-lg">Order Now</Link>
            <Link to="/about" className="btn btn-lg btn-gold">Our Story</Link>
          </div>
        </div>
      </section>
      <section className="container page">
        <h2 className="h2">Chef's Favourites</h2>
        {loading && <p>Loading menu...</p>}
        {error && <p className="error">{error}</p>}
        <div className="grid">{featured.map((i) => <MenuCard key={i.id} item={i} />)}</div>
        <div className="center"><Link to="/menu" className="btn btn-outline">See Full Menu</Link></div>
      </section>
    </>
  );
}
