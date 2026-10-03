import React from "react";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-in">
        <span className="brand-sm">龍 Dragon Wok</span>
        <span>Authentic Chinese, wok-fired fresh. Cash on Delivery.</span>
        <span>© {new Date().getFullYear()} Dragon Wok</span>
      </div>
    </footer>
  );
}
