import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Eye, 
  Plus, 
  Edit2, 
  RefreshCw,
  Loader2,
  Building2,
  Mail,
  Phone,
  MapPin,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import './Vendors.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function Vendors({ user }) {
  const [vendors, setVendors] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [processing, setProcessing] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    vendor_code: '',
    name: '',
    description: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    tax_id: '',
  });

  const [editFormData, setEditFormData] = useState({
    vendor_code: '',
    name: '',
    description: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    tax_id: '',
  });

  const [statusFormData, setStatusFormData] = useState({
    vendor_id: null,
    status: '',
    current_status: '',
  });

  useEffect(() => {
    fetchVendors();
  }, [statusFilter]);

  const fetchVendors = async () => {
    setLoading(true);
    setError('');
    
    try {
        const token = localStorage.getItem('access_token');
        let url = `${API_BASE_URL}/vendors?limit=100`;
        if (statusFilter) {
            url += `&status=${statusFilter}`;
        }
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
                setError('You don\'t have permission to view vendors.');
                setVendors([]);
                setTotal(0);
                setLoading(false);
                return;
            }
            throw new Error('Failed to load vendors');
        }

        const data = await response.json();
        
        // Handle the response - API now returns array directly
        if (Array.isArray(data)) {
            setVendors(data);
            setTotal(data.length);
        } else if (data.vendors && Array.isArray(data.vendors)) {
            // Handle paginated response (if we switch to paginated)
            setVendors(data.vendors);
            setTotal(data.total || data.vendors.length);
        } else {
            setVendors([]);
            setTotal(0);
        }
    } catch (err) {
        setError('Unable to load vendors. Please try again.');
    } finally {
        setLoading(false);
    }
};

  const handleCreateVendor = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const payload = {
        vendor_code: formData.vendor_code.toUpperCase().trim(),
        name: formData.name.trim(),
        description: formData.description || null,
        email: formData.email.toLowerCase().trim(),
        phone: formData.phone.trim(),
        address: formData.address || null,
        city: formData.city || null,
        state: formData.state || null,
        country: formData.country || null,
        postal_code: formData.postal_code || null,
        tax_id: formData.tax_id.toUpperCase().trim(),
      };

      const response = await fetch(`${API_BASE_URL}/vendors`, {
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
          if (data.detail?.includes('vendor code')) {
            throw new Error('Vendor code already exists.');
          } else if (data.detail?.includes('Tax id')) {
            throw new Error('Tax ID is already taken.');
          }
          throw new Error(data.detail || 'Vendor already exists.');
        } else if (response.status === 400) {
          throw new Error(data.detail || 'Please provide valid information (phone number must contain only digits).');
        } else if (response.status === 403) {
          throw new Error('You don\'t have permission to create vendors.');
        }
        throw new Error(data.detail || 'Failed to create vendor');
      }

      setShowCreateModal(false);
      resetForm();
      await fetchVendors();
    } catch (err) {
      setError(err.message || 'Unable to create vendor. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleUpdateVendor = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const payload = {};
      
      // Only include fields that have changed
      if (editFormData.vendor_code !== selectedVendor.vendor_code) {
        payload.vendor_code = editFormData.vendor_code.toUpperCase().trim();
      }
      if (editFormData.name !== selectedVendor.name) {
        payload.name = editFormData.name.trim();
      }
      if (editFormData.description !== selectedVendor.description) {
        payload.description = editFormData.description || null;
      }
      if (editFormData.email !== selectedVendor.email) {
        payload.email = editFormData.email.toLowerCase().trim();
      }
      if (editFormData.phone !== selectedVendor.phone) {
        payload.phone = editFormData.phone.trim();
      }
      if (editFormData.address !== selectedVendor.address) {
        payload.address = editFormData.address || null;
      }
      if (editFormData.city !== selectedVendor.city) {
        payload.city = editFormData.city || null;
      }
      if (editFormData.state !== selectedVendor.state) {
        payload.state = editFormData.state || null;
      }
      if (editFormData.country !== selectedVendor.country) {
        payload.country = editFormData.country || null;
      }
      if (editFormData.postal_code !== selectedVendor.postal_code) {
        payload.postal_code = editFormData.postal_code || null;
      }
      if (editFormData.tax_id !== selectedVendor.tax_id) {
        payload.tax_id = editFormData.tax_id.toUpperCase().trim();
      }

      if (Object.keys(payload).length === 0) {
        setShowEditModal(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/vendors/${selectedVendor.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          if (data.detail?.includes('vendor code')) {
            throw new Error('Vendor code already exists.');
          } else if (data.detail?.includes('Tax id')) {
            throw new Error('Tax ID is already taken.');
          } else if (data.detail?.includes('Email')) {
            throw new Error('Email is already taken.');
          }
          throw new Error(data.detail || 'Vendor already exists.');
        } else if (response.status === 400) {
          throw new Error(data.detail || 'Please provide valid information.');
        } else if (response.status === 403) {
          throw new Error('You don\'t have permission to update vendors.');
        }
        throw new Error(data.detail || 'Failed to update vendor');
      }

      setShowEditModal(false);
      await fetchVendors();
      // Refresh selected vendor if it was the one being edited
      if (selectedVendor && selectedVendor.id === data.id) {
        setSelectedVendor(data);
      }
    } catch (err) {
      setError(err.message || 'Unable to update vendor. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleUpdateStatus = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/vendors/${statusFormData.vendor_id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          status: statusFormData.status,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error(`Invalid status transition: ${statusFormData.current_status} → ${statusFormData.status}`);
        } else if (response.status === 403) {
          throw new Error('You don\'t have permission to update vendor status.');
        }
        throw new Error(data.detail || 'Failed to update vendor status');
      }

      setShowStatusModal(false);
      setStatusFormData({ vendor_id: null, status: '', current_status: '' });
      await fetchVendors();
      
      if (selectedVendor && selectedVendor.id === statusFormData.vendor_id) {
        const updated = vendors.find(v => v.id === statusFormData.vendor_id);
        if (updated) setSelectedVendor(updated);
      }
    } catch (err) {
      setError(err.message || 'Unable to update vendor status. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const resetForm = () => {
    setFormData({
      vendor_code: '',
      name: '',
      description: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      country: '',
      postal_code: '',
      tax_id: '',
    });
  };

  const openEditModal = (vendor) => {
    setSelectedVendor(vendor);
    setEditFormData({
      vendor_code: vendor.vendor_code || '',
      name: vendor.name || '',
      description: vendor.description || '',
      email: vendor.email || '',
      phone: vendor.phone || '',
      address: vendor.address || '',
      city: vendor.city || '',
      state: vendor.state || '',
      country: vendor.country || '',
      postal_code: vendor.postal_code || '',
      tax_id: vendor.tax_id || '',
    });
    setShowEditModal(true);
  };

  const openStatusModal = (vendor) => {
    setStatusFormData({
      vendor_id: vendor.id,
      status: '',
      current_status: vendor.status,
    });
    setShowStatusModal(true);
  };

  const getAvailableStatuses = (currentStatus) => {
    const transitions = {
      'ACTIVE': ['INACTIVE', 'BLOCKED'],
      'INACTIVE': ['ACTIVE'],
      'BLOCKED': ['ACTIVE', 'INACTIVE'],
    };
    return transitions[currentStatus] || [];
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchVendors();
  };

  const filteredVendors = vendors.filter(v => {
    const searchLower = search.toLowerCase();
    return (
      (v.vendor_code || '').toLowerCase().includes(searchLower) ||
      (v.name || '').toLowerCase().includes(searchLower) ||
      (v.email || '').toLowerCase().includes(searchLower) ||
      (v.tax_id || '').toLowerCase().includes(searchLower)
    );
  });

  if (loading) {
    return <div className="vendors-loading">Loading vendors...</div>;
  }

  return (
    <div className="vendors-page">
      <div className="vendors-header">
        <div>
          <h1 className="vendors-title">Vendors</h1>
          <p className="vendors-subtitle">Manage vendor relationships</p>
          {total > 0 && <span className="vendors-count">{total} vendors</span>}
        </div>
        <button 
          className="create-btn"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus size={18} />
          New Vendor
        </button>
      </div>

      {error && <div className="vendors-error">{error}</div>}

      <div className="vendors-toolbar">
        <form className="search-wrapper" onSubmit={handleSearch}>
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search by code, name, email, or tax ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </form>
        <div className="filter-wrapper">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="BLOCKED">Blocked</option>
          </select>
        </div>
        <button className="refresh-btn" onClick={fetchVendors}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {filteredVendors.length === 0 ? (
        <div className="vendors-empty">
          <Building2 size={48} className="empty-icon" />
          <p>No vendors found.</p>
          <p className="empty-hint">Create a new vendor to get started.</p>
        </div>
      ) : (
        <div className="vendors-table-wrapper">
          <table className="vendors-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Vendor Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredVendors.map((vendor) => (
                <tr key={vendor.id}>
                  <td className="vendor-code">{vendor.vendor_code}</td>
                  <td className="vendor-name">{vendor.name}</td>
                  <td className="vendor-email">{vendor.email}</td>
                  <td>{vendor.phone || '—'}</td>
                  <td>
                    <span className={`status-badge ${vendor.status?.toLowerCase()}`}>
                      {vendor.status || 'ACTIVE'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn view"
                        onClick={() => setSelectedVendor(vendor)}
                        title="View Details"
                      >
                        <Eye size={16} />
                      </button>
                      <button 
                        className="action-btn edit"
                        onClick={() => openEditModal(vendor)}
                        title="Edit Vendor"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button 
                        className="action-btn status"
                        onClick={() => openStatusModal(vendor)}
                        title="Change Status"
                      >
                        <CheckCircle size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* View Details Modal */}
      {selectedVendor && !showEditModal && !showStatusModal && (
        <div className="modal-overlay" onClick={() => setSelectedVendor(null)}>
          <div className="modal-content detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>{selectedVendor.vendor_code}</h3>
                <span className={`status-badge ${selectedVendor.status?.toLowerCase()}`}>
                  {selectedVendor.status || 'ACTIVE'}
                </span>
              </div>
              <button className="modal-close" onClick={() => setSelectedVendor(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-row">
                <span className="detail-label">Name</span>
                <span className="detail-value">{selectedVendor.name}</span>
              </div>
              {selectedVendor.description && (
                <div className="detail-row">
                  <span className="detail-label">Description</span>
                  <span className="detail-value">{selectedVendor.description}</span>
                </div>
              )}
              <div className="detail-row">
                <span className="detail-label">Email</span>
                <span className="detail-value"><Mail size={14} className="detail-icon" /> {selectedVendor.email}</span>
              </div>
              {selectedVendor.phone && (
                <div className="detail-row">
                  <span className="detail-label">Phone</span>
                  <span className="detail-value"><Phone size={14} className="detail-icon" /> {selectedVendor.phone}</span>
                </div>
              )}
              <div className="detail-row">
                <span className="detail-label">Tax ID</span>
                <span className="detail-value">{selectedVendor.tax_id}</span>
              </div>
              {selectedVendor.address && (
                <div className="detail-row">
                  <span className="detail-label">Address</span>
                  <span className="detail-value">
                    <MapPin size={14} className="detail-icon" />
                    {[selectedVendor.address, selectedVendor.city, selectedVendor.state, selectedVendor.country, selectedVendor.postal_code]
                      .filter(Boolean)
                      .join(', ')}
                  </span>
                </div>
              )}
              <div className="detail-row">
                <span className="detail-label">Created</span>
                <span>{selectedVendor.created_at ? new Date(selectedVendor.created_at).toLocaleString() : '—'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Updated</span>
                <span>{selectedVendor.updated_at ? new Date(selectedVendor.updated_at).toLocaleString() : '—'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Vendor Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content create-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Vendor</h3>
              <button className="modal-close" onClick={() => {
                setShowCreateModal(false);
                resetForm();
              }}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleCreateVendor}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="vendor_code">Vendor Code *</label>
                  <input
                    id="vendor_code"
                    type="text"
                    value={formData.vendor_code}
                    onChange={(e) => setFormData({ ...formData, vendor_code: e.target.value })}
                    required
                    minLength={2}
                    maxLength={50}
                    placeholder="VEN-001"
                    disabled={processing}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="name">Vendor Name *</label>
                  <input
                    id="name"
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    minLength={2}
                    maxLength={255}
                    placeholder="ABC Supplies Ltd"
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={2}
                  placeholder="Vendor description"
                  maxLength={5000}
                  disabled={processing}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="email">Email *</label>
                  <input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    placeholder="vendor@company.com"
                    disabled={processing}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="phone">Phone *</label>
                  <input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    required
                    placeholder="1234567890"
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="tax_id">Tax ID *</label>
                  <input
                    id="tax_id"
                    type="text"
                    value={formData.tax_id}
                    onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })}
                    required
                    maxLength={100}
                    placeholder="GSTIN-12345"
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="address">Address</label>
                <textarea
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  rows={2}
                  placeholder="Street address"
                  maxLength={2000}
                  disabled={processing}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="city">City</label>
                  <input
                    id="city"
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    maxLength={100}
                    placeholder="City"
                    disabled={processing}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="state">State</label>
                  <input
                    id="state"
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    maxLength={100}
                    placeholder="State"
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="country">Country</label>
                  <input
                    id="country"
                    type="text"
                    value={formData.country}
                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                    maxLength={100}
                    placeholder="Country"
                    disabled={processing}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="postal_code">Postal Code</label>
                  <input
                    id="postal_code"
                    type="text"
                    value={formData.postal_code}
                    onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                    maxLength={20}
                    placeholder="Postal code"
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="modal-btn cancel"
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
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
                    'Create Vendor'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Vendor Modal */}
      {showEditModal && selectedVendor && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content create-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Vendor</h3>
              <button className="modal-close" onClick={() => setShowEditModal(false)}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleUpdateVendor}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit_vendor_code">Vendor Code *</label>
                  <input
                    id="edit_vendor_code"
                    type="text"
                    value={editFormData.vendor_code}
                    onChange={(e) => setEditFormData({ ...editFormData, vendor_code: e.target.value })}
                    required
                    minLength={2}
                    maxLength={50}
                    disabled={processing}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="edit_name">Vendor Name *</label>
                  <input
                    id="edit_name"
                    type="text"
                    value={editFormData.name}
                    onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                    required
                    minLength={2}
                    maxLength={255}
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="edit_description">Description</label>
                <textarea
                  id="edit_description"
                  value={editFormData.description}
                  onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                  rows={2}
                  maxLength={5000}
                  disabled={processing}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit_email">Email *</label>
                  <input
                    id="edit_email"
                    type="email"
                    value={editFormData.email}
                    onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                    required
                    disabled={processing}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="edit_phone">Phone *</label>
                  <input
                    id="edit_phone"
                    type="tel"
                    value={editFormData.phone}
                    onChange={(e) => setEditFormData({ ...editFormData, phone: e.target.value })}
                    required
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit_tax_id">Tax ID *</label>
                  <input
                    id="edit_tax_id"
                    type="text"
                    value={editFormData.tax_id}
                    onChange={(e) => setEditFormData({ ...editFormData, tax_id: e.target.value })}
                    required
                    maxLength={100}
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="edit_address">Address</label>
                <textarea
                  id="edit_address"
                  value={editFormData.address}
                  onChange={(e) => setEditFormData({ ...editFormData, address: e.target.value })}
                  rows={2}
                  maxLength={2000}
                  disabled={processing}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit_city">City</label>
                  <input
                    id="edit_city"
                    type="text"
                    value={editFormData.city}
                    onChange={(e) => setEditFormData({ ...editFormData, city: e.target.value })}
                    maxLength={100}
                    disabled={processing}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="edit_state">State</label>
                  <input
                    id="edit_state"
                    type="text"
                    value={editFormData.state}
                    onChange={(e) => setEditFormData({ ...editFormData, state: e.target.value })}
                    maxLength={100}
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="edit_country">Country</label>
                  <input
                    id="edit_country"
                    type="text"
                    value={editFormData.country}
                    onChange={(e) => setEditFormData({ ...editFormData, country: e.target.value })}
                    maxLength={100}
                    disabled={processing}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="edit_postal_code">Postal Code</label>
                  <input
                    id="edit_postal_code"
                    type="text"
                    value={editFormData.postal_code}
                    onChange={(e) => setEditFormData({ ...editFormData, postal_code: e.target.value })}
                    maxLength={20}
                    disabled={processing}
                  />
                </div>
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
                    'Update Vendor'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Change Status Modal */}
      {showStatusModal && (
        <div className="modal-overlay" onClick={() => setShowStatusModal(false)}>
          <div className="modal-content status-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Change Vendor Status</h3>
              <button className="modal-close" onClick={() => setShowStatusModal(false)}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleUpdateStatus}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="status-info">
                <span className="status-label">Current Status:</span>
                <span className={`status-badge ${statusFormData.current_status?.toLowerCase()}`}>
                  {statusFormData.current_status || 'ACTIVE'}
                </span>
              </div>

              <div className="form-group">
                <label htmlFor="new_status">New Status *</label>
                <select
                  id="new_status"
                  value={statusFormData.status}
                  onChange={(e) => setStatusFormData({ ...statusFormData, status: e.target.value })}
                  required
                  disabled={processing}
                >
                  <option value="">Select new status</option>
                  {getAvailableStatuses(statusFormData.current_status).map((status) => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
                {getAvailableStatuses(statusFormData.current_status).length === 0 && (
                  <p className="form-hint">No valid status transitions available.</p>
                )}
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="modal-btn cancel"
                  onClick={() => setShowStatusModal(false)}
                  disabled={processing}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="modal-btn create"
                  disabled={processing || !statusFormData.status}
                >
                  {processing ? (
                    <>
                      <Loader2 size={16} className="spinner" />
                      Updating...
                    </>
                  ) : (
                    'Update Status'
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

export default Vendors;