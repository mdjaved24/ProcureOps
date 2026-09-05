import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Building2 } from 'lucide-react';
import './VendorLogin.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function VendorLogin({ setVendorAuth, setVendorData }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/vendor/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim(),
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Invalid email or password');
        } else if (response.status === 403) {
          throw new Error('Vendor account is inactive');
        } else {
          throw new Error(data.detail || 'Login failed');
        }
      }

      // Store vendor data
      localStorage.setItem('vendor_access_token', data.access_token);
      localStorage.setItem('vendor_data', JSON.stringify({
        vendor_id: data.vendor_id,
        vendor_name: data.vendor_name,
        token_type: data.token_type,
      }));

      setVendorAuth(true);
      setVendorData({
        vendor_id: data.vendor_id,
        vendor_name: data.vendor_name,
      });

      navigate('/vendor/dashboard');
    } catch (err) {
      setError(err.message || 'Unable to login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="vendor-login-page">
      <div className="vendor-login-container">
        <div className="vendor-login-header">
          <div className="vendor-login-logo">
            <Building2 size={32} />
            <span>ProcureOps</span>
          </div>
          <p className="vendor-login-subtitle">Vendor Portal</p>
        </div>

        <form className="vendor-login-form" onSubmit={handleSubmit}>
          {error && <div className="vendor-login-error">{error}</div>}
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vendor@company.com"
              required
              disabled={loading}
              autoComplete="email"
            />
          </div>

          <div className="form-group password-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-wrapper">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                disabled={loading}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={togglePasswordVisibility}
                disabled={loading}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button type="submit" className="vendor-login-button" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

          <div className="vendor-login-footer">
            <p>Access your RFQs and submit quotations</p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default VendorLogin;