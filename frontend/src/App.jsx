import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Procurement from './pages/Procurement';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import RFQs from './pages/RFQs';
import Quotations from './pages/Quotations';
import Vendors from './pages/Vendors';
import Approvals from './pages/Approvals';
import Audit from './pages/Audit';
import AdminUsers from './pages/AdminUsers';
import VendorLogin from './pages/VendorLogin';
import VendorDashboard from './pages/VendorDashboard';
import VendorRFQs from './pages/VendorRFQs';
import VendorQuotations from './pages/VendorQuotations';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [isVendorAuthenticated, setIsVendorAuthenticated] = useState(false);
  const [vendorData, setVendorData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    const vendorToken = localStorage.getItem('vendor_access_token');
    const vendorDataStr = localStorage.getItem('vendor_data');

    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setIsAuthenticated(true);
        setUser(parsedUser);
      } catch (e) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
      }
    }

    if (vendorToken && vendorDataStr) {
      try {
        const parsedVendor = JSON.parse(vendorDataStr);
        setIsVendorAuthenticated(true);
        setVendorData(parsedVendor);
      } catch (e) {
        localStorage.removeItem('vendor_access_token');
        localStorage.removeItem('vendor_data');
      }
    }

    setLoading(false);
  }, []);

  if (loading) {
    return <div className="app-loading">Loading...</div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Main Routes */}
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login setAuth={setIsAuthenticated} setUser={setUser} />} />
        <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register setAuth={setIsAuthenticated} setUser={setUser} />} />
        
        {/* Vendor Login */}
        <Route path="/vendor/login" element={isVendorAuthenticated ? <Navigate to="/vendor/dashboard" /> : <VendorLogin setVendorAuth={setIsVendorAuthenticated} setVendorData={setVendorData} />} />
        
        {/* Vendor Routes - Using same Layout with vendor data */}
        <Route element={<ProtectedRoute isAuthenticated={isVendorAuthenticated} isVendor={true} />}>
          <Route element={<Layout user={vendorData} setAuth={setIsVendorAuthenticated} setUser={setVendorData} isVendor={true} />}>
            <Route path="/vendor/dashboard" element={<VendorDashboard vendorData={vendorData} />} />
            <Route path="/vendor/rfqs" element={<VendorRFQs vendorData={vendorData} />} />
            <Route path="/vendor/quotations" element={<VendorQuotations vendorData={vendorData} />} />
          </Route>
        </Route>
        
        {/* Internal Routes */}
        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} isVendor={false} />}>
          <Route element={<Layout user={user} setAuth={setIsAuthenticated} setUser={setUser} isVendor={false} />}>
            <Route path="/dashboard" element={<Dashboard user={user} />} />
            <Route path="/assistant" element={<AIAssistant user={user} />} />
            <Route path="/procurement" element={<Procurement user={user} />} />
            <Route path="/rfqs" element={<RFQs user={user} />} />
            <Route path="/quotations" element={<Quotations user={user} />} />
            <Route path="/vendors" element={<Vendors user={user} />} />
            <Route path="/approvals" element={<Approvals user={user} />} />
            <Route path="/audit" element={<Audit user={user} />} />
            <Route path="/admin/users" element={<AdminUsers user={user} />} />
          </Route>
        </Route>
        
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;