import React from "react";
import { Route, Routes } from "react-router-dom";
import Footer from "./components/Footer.jsx";
import Navbar from "./components/Navbar.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import About from "./pages/About.jsx";
import Admin from "./pages/Admin.jsx";
import Cart from "./pages/Cart.jsx";
import Checkout from "./pages/Checkout.jsx";
import Contact from "./pages/Contact.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Menu from "./pages/Menu.jsx";
import MyOrders from "./pages/MyOrders.jsx";
import OrderConfirmation from "./pages/OrderConfirmation.jsx";
import Register from "./pages/Register.jsx";

export default function App() {
  return (
    <div className="shell">
      <Navbar />
      <main className="main">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/menu" element={<Menu />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
          <Route path="/order-confirmation/:id" element={<ProtectedRoute><OrderConfirmation /></ProtectedRoute>} />
          <Route path="/orders" element={<ProtectedRoute><MyOrders /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedRoute admin><Admin /></ProtectedRoute>} />
          <Route path="*" element={<div className="container page"><h1 className="h1">Page not found</h1></div>} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
