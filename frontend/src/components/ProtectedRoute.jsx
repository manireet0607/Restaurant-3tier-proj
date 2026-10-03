import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

// <ProtectedRoute> needs a logged-in user. <ProtectedRoute admin> also needs the admin role.
// The backend checks the role again on every admin request.
export default function ProtectedRoute({ admin = false, children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <div className="container page"><p>Loading...</p></div>;
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  if (admin && user.role !== "admin") return <Navigate to="/" replace />;
  return children;
}
