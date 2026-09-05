import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, User, Building2 } from 'lucide-react';
import './Header.css';

function Header({ user, setAuth, setUser, isVendor = false }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (isVendor) {
      localStorage.removeItem('vendor_access_token');
      localStorage.removeItem('vendor_data');
      setAuth(false);
      setUser(null);
      navigate('/vendor/login');
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
      setAuth(false);
      setUser(null);
      navigate('/login');
    }
  };

  const getUserName = () => {
    if (isVendor) {
      return user?.vendor_name || user?.name || 'Vendor';
    }
    return user?.full_name || user?.name || user?.email?.split('@')[0] || 'User';
  };

  const getUserRole = () => {
    if (isVendor) {
      return 'VENDOR';
    }
    return user?.role || user?.role_name || '';
  };

  const getTitle = () => {
    if (isVendor) {
      return 'Vendor Portal';
    }
    return 'ProcureOps';
  };

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">{getTitle()}</h1>
        {isVendor && <span className="header-badge">Vendor</span>}
      </div>
      
      <div className="header-right">
        <div className="header-user">
          {isVendor ? (
            <Building2 className="header-user-icon" size={16} />
          ) : (
            <User className="header-user-icon" size={16} />
          )}
          <span className="header-user-name">{getUserName()}</span>
          <span className="header-user-role">{getUserRole()}</span>
        </div>
        <button className="header-logout" onClick={handleLogout}>
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
}

export default Header;