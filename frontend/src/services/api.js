// All calls to the FastAPI backend go through here.
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
const TOKEN_KEY = "dw_token";

export const tokenStore = {
  get: () => { try { return localStorage.getItem(TOKEN_KEY); } catch { return null; } },
  set: (t) => { try { localStorage.setItem(TOKEN_KEY, t); } catch { /* ignore */ } },
  clear: () => { try { localStorage.removeItem(TOKEN_KEY); } catch { /* ignore */ } },
};

let onUnauthorized = () => {};
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn; };

async function request(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = tokenStore.get();
  if (token) headers.Authorization = `Bearer ${token}`;
  let res;
  try {
    res = await fetch(`${BASE}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new Error("Cannot reach the server. Please try again.");
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && token) onUnauthorized();
    const msg = data.errors?.[0]?.message || (typeof data.detail === "string" ? data.detail : "Something went wrong");
    throw new Error(msg);
  }
  return data;
}

export const api = {
  register: (b) => request("/auth/register", { method: "POST", body: b }),
  login: (b) => request("/auth/login", { method: "POST", body: b }),
  me: () => request("/users/me"),
  config: () => request("/config"),
  categories: () => request("/categories"),
  menu: () => request("/menu"),
  createOrder: (b) => request("/orders", { method: "POST", body: b }),
  myOrders: () => request("/orders"),
  order: (id) => request(`/orders/${id}`),
  // admin
  adminStats: () => request("/admin/stats"),
  adminOrders: () => request("/admin/orders"),
  adminSetStatus: (id, status) => request(`/admin/orders/${id}/status`, { method: "PATCH", body: { status } }),
  adminSaveItem: (item) =>
    item.id ? request(`/admin/menu/${item.id}`, { method: "PUT", body: strip(item) }) : request("/admin/menu", { method: "POST", body: strip(item) }),
  adminSetAvailability: (id, is_available) => request(`/admin/menu/${id}/availability`, { method: "PATCH", body: { is_available } }),
  adminDeleteItem: (id) => request(`/admin/menu/${id}`, { method: "DELETE" }),
  adminSaveCategory: (c) =>
    c.id ? request(`/admin/categories/${c.id}`, { method: "PUT", body: { name: c.name, description: c.description || null } })
         : request("/admin/categories", { method: "POST", body: { name: c.name, description: c.description || null } }),
  adminDeleteCategory: (id) => request(`/admin/categories/${id}`, { method: "DELETE" }),
};

function strip({ category_id, name, description, price, image_url, food_type, is_available }) {
  return { category_id: Number(category_id), name, description: description || "", price: String(price), image_url: image_url || null, food_type, is_available };
}

export const inr = (n) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(Number(n));

export const STATUS_LABELS = {
  pending: "Pending", confirmed: "Confirmed", preparing: "Preparing",
  out_for_delivery: "Out for Delivery", delivered: "Delivered", cancelled: "Cancelled",
};
// Mirrors the backend rules. The backend is the one that enforces them.
export const NEXT_STATUSES = {
  pending: ["confirmed", "cancelled"], confirmed: ["preparing", "cancelled"],
  preparing: ["out_for_delivery", "cancelled"], out_for_delivery: ["delivered"], delivered: [], cancelled: [],
};
