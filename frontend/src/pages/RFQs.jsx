import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Eye, 
  Plus, 
  Send, 
  XCircle, 
  CheckCircle,
  RefreshCw,
  Loader2,
  Building2,
  Calendar,
  FileText,
  Clock
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import './RFQs.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function RFQs({ user }) {
  const [rfqs, setRfqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedRFQ, setSelectedRFQ] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showVendorModal, setShowVendorModal] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [purchaseRequests, setPurchaseRequests] = useState([]);
  const [vendors, setVendors] = useState([]);

  // Create form state
  const [formData, setFormData] = useState({
    purchase_request_id: '',
    title: '',
    description: '',
    submission_deadline: '',
  });

  // Vendor form state
  const [vendorForm, setVendorForm] = useState({
    rfq_id: null,
    vendor_id: '',
  });

  useEffect(() => {
    fetchRFQs();
    fetchPurchaseRequests();
    fetchVendors();
  }, []);

  // Check if user has RFQ permissions
  const userRole = user?.role?.toUpperCase() || user?.role_name?.toUpperCase() || '';
  const hasRFQPermission = ['ADMIN', 'PROCUREMENT_MANAGER', 'PROCUREMENT_HEAD', 'FINANCE_OFFICER', 'CFO'].includes(userRole);

  const fetchRFQs = async () => {
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      let url = `${API_BASE_URL}/rfqs?limit=100`;
      if (statusFilter) {
        url += `&status_filter=${statusFilter}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          setError('You don\'t have permission to view RFQs.');
          setRfqs([]);
          setLoading(false);
          return;
        }
        if (response.status === 404) {
          // RFQ endpoint might not exist yet
          setError('RFQ module is not fully configured yet.');
          setRfqs([]);
          setLoading(false);
          return;
        }
        throw new Error('Failed to load RFQs');
      }

      const data = await response.json();
      setRfqs(Array.isArray(data) ? data : []);
    } catch (err) {
      setError('Unable to load RFQs. Please try again.');
      setRfqs([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchPurchaseRequests = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/procurement/requests`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Filter only APPROVED purchase requests
        const approved = Array.isArray(data) 
          ? data.filter(req => req.status === 'APPROVED')
          : [];
        setPurchaseRequests(approved);
      }
    } catch (err) {
      console.error('Failed to fetch purchase requests:', err);
    }
  };

  const fetchVendors = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/vendors`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Handle both array and paginated response
        if (data.vendors && Array.isArray(data.vendors)) {
          setVendors(data.vendors);
        } else if (Array.isArray(data)) {
          setVendors(data);
        } else {
          setVendors([]);
        }
      }
    } catch (err) {
      console.error('Failed to fetch vendors:', err);
    }
  };

  const handleCreateRFQ = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const payload = {
        purchase_request_id: parseInt(formData.purchase_request_id),
        title: formData.title.trim(),
        description: formData.description || null,
        submission_deadline: new Date(formData.submission_deadline).toISOString(),
      };

      const response = await fetch(`${API_BASE_URL}/rfqs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You don\'t have permission to create RFQs.');
        }
        if (response.status === 409) {
          throw new Error(data.detail || 'An active RFQ already exists for this purchase request.');
        }
        if (response.status === 404) {
          throw new Error('Purchase request not found.');
        }
        throw new Error(data.detail || 'Failed to create RFQ');
      }

      setShowCreateModal(false);
      resetForm();
      await fetchRFQs();
    } catch (err) {
      setError(err.message || 'Unable to create RFQ. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleAddVendor = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/rfqs/${vendorForm.rfq_id}/vendors`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          vendor_id: parseInt(vendorForm.vendor_id),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error('Vendor already added to this RFQ.');
        }
        if (response.status === 404) {
          throw new Error('RFQ or Vendor not found.');
        }
        throw new Error(data.detail || 'Failed to add vendor');
      }

      setShowVendorModal(false);
      setVendorForm({ rfq_id: null, vendor_id: '' });
      await fetchRFQs();
      if (selectedRFQ && selectedRFQ.id === vendorForm.rfq_id) {
        const updated = rfqs.find(r => r.id === vendorForm.rfq_id);
        if (updated) setSelectedRFQ(updated);
      }
    } catch (err) {
      setError(err.message || 'Unable to add vendor. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleIssueRFQ = async (rfqId) => {
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/rfqs/${rfqId}/issue`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error(data.detail || 'RFQ cannot be issued in its current state.');
        }
        if (response.status === 400) {
          throw new Error(data.detail || 'Submission deadline must be in the future.');
        }
        throw new Error(data.detail || 'Failed to issue RFQ');
      }

      await fetchRFQs();
      if (selectedRFQ && selectedRFQ.id === rfqId) {
        const updated = rfqs.find(r => r.id === rfqId);
        if (updated) setSelectedRFQ(updated);
      }
    } catch (err) {
      setError(err.message || 'Unable to issue RFQ. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleCloseRFQ = async (rfqId) => {
    if (!window.confirm('Are you sure you want to close this RFQ?')) return;
    
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/rfqs/${rfqId}/close`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error(data.detail || 'RFQ cannot be closed in its current state.');
        }
        throw new Error(data.detail || 'Failed to close RFQ');
      }

      await fetchRFQs();
      if (selectedRFQ && selectedRFQ.id === rfqId) {
        const updated = rfqs.find(r => r.id === rfqId);
        if (updated) setSelectedRFQ(updated);
      }
    } catch (err) {
      setError(err.message || 'Unable to close RFQ. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleCancelRFQ = async (rfqId) => {
    if (!window.confirm('Are you sure you want to cancel this RFQ?')) return;
    
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/rfqs/${rfqId}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error(data.detail || 'RFQ cannot be cancelled in its current state.');
        }
        throw new Error(data.detail || 'Failed to cancel RFQ');
      }

      await fetchRFQs();
      if (selectedRFQ && selectedRFQ.id === rfqId) {
        const updated = rfqs.find(r => r.id === rfqId);
        if (updated) setSelectedRFQ(updated);
      }
    } catch (err) {
      setError(err.message || 'Unable to cancel RFQ. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const resetForm = () => {
    setFormData({
      purchase_request_id: '',
      title: '',
      description: '',
      submission_deadline: '',
    });
  };

  const canAddVendors = (rfq) => {
    return rfq.status === 'DRAFT';
  };

  const canIssue = (rfq) => {
    return rfq.status === 'DRAFT' && rfq.vendors && rfq.vendors.length > 0;
  };

  const canClose = (rfq) => {
    return rfq.status === 'ISSUED';
  };

  const canCancel = (rfq) => {
    return rfq.status === 'DRAFT' || rfq.status === 'ISSUED';
  };

  const getStatusColor = (status) => {
    const colors = {
      'DRAFT': 'status-draft',
      'ISSUED': 'status-issued',
      'CLOSED': 'status-closed',
      'CANCELLED': 'status-cancelled',
    };
    return colors[status] || 'status-default';
  };

  const filteredRFQs = rfqs.filter(rfq => {
    const searchLower = search.toLowerCase();
    return (
      (rfq.rfq_number || '').toLowerCase().includes(searchLower) ||
      (rfq.title || '').toLowerCase().includes(searchLower) ||
      (rfq.description || '').toLowerCase().includes(searchLower)
    );
  });

  // If user doesn't have RFQ permission
  if (!hasRFQPermission) {
    return (
      <div className="rfqs-page">
        <div className="rfqs-header">
          <h1 className="rfqs-title">RFQs</h1>
          <p className="rfqs-subtitle">Request for Quotations</p>
        </div>
        <div className="rfqs-readonly">
          <AlertCircle size={48} className="readonly-icon" />
          <p className="readonly-title">RFQ Permissions Required</p>
          <p className="readonly-description">
            Your role ({userRole || 'Employee'}) does not have RFQ permissions.
          </p>
          <p className="readonly-hint">
            RFQs are managed by Procurement Managers, Procurement Heads, and Finance.
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return <div className="rfqs-loading">Loading RFQs...</div>;
  }

  return (
    <div className="rfqs-page">
      <div className="rfqs-header">
        <div>
          <h1 className="rfqs-title">RFQs</h1>
          <p className="rfqs-subtitle">Request for Quotations</p>
        </div>
        <button 
          className="create-btn"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus size={18} />
          New RFQ
        </button>
      </div>

      {error && <div className="rfqs-error">{error}</div>}

      <div className="rfqs-toolbar">
        <div className="search-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search RFQs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-wrapper">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="ISSUED">Issued</option>
            <option value="CLOSED">Closed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
        <button className="refresh-btn" onClick={fetchRFQs}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {filteredRFQs.length === 0 ? (
        <div className="rfqs-empty">
          <FileText size={48} className="empty-icon" />
          <p>No RFQs found.</p>
          <p className="empty-hint">Create a new RFQ from an approved purchase request.</p>
        </div>
      ) : (
        <div className="rfqs-table-wrapper">
          <table className="rfqs-table">
            <thead>
              <tr>
                <th>RFQ Number</th>
                <th>Title</th>
                <th>Status</th>
                <th>Vendors</th>
                <th>Deadline</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRFQs.map((rfq) => (
                <tr key={rfq.id}>
                  <td className="rfq-number">{rfq.rfq_number}</td>
                  <td className="rfq-title">{rfq.title}</td>
                  <td>
                    <span className={`status-badge ${getStatusColor(rfq.status)}`}>
                      {rfq.status}
                    </span>
                  </td>
                  <td>{rfq.vendors?.length || 0}</td>
                  <td>
                    {rfq.submission_deadline 
                      ? new Date(rfq.submission_deadline).toLocaleDateString()
                      : '—'}
                  </td>
                  <td>{rfq.created_at ? new Date(rfq.created_at).toLocaleDateString() : '—'}</td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn view"
                        onClick={() => setSelectedRFQ(rfq)}
                        title="View Details"
                      >
                        <Eye size={16} />
                      </button>
                      
                      {canAddVendors(rfq) && (
                        <button 
                          className="action-btn vendor"
                          onClick={() => {
                            setVendorForm({ rfq_id: rfq.id, vendor_id: '' });
                            setShowVendorModal(true);
                          }}
                          title="Add Vendor"
                        >
                          <Building2 size={16} />
                        </button>
                      )}
                      
                      {canIssue(rfq) && (
                        <button 
                          className="action-btn issue"
                          onClick={() => handleIssueRFQ(rfq.id)}
                          disabled={processing}
                          title="Issue RFQ"
                        >
                          <Send size={16} />
                        </button>
                      )}
                      
                      {canClose(rfq) && (
                        <button 
                          className="action-btn close"
                          onClick={() => handleCloseRFQ(rfq.id)}
                          disabled={processing}
                          title="Close RFQ"
                        >
                          <CheckCircle size={16} />
                        </button>
                      )}
                      
                      {canCancel(rfq) && (
                        <button 
                          className="action-btn cancel"
                          onClick={() => handleCancelRFQ(rfq.id)}
                          disabled={processing}
                          title="Cancel RFQ"
                        >
                          <XCircle size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* View Details Modal */}
      {selectedRFQ && (
        <div className="modal-overlay" onClick={() => setSelectedRFQ(null)}>
          <div className="modal-content detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>{selectedRFQ.rfq_number}</h3>
                <span className={`status-badge ${getStatusColor(selectedRFQ.status)}`}>
                  {selectedRFQ.status}
                </span>
              </div>
              <button className="modal-close" onClick={() => setSelectedRFQ(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-row">
                <span className="detail-label">Title</span>
                <span>{selectedRFQ.title}</span>
              </div>
              {selectedRFQ.description && (
                <div className="detail-row">
                  <span className="detail-label">Description</span>
                  <span className="detail-value">{selectedRFQ.description}</span>
                </div>
              )}
              <div className="detail-row">
                <span className="detail-label">Purchase Request</span>
                <span>PR-{String(selectedRFQ.purchase_request_id).padStart(6, '0')}</span>
              </div>
              {selectedRFQ.issue_date && (
                <div className="detail-row">
                  <span className="detail-label">Issue Date</span>
                  <span>{new Date(selectedRFQ.issue_date).toLocaleString()}</span>
                </div>
              )}
              {selectedRFQ.submission_deadline && (
                <div className="detail-row">
                  <span className="detail-label">Submission Deadline</span>
                  <span>{new Date(selectedRFQ.submission_deadline).toLocaleString()}</span>
                </div>
              )}
              <div className="detail-row">
                <span className="detail-label">Created</span>
                <span>{new Date(selectedRFQ.created_at).toLocaleString()}</span>
              </div>
              
              {/* Items Section */}
              {selectedRFQ.items && selectedRFQ.items.length > 0 && (
                <div className="items-section">
                  <h4>Items ({selectedRFQ.items.length})</h4>
                  <table className="items-table">
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th>Description</th>
                        <th>Quantity</th>
                        <th>Unit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedRFQ.items.map((item, idx) => (
                        <tr key={idx}>
                          <td className="item-name">{item.item_name}</td>
                          <td className="item-desc">{item.description || '—'}</td>
                          <td>{item.quantity}</td>
                          <td>{item.unit}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Vendors Section */}
              {selectedRFQ.vendors && selectedRFQ.vendors.length > 0 && (
                <div className="vendors-section">
                  <h4>Vendors ({selectedRFQ.vendors.length})</h4>
                  <div className="vendors-list">
                    {selectedRFQ.vendors.map((v, idx) => (
                      <div key={idx} className="vendor-chip">
                        <Building2 size={14} />
                        <span>Vendor #{v.vendor_id}</span>
                        <span className={`vendor-status ${v.status?.toLowerCase()}`}>
                          {v.status || 'INVITED'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create RFQ Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content create-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New RFQ</h3>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleCreateRFQ}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="form-group">
                <label htmlFor="purchase_request">Purchase Request *</label>
                <select
                  id="purchase_request"
                  value={formData.purchase_request_id}
                  onChange={(e) => setFormData({ ...formData, purchase_request_id: e.target.value })}
                  required
                  disabled={processing}
                >
                  <option value="">Select approved purchase request</option>
                  {purchaseRequests.map((pr) => (
                    <option key={pr.id} value={pr.id}>
                      {pr.request_number} - {pr.title}
                    </option>
                  ))}
                </select>
                {purchaseRequests.length === 0 && (
                  <p className="form-hint">No approved purchase requests available. Please approve a purchase request first.</p>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input
                  id="title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                  minLength={1}
                  maxLength={255}
                  placeholder="Enter RFQ title"
                  disabled={processing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  placeholder="Enter description"
                  maxLength={5000}
                  disabled={processing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="deadline">Submission Deadline *</label>
                <input
                  id="deadline"
                  type="datetime-local"
                  value={formData.submission_deadline}
                  onChange={(e) => setFormData({ ...formData, submission_deadline: e.target.value })}
                  required
                  disabled={processing}
                />
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
                  disabled={processing || purchaseRequests.length === 0}
                >
                  {processing ? (
                    <>
                      <Loader2 size={16} className="spinner" />
                      Creating...
                    </>
                  ) : (
                    'Create RFQ'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Vendor Modal */}
      {showVendorModal && (
        <div className="modal-overlay" onClick={() => setShowVendorModal(false)}>
          <div className="modal-content vendor-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add Vendor to RFQ</h3>
              <button className="modal-close" onClick={() => setShowVendorModal(false)}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleAddVendor}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="form-group">
                <label htmlFor="vendor">Select Vendor *</label>
                <select
                  id="vendor"
                  value={vendorForm.vendor_id}
                  onChange={(e) => setVendorForm({ ...vendorForm, vendor_id: e.target.value })}
                  required
                  disabled={processing}
                >
                  <option value="">Choose a vendor</option>
                  {vendors.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name || v.vendor_name || `Vendor #${v.id}`}
                    </option>
                  ))}
                </select>
                {vendors.length === 0 && (
                  <p className="form-hint">No vendors available. Please add vendors first.</p>
                )}
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="modal-btn cancel"
                  onClick={() => setShowVendorModal(false)}
                  disabled={processing}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="modal-btn create"
                  disabled={processing || vendors.length === 0}
                >
                  {processing ? (
                    <>
                      <Loader2 size={16} className="spinner" />
                      Adding...
                    </>
                  ) : (
                    'Add Vendor'
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

export default RFQs;