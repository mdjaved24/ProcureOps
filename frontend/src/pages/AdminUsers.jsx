import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Edit2, 
  Trash2, 
  RefreshCw,
  Loader2,
  User,
  Building2,
  Mail,
  Phone,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye,
  EyeOff
} from 'lucide-react';
import './AdminUsers.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function AdminUsers({ user }) {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  // Create form state
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: '',
    role_id: '',
    department_id: '',
    vendor_id: '',
  });

  const [editFormData, setEditFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    role_id: '',
    department_id: '',
    is_active: true,
    vendor_id: '',
  });

  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    fetchUsers();
    fetchRoles();
    fetchVendors();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      let url = `${API_BASE_URL}/admin/users?limit=100`;
      if (search) {
        url += `&search=${encodeURIComponent(search)}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          setError('You don\'t have permission to manage users.');
          setUsers([]);
          setLoading(false);
          return;
        }
        throw new Error('Failed to load users');
      }

      const data = await response.json();
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      setError('Unable to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/users/roles/dropdown`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setRoles(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch roles:', err);
    }
  };

  const fetchVendors = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/users/vendors/dropdown`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setVendors(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch vendors:', err);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      setProcessing(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      setProcessing(false);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      
      // Check if selected role is VENDOR
      const selectedRole = roles.find(r => r.id === parseInt(formData.role_id));
      const isVendor = selectedRole?.name?.toUpperCase() === 'VENDOR';

      const payload = {
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        phone: formData.phone || null,
        password: formData.password,
        role_id: parseInt(formData.role_id),
        department_id: formData.department_id ? parseInt(formData.department_id) : null,
        vendor_id: isVendor && formData.vendor_id ? parseInt(formData.vendor_id) : null,
      };

      const response = await fetch(`${API_BASE_URL}/admin/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error('Email already registered');
        }
        throw new Error(data.detail || 'Failed to create user');
      }

      setShowCreateModal(false);
      resetForm();
      await fetchUsers();
    } catch (err) {
      setError(err.message || 'Unable to create user. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleEditUser = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      
      const payload = {
        full_name: editFormData.full_name || null,
        email: editFormData.email || null,
        phone: editFormData.phone || null,
        role_id: editFormData.role_id ? parseInt(editFormData.role_id) : null,
        department_id: editFormData.department_id ? parseInt(editFormData.department_id) : null,
        is_active: editFormData.is_active,
      };

      // If role is VENDOR, include vendor_id
      const selectedRole = roles.find(r => r.id === parseInt(editFormData.role_id));
      if (selectedRole?.name?.toUpperCase() === 'VENDOR' && editFormData.vendor_id) {
        payload.vendor_id = parseInt(editFormData.vendor_id);
      }

      const response = await fetch(`${API_BASE_URL}/admin/users/${selectedUser.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update user');
      }

      setShowEditModal(false);
      await fetchUsers();
    } catch (err) {
      setError(err.message || 'Unable to update user. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete user');
      }

      await fetchUsers();
    } catch (err) {
      setError(err.message || 'Unable to delete user. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const resetForm = () => {
    setFormData({
      full_name: '',
      email: '',
      phone: '',
      password: '',
      confirm_password: '',
      role_id: '',
      department_id: '',
      vendor_id: '',
    });
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setEditFormData({
      full_name: user.full_name || '',
      email: user.email || '',
      phone: user.phone || '',
      role_id: user.role_id || '',
      department_id: user.department_id || '',
      is_active: user.is_active !== undefined ? user.is_active : true,
      vendor_id: user.vendor_id || '',
    });
    setShowEditModal(true);
  };

  const isVendorRole = (roleId) => {
    const role = roles.find(r => r.id === parseInt(roleId));
    return role?.name?.toUpperCase() === 'VENDOR';
  };

  const getRoleName = (roleId) => {
    const role = roles.find(r => r.id === roleId);
    return role?.name || '—';
  };

  const getStatusBadge = (isActive) => {
    return isActive ? (
      <span className="status-badge active">Active</span>
    ) : (
      <span className="status-badge inactive">Inactive</span>
    );
  };

  if (loading) {
    return <div className="admin-users-loading">Loading users...</div>;
  }

  return (
    <div className="admin-users-page">
      <div className="admin-users-header">
        <div>
          <h1 className="admin-users-title">User Management</h1>
          <p className="admin-users-subtitle">Manage system users and their roles</p>
        </div>
        <button 
          className="create-btn"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus size={18} />
          Add User
        </button>
      </div>

      {error && <div className="admin-users-error">{error}</div>}

      <div className="admin-users-toolbar">
        <div className="search-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search users by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && fetchUsers()}
            className="search-input"
          />
        </div>
        <button className="refresh-btn" onClick={fetchUsers}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {users.length === 0 ? (
        <div className="admin-users-empty">
          <User size={48} className="empty-icon" />
          <p>No users found</p>
          <p className="empty-hint">Create your first user by clicking "Add User"</p>
        </div>
      ) : (
        <div className="admin-users-table-wrapper">
          <table className="admin-users-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role</th>
                <th>Vendor</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="user-name">
                    <div className="user-avatar">
                      {u.full_name?.charAt(0) || 'U'}
                    </div>
                    {u.full_name}
                  </td>
                  <td className="user-email">{u.email}</td>
                  <td>{u.phone || '—'}</td>
                  <td>
                    <span className="role-badge">{getRoleName(u.role_id)}</span>
                  </td>
                  <td>{u.vendor_name || '—'}</td>
                  <td>{getStatusBadge(u.is_active)}</td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn edit"
                        onClick={() => openEditModal(u)}
                        title="Edit User"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button 
                        className="action-btn delete"
                        onClick={() => handleDeleteUser(u.id)}
                        disabled={processing}
                        title="Delete User"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content create-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add New User</h3>
              <button className="modal-close" onClick={() => {
                setShowCreateModal(false);
                resetForm();
                setError('');
              }}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleCreateUser}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="form-group">
                <label htmlFor="full_name">Full Name *</label>
                <input
                  id="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  required
                  placeholder="John Doe"
                  disabled={processing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  placeholder="user@company.com"
                  disabled={processing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">Phone</label>
                <input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="+1 234 567 8900"
                  disabled={processing}
                />
              </div>

              <div className="form-group password-group">
                <label htmlFor="password">Password *</label>
                <div className="password-input-wrapper">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    minLength={8}
                    placeholder="Min 8 characters"
                    disabled={processing}
                  />
                  <button
                    type="button"
                    className="password-toggle-btn"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <div className="form-group password-group">
                <label htmlFor="confirm_password">Confirm Password *</label>
                <div className="password-input-wrapper">
                  <input
                    id="confirm_password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.confirm_password}
                    onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                    required
                    minLength={8}
                    placeholder="Confirm password"
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="role_id">Role *</label>
                  <select
                    id="role_id"
                    value={formData.role_id}
                    onChange={(e) => {
                      setFormData({ 
                        ...formData, 
                        role_id: e.target.value,
                        vendor_id: '' // Reset vendor when role changes
                      });
                    }}
                    required
                    disabled={processing}
                  >
                    <option value="">Select Role</option>
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="department_id">Department</label>
                  <select
                    id="department_id"
                    value={formData.department_id}
                    onChange={(e) => setFormData({ ...formData, department_id: e.target.value })}
                    disabled={processing}
                  >
                    <option value="">Select Department</option>
                    {/* Departments will be fetched separately */}
                  </select>
                </div>
              </div>

              {/* Vendor dropdown - only shown when VENDOR role is selected */}
              {formData.role_id && isVendorRole(formData.role_id) && (
                <div className="form-group">
                  <label htmlFor="vendor_id">Vendor *</label>
                  <select
                    id="vendor_id"
                    value={formData.vendor_id}
                    onChange={(e) => setFormData({ ...formData, vendor_id: e.target.value })}
                    required
                    disabled={processing}
                  >
                    <option value="">Select Vendor</option>
                    {vendors.map((vendor) => (
                      <option key={vendor.id} value={vendor.id}>
                        {vendor.vendor_code} - {vendor.name}
                      </option>
                    ))}
                  </select>
                  {vendors.length === 0 && (
                    <p className="form-hint">No active vendors available. Please create a vendor first.</p>
                  )}
                </div>
              )}

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="modal-btn cancel"
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                    setError('');
                  }}
                  disabled={processing}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="modal-btn create"
                  disabled={processing}
                >
                  {processing ? (
                    <>
                      <Loader2 size={16} className="spinner" />
                      Creating...
                    </>
                  ) : (
                    'Create User'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditModal && selectedUser && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content create-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit User</h3>
              <button className="modal-close" onClick={() => setShowEditModal(false)}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleEditUser}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="form-group">
                <label htmlFor="edit_full_name">Full Name</label>
                <input
                  id="edit_full_name"
                  type="text"
                  value={editFormData.full_name}
                  onChange={(e) => setEditFormData({ ...editFormData, full_name: e.target.value })}
                  placeholder="John Doe"
                  disabled={processing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit_email">Email</label>
                <input
                  id="edit_email"
                  type="email"
                  value={editFormData.email}
                  onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                  placeholder="user@company.com"
                  disabled={processing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit_phone">Phone</label>
                <input
                  id="edit_phone"
                  type="tel"
                  value={editFormData.phone}
                  onChange={(e) => setEditFormData({ ...editFormData, phone: e.target.value })}
                  placeholder="+1 234 567 8900"
                  disabled={processing}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit_role_id">Role</label>
                  <select
                    id="edit_role_id"
                    value={editFormData.role_id}
                    onChange={(e) => {
                      setEditFormData({ 
                        ...editFormData, 
                        role_id: e.target.value,
                        vendor_id: '' // Reset vendor when role changes
                      });
                    }}
                    disabled={processing}
                  >
                    <option value="">Select Role</option>
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="edit_department_id">Department</label>
                  <select
                    id="edit_department_id"
                    value={editFormData.department_id}
                    onChange={(e) => setEditFormData({ ...editFormData, department_id: e.target.value })}
                    disabled={processing}
                  >
                    <option value="">Select Department</option>
                  </select>
                </div>
              </div>

              {/* Vendor dropdown - only shown when VENDOR role is selected */}
              {editFormData.role_id && isVendorRole(editFormData.role_id) && (
                <div className="form-group">
                  <label htmlFor="edit_vendor_id">Vendor</label>
                  <select
                    id="edit_vendor_id"
                    value={editFormData.vendor_id}
                    onChange={(e) => setEditFormData({ ...editFormData, vendor_id: e.target.value })}
                    disabled={processing}
                  >
                    <option value="">Select Vendor</option>
                    {vendors.map((vendor) => (
                      <option key={vendor.id} value={vendor.id}>
                        {vendor.vendor_code} - {vendor.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="form-group">
                <label htmlFor="edit_is_active">Status</label>
                <select
                  id="edit_is_active"
                  value={editFormData.is_active ? 'true' : 'false'}
                  onChange={(e) => setEditFormData({ ...editFormData, is_active: e.target.value === 'true' })}
                  disabled={processing}
                >
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="modal-btn cancel"
                  onClick={() => setShowEditModal(false)}
                  disabled={processing}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="modal-btn create"
                  disabled={processing}
                >
                  {processing ? (
                    <>
                      <Loader2 size={16} className="spinner" />
                      Updating...
                    </>
                  ) : (
                    'Update User'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminUsers