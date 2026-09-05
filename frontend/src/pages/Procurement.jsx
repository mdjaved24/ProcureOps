import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Eye, 
  Send, 
  FileCheck, 
  ClipboardCheck,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Edit2,
  RefreshCw,
  Loader2,
  Trash2
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import './Procurement.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function Procurement({ user }) {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();

  // Create form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    currency: 'INR',
    required_by_date: '',
    items: [
      {
        item_name: '',
        description: '',
        quantity: 1,
        unit: 'unit',
        estimated_unit_price: 0,
      }
    ]
  });

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/procurement/requests`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          setError('You don\'t have permission to view procurement requests.');
          setRequests([]);
          setLoading(false);
          return;
        }
        throw new Error('Failed to load procurement requests');
      }

      const data = await response.json();
      setRequests(Array.isArray(data) ? data : []);
    } catch (err) {
      setError('Unable to load procurement requests. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRequest = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      
      // Calculate total estimated amount
      const estimatedAmount = formData.items.reduce((sum, item) => {
        return sum + (Number(item.quantity) * Number(item.estimated_unit_price));
      }, 0);

      const payload = {
        title: formData.title,
        description: formData.description || null,
        currency: formData.currency,
        required_by_date: formData.required_by_date || null,
        items: formData.items.map(item => ({
          item_name: item.item_name,
          description: item.description || null,
          quantity: Number(item.quantity),
          unit: item.unit || 'unit',
          estimated_unit_price: Number(item.estimated_unit_price),
        })),
      };

      const response = await fetch(`${API_BASE_URL}/procurement/requests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 400) {
          throw new Error(data.detail || 'Invalid request data');
        } else if (response.status === 403) {
          throw new Error('You don\'t have permission to create procurement requests.');
        } else {
          throw new Error(data.detail || 'Failed to create request');
        }
      }

      setShowCreateModal(false);
      resetForm();
      await fetchRequests();
    } catch (err) {
      setError(err.message || 'Unable to create request. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleSubmitRequest = async (requestId) => {
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/procurement/requests/${requestId}/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('Only the request owner can submit this request.');
        } else if (response.status === 404) {
          throw new Error('Purchase request not found.');
        }
        throw new Error(data.detail || 'Failed to submit request');
      }

      setShowSubmitModal(false);
      await fetchRequests();
    } catch (err) {
      setError(err.message || 'Unable to submit request. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleStartReview = async (requestId) => {
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/procurement/requests/${requestId}/start-review`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You don\'t have permission to review requests.');
        }
        throw new Error(data.detail || 'Failed to start review');
      }

      await fetchRequests();
    } catch (err) {
      setError(err.message || 'Unable to start review. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleEvaluate = async (requestId) => {
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/procurement/requests/${requestId}/evaluate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You don\'t have permission to evaluate requests.');
        } else if (response.status === 409) {
          throw new Error(data.detail || 'Request evaluation conflict.');
        }
        throw new Error(data.detail || 'Failed to evaluate request');
      }

      await fetchRequests();
    } catch (err) {
      setError(err.message || 'Unable to evaluate request. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const canSubmit = (request) => {
    if (!user) return false;
    return request.status === 'DRAFT' && 
           request.requester_id === user.id;
  };

  const canStartReview = (request) => {
    const role = user?.role?.toUpperCase();
    return request.status === 'SUBMITTED' && 
           ['ADMIN', 'PROCUREMENT_MANAGER', 'PROCUREMENT_HEAD', 'PROCUREMENT_ANALYST'].includes(role);
  };

  const canEvaluate = (request) => {
    const role = user?.role?.toUpperCase();
    return request.status === 'UNDER_REVIEW' && 
           ['ADMIN', 'PROCUREMENT_MANAGER', 'PROCUREMENT_HEAD'].includes(role);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      currency: 'INR',
      required_by_date: '',
      items: [
        {
          item_name: '',
          description: '',
          quantity: 1,
          unit: 'unit',
          estimated_unit_price: 0,
        }
      ]
    });
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [
        ...formData.items,
        {
          item_name: '',
          description: '',
          quantity: 1,
          unit: 'unit',
          estimated_unit_price: 0,
        }
      ]
    });
  };

  const removeItem = (index) => {
    if (formData.items.length === 1) return;
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const updateItem = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  const getTotalAmount = () => {
    return formData.items.reduce((sum, item) => {
      return sum + (Number(item.quantity) * Number(item.estimated_unit_price));
    }, 0);
  };

  const filteredRequests = requests.filter(req => {
    const searchLower = search.toLowerCase();
    return (
      (req.request_number || '').toLowerCase().includes(searchLower) ||
      (req.title || '').toLowerCase().includes(searchLower) ||
      (req.description || '').toLowerCase().includes(searchLower)
    );
  });

  if (loading) {
    return <div className="procurement-loading">Loading procurement requests...</div>;
  }

  return (
    <div className="procurement-page">
      <div className="procurement-header">
        <div>
          <h1 className="procurement-title">Procurement</h1>
          <p className="procurement-subtitle">Manage purchase requests</p>
        </div>
        <button 
          className="create-btn"
          onClick={() => setShowCreateModal(true)}
        >
          <Plus size={18} />
          New Request
        </button>
      </div>

      {error && <div className="procurement-error">{error}</div>}

      <div className="procurement-toolbar">
        <div className="search-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search requests..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>
        <button className="refresh-btn" onClick={fetchRequests}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {filteredRequests.length === 0 ? (
        <div className="procurement-empty">
          <p>No procurement requests found.</p>
          <p className="empty-hint">Create a new purchase request to get started.</p>
        </div>
      ) : (
        <div className="procurement-table-wrapper">
          <table className="procurement-table">
            <thead>
              <tr>
                <th>Request Number</th>
                <th>Title</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRequests.map((req) => (
                <tr key={req.id}>
                  <td className="req-number">{req.request_number}</td>
                  <td>{req.title}</td>
                  <td><StatusBadge status={req.status} /></td>
                  <td>₹{req.estimated_amount?.toLocaleString() || 0}</td>
                  <td>{req.created_at ? new Date(req.created_at).toLocaleDateString() : '—'}</td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn view"
                        onClick={() => setSelectedRequest(req)}
                        title="View Details"
                      >
                        <Eye size={16} />
                      </button>
                      
                      {canSubmit(req) && (
                        <button 
                          className="action-btn submit"
                          onClick={() => {
                            setSelectedRequest(req);
                            setShowSubmitModal(true);
                          }}
                          title="Submit for Review"
                        >
                          <Send size={16} />
                        </button>
                      )}
                      
                      {canStartReview(req) && (
                        <button 
                          className="action-btn review"
                          onClick={() => handleStartReview(req.id)}
                          disabled={processing}
                          title="Start Review"
                        >
                          <ClipboardCheck size={16} />
                        </button>
                      )}
                      
                      {canEvaluate(req) && (
                        <button 
                          className="action-btn evaluate"
                          onClick={() => handleEvaluate(req.id)}
                          disabled={processing}
                          title="Evaluate & Create Approval"
                        >
                          <FileCheck size={16} />
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
      {selectedRequest && !showSubmitModal && (
        <div className="modal-overlay" onClick={() => setSelectedRequest(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedRequest.request_number}</h3>
              <button className="modal-close" onClick={() => setSelectedRequest(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-row">
                <span className="detail-label">Title</span>
                <span>{selectedRequest.title}</span>
              </div>
              {selectedRequest.description && (
                <div className="detail-row">
                  <span className="detail-label">Description</span>
                  <span>{selectedRequest.description}</span>
                </div>
              )}
              <div className="detail-row">
                <span className="detail-label">Status</span>
                <StatusBadge status={selectedRequest.status} />
              </div>
              <div className="detail-row">
                <span className="detail-label">Estimated Amount</span>
                <span>₹{selectedRequest.estimated_amount?.toLocaleString()}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Currency</span>
                <span>{selectedRequest.currency}</span>
              </div>
              {selectedRequest.required_by_date && (
                <div className="detail-row">
                  <span className="detail-label">Required By</span>
                  <span>{new Date(selectedRequest.required_by_date).toLocaleDateString()}</span>
                </div>
              )}
              <div className="detail-row">
                <span className="detail-label">Created</span>
                <span>{new Date(selectedRequest.created_at).toLocaleString()}</span>
              </div>
              {selectedRequest.items && selectedRequest.items.length > 0 && (
                <div className="items-section">
                  <h4>Items</h4>
                  <table className="items-table">
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedRequest.items.map((item, idx) => (
                        <tr key={idx}>
                          <td>{item.item_name}</td>
                          <td>{item.quantity}</td>
                          <td>₹{item.estimated_unit_price?.toLocaleString()}</td>
                          <td>₹{item.total_price?.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Submit Confirmation Modal */}
      {showSubmitModal && selectedRequest && (
        <div className="modal-overlay" onClick={() => setShowSubmitModal(false)}>
          <div className="modal-content confirmation-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Submit for Review</h3>
              <button className="modal-close" onClick={() => setShowSubmitModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="confirmation-icon">
                <AlertCircle size={48} />
              </div>
              <p className="confirmation-text">
                Are you sure you want to submit <strong>{selectedRequest.request_number}</strong> for review?
              </p>
              <p className="confirmation-subtext">
                Once submitted, the request will be reviewed by the procurement team.
              </p>
              <div className="confirmation-actions">
                <button 
                  className="confirmation-btn cancel"
                  onClick={() => setShowSubmitModal(false)}
                  disabled={processing}
                >
                  Cancel
                </button>
                <button 
                  className="confirmation-btn confirm"
                  onClick={() => handleSubmitRequest(selectedRequest.id)}
                  disabled={processing}
                >
                  {processing ? (
                    <>
                      <Loader2 size={16} className="spinner" />
                      Submitting...
                    </>
                  ) : (
                    'Submit Request'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Request Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content create-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>New Purchase Request</h3>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleCreateRequest}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="form-group">
                <label htmlFor="title">Title *</label>
                <input
                  id="title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                  minLength={3}
                  maxLength={255}
                  placeholder="Enter request title"
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
                  disabled={processing}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="currency">Currency</label>
                  <select
                    id="currency"
                    value={formData.currency}
                    onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                    disabled={processing}
                  >
                    <option value="INR">INR</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="required_by">Required By</label>
                  <input
                    id="required_by"
                    type="date"
                    value={formData.required_by_date}
                    onChange={(e) => setFormData({ ...formData, required_by_date: e.target.value })}
                    disabled={processing}
                  />
                </div>
              </div>

              <div className="items-section-header">
                <h4>Items</h4>
                <button type="button" className="add-item-btn" onClick={addItem} disabled={processing}>
                  <Plus size={16} />
                  Add Item
                </button>
              </div>

              <div className="items-container">
                {formData.items.map((item, index) => (
                  <div key={index} className="item-card">
                    <div className="item-card-header">
                      <span className="item-number">Item #{index + 1}</span>
                      {formData.items.length > 1 && (
                        <button
                          type="button"
                          className="remove-item-btn"
                          onClick={() => removeItem(index)}
                          disabled={processing}
                          title="Remove item"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                    <div className="item-card-body">
                      <div className="item-field">
                        <label>Item Name *</label>
                        <input
                          type="text"
                          value={item.item_name}
                          onChange={(e) => updateItem(index, 'item_name', e.target.value)}
                          required
                          placeholder="Enter item name"
                          disabled={processing}
                        />
                      </div>
                      <div className="item-field">
                        <label>Description</label>
                        <input
                          type="text"
                          value={item.description}
                          onChange={(e) => updateItem(index, 'description', e.target.value)}
                          placeholder="Item description"
                          disabled={processing}
                        />
                      </div>
                      <div className="item-field-small">
                        <label>Quantity *</label>
                        <input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => updateItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                          required
                          min="0.01"
                          step="0.01"
                          disabled={processing}
                        />
                      </div>
                      <div className="item-field-small">
                        <label>Unit</label>
                        <input
                          type="text"
                          value={item.unit}
                          onChange={(e) => updateItem(index, 'unit', e.target.value)}
                          placeholder="unit"
                          disabled={processing}
                        />
                      </div>
                      <div className="item-field-small">
                        <label>Unit Price *</label>
                        <input
                          type="number"
                          value={item.estimated_unit_price}
                          onChange={(e) => updateItem(index, 'estimated_unit_price', parseFloat(e.target.value) || 0)}
                          required
                          min="0.01"
                          step="0.01"
                          disabled={processing}
                        />
                      </div>
                      <div className="item-field-total">
                        <label>Total</label>
                        <span className="item-total-price">
                          ₹{(Number(item.quantity) * Number(item.estimated_unit_price)).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="total-amount">
                <span>Total Estimated Amount:</span>
                <strong>₹{getTotalAmount().toLocaleString()}</strong>
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
                    'Create Request'
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

export default Procurement;