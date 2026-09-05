import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Bot, 
  FileText, 
  FileCheck, 
  Building2, 
  CheckCircle, 
  ClipboardList,
  ChevronLeft,
  ChevronRight,
  ShoppingBag,
  Users,
  LogOut
} from 'lucide-react';
import './Sidebar.css';

function Sidebar({ user, collapsed, setCollapsed, isVendor = false }) {
  const hasPermission = (permissionCode) => {
    if (!user) return false;
    if (user.permissions) {
      return user.permissions.includes(permissionCode);
    }
    return false;
  };

  // Role-based permission mapping
  const getPermissionsByRole = (role) => {
    const rolePermissions = {
      'EMPLOYEE': ['procurement:create', 'procurement:read', 'procurement:update', 'procurement:submit', 'procurement:cancel'],
      'PROCUREMENT_ANALYST': ['procurement:create', 'procurement:read', 'procurement:update', 'procurement:submit', 'procurement:review', 'vendor:read', 'contract:read', 'approval:read', 'policy:read', 'workflow:read'],
      'PROCUREMENT_MANAGER': ['procurement:create', 'procurement:read', 'procurement:update', 'procurement:submit', 'procurement:review', 'vendor:read', 'vendor:approve', 'contract:read', 'contract:approve', 'approval:read', 'approval:approve', 'approval:reject', 'approval:delegate', 'approval:escalate', 'policy:read', 'workflow:read', 'workflow:execute'],
      'PROCUREMENT_HEAD': ['procurement:read', 'procurement:update', 'procurement:submit', 'procurement:review', 'vendor:read', 'vendor:approve', 'contract:read', 'contract:create', 'contract:update', 'contract:approve', 'approval:read', 'approval:approve', 'approval:reject', 'approval:delegate', 'approval:escalate', 'policy:read', 'workflow:read', 'workflow:execute', 'workflow:resume'],
      'FINANCE_OFFICER': ['procurement:read', 'vendor:read', 'contract:read', 'contract:approve', 'approval:read', 'approval:approve', 'approval:reject', 'policy:read', 'workflow:read'],
      'LEGAL_OFFICER': ['procurement:read', 'vendor:read', 'contract:read', 'contract:create', 'contract:update', 'contract:approve', 'approval:read', 'approval:approve', 'approval:reject', 'workflow:read'],
      'SECURITY_OFFICER': ['procurement:read', 'vendor:read', 'contract:read', 'contract:approve', 'approval:read', 'approval:approve', 'approval:reject', 'workflow:read'],
      'COMPLIANCE_OFFICER': ['procurement:read', 'vendor:read', 'contract:read', 'contract:approve', 'approval:read', 'approval:approve', 'approval:reject', 'approval:escalate', 'workflow:read'],
      'CFO': ['procurement:read', 'vendor:read', 'vendor:approve', 'contract:read', 'contract:approve', 'approval:read', 'approval:approve', 'approval:reject', 'approval:escalate', 'policy:read', 'workflow:read', 'workflow:resume'],
      'AUDITOR': ['procurement:read', 'audit:read', 'vendor:read', 'contract:read', 'approval:read', 'workflow:read'],
      'ADMIN': ['admin:users', 'admin:roles', 'admin:permissions', 'procurement:read', 'vendor:read', 'contract:read', 'approval:read', 'policy:read', 'workflow:read', 'audit:read'],
      'VENDOR': ['rfq:read', 'quotation:read', 'quotation:submit', 'vendor:portal_access', 'vendor:view_rfqs', 'vendor:submit_quotation'],
    };

    const roleUpper = role?.toUpperCase() || '';
    return rolePermissions[roleUpper] || [];
  };

  const userRole = user?.role?.toUpperCase() || user?.role_name?.toUpperCase() || '';
  const userPermissions = user?.permissions || getPermissionsByRole(userRole);

  const canAccess = (requiredPermission) => {
    if (!user) return false;
    if (userRole === 'ADMIN') return true;
    return userPermissions.includes(requiredPermission);
  };

  // Get nav items based on role
  const getNavItems = () => {
    // Vendor nav items
    if (isVendor || userRole === 'VENDOR') {
      return [
        { path: '/vendor/dashboard', icon: LayoutDashboard, label: 'Dashboard', permission: null },
        { path: '/vendor/rfqs', icon: FileText, label: 'My RFQs', permission: 'rfq:read' },
        { path: '/vendor/quotations', icon: FileCheck, label: 'My Quotations', permission: 'quotation:read' },
      ];
    }

    // Internal user nav items
    const baseItems = [
      { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', permission: null },
      { path: '/assistant', icon: Bot, label: 'AI Assistant', permission: null },
    ];

    const internalItems = [
      { path: '/procurement', icon: ShoppingBag, label: 'Procurement', permission: 'procurement:read' },
      { path: '/rfqs', icon: FileText, label: 'RFQs', permission: 'contract:read' },
      { path: '/quotations', icon: FileCheck, label: 'Quotations', permission: 'contract:read' },
      { path: '/vendors', icon: Building2, label: 'Vendors', permission: 'vendor:read' },
      { path: '/approvals', icon: CheckCircle, label: 'Approvals', permission: 'approval:read' },
      { path: '/audit', icon: ClipboardList, label: 'Audit', permission: 'audit:read' },
    ];

    const adminItems = [
      { path: '/admin/users', icon: Users, label: 'User Management', permission: 'admin:users' },
    ];

    let items = [...baseItems];

    for (const item of internalItems) {
      if (!item.permission || canAccess(item.permission)) {
        items.push(item);
      }
    }

    if (userRole === 'ADMIN' || canAccess('admin:users')) {
      items.push(...adminItems);
    }

    return items;
  };

  const navItems = getNavItems();

  if (!user) {
    return (
      <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">P</div>
          {!collapsed && <span className="sidebar-brand-text">ProcureOps</span>}
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/dashboard" className="sidebar-link">
            <LayoutDashboard className="sidebar-icon" size={20} />
            {!collapsed && <span className="sidebar-label">Dashboard</span>}
          </NavLink>
        </nav>
        <button 
          className="sidebar-toggle"
          onClick={() => setCollapsed(!collapsed)}
          aria-label="Toggle sidebar"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>
    );
  }

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">P</div>
        {!collapsed && (
          <>
            <span className="sidebar-brand-text">ProcureOps</span>
            {isVendor && <span className="sidebar-role-badge">Vendor</span>}
          </>
        )}
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `sidebar-link ${isActive ? 'active' : ''}`
            }
          >
            <item.icon className="sidebar-icon" size={20} />
            {!collapsed && <span className="sidebar-label">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <button 
        className="sidebar-toggle"
        onClick={() => setCollapsed(!collapsed)}
        aria-label="Toggle sidebar"
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>
    </div>
  );
}

export default Sidebar;