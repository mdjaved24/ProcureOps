import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

function ProtectedRoute({ isAuthenticated, isVendor = false }) {
  // If not authenticated, redirect to appropriate login
  if (!isAuthenticated) {
    return <Navigate to={isVendor ? "/vendor/login" : "/login"} replace />;
  }
  
  return <Outlet />;
}

export default ProtectedRoute;