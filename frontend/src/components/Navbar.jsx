import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { useCart } from "../context/CartContext.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { count } = useCart();
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);
  return (
    <header className="nav">
      <div className="nav-bar container">
        <Link to="/" className="brand" onClick={close}><span className="seal">龍</span> Dragon Wok</Link>
        <button className="burger" onClick={() => setOpen(!open)} aria-label="Menu">{open ? "✕" : "☰"}</button>
        <nav className={`nav-links ${open ? "open" : ""}`}>
          <NavLink to="/" end onClick={close}>Home</NavLink>
          <NavLink to="/menu" onClick={close}>Menu</NavLink>
          <NavLink to="/about" onClick={close}>About Us</NavLink>
          <NavLink to="/contact" onClick={close}>Contact</NavLink>
          <NavLink to="/cart" onClick={close}>Cart{count > 0 && <span className="badge">{count}</span>}</NavLink>
          {user ? (
            <>
              <NavLink to="/orders" onClick={close}>My Orders</NavLink>
              {user.role === "admin" && <NavLink to="/admin" onClick={close}>Admin</NavLink>}
              <button className="btn btn-outline btn-sm" onClick={() => { close(); logout(); }}>Logout</button>
            </>
          ) : (
            <>
              <NavLink to="/login" onClick={close}>Login</NavLink>
              <Link to="/register" className="btn btn-sm" onClick={close}>Register</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
