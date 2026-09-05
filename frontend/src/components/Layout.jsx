import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import './Layout.css';

function Layout({ user, setAuth, setUser, isVendor = false }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="layout">
      <Sidebar 
        user={user} 
        collapsed={sidebarCollapsed} 
        setCollapsed={setSidebarCollapsed}
        isVendor={isVendor}
      />
      <div className={`layout-main ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <Header 
          user={user} 
          setAuth={setAuth} 
          setUser={setUser}
          isVendor={isVendor}
        />
        <div className="layout-content">
          <Outlet context={{ user, isVendor }} />
        </div>
      </div>
    </div>
  );
}

export default Layout;