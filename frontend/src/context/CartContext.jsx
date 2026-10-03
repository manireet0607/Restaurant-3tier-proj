import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

const CartContext = createContext(null);
const KEY = "dw_cart";

function load() {
  try { const v = JSON.parse(localStorage.getItem(KEY)); return Array.isArray(v) ? v : []; } catch { return []; }
}

// Prices in the cart are only for display. The server recalculates everything.
export function CartProvider({ children }) {
  const [lines, setLines] = useState(load);
  useEffect(() => { try { localStorage.setItem(KEY, JSON.stringify(lines)); } catch { /* ignore */ } }, [lines]);

  const value = useMemo(() => ({
    lines,
    count: lines.reduce((s, l) => s + l.quantity, 0),
    subtotal: lines.reduce((s, l) => s + Number(l.price) * l.quantity, 0),
    add: (item) => setLines((p) => {
      const f = p.find((l) => l.id === item.id);
      if (f) return p.map((l) => (l.id === item.id ? { ...l, quantity: Math.min(20, l.quantity + 1) } : l));
      return [...p, { id: item.id, name: item.name, price: item.price, food_type: item.food_type, quantity: 1 }];
    }),
    setQuantity: (id, q) => setLines((p) => (q <= 0 ? p.filter((l) => l.id !== id) : p.map((l) => (l.id === id ? { ...l, quantity: Math.min(20, q) } : l)))),
    remove: (id) => setLines((p) => p.filter((l) => l.id !== id)),
    clear: () => setLines([]),
  }), [lines]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);
