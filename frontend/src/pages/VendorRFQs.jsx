import React, { useState, useEffect } from 'react';
import { 
  Eye, 
  RefreshCw, 
  Loader2,
  FileText,
  Clock,
  Building2,
  Send,
  CheckCircle,
  XCircle,
  AlertCircle,
  Calendar
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import StatusBadge from '../components/StatusBadge';
import './VendorRFQs.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function VendorRFQs({ vendorData }) {
  const [rfqs, setRfqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRFQ, setSelectedRFQ] = useState(null);
  const [showQuotationModal, setShowQuotationModal] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [quotationItems, setQuotationItems] = useState([]);
  const [quotationForm, setQuotationForm] = useState({
    currency: 'INR',
    tax_amount: 0,
    valid_until: '',
    notes: '',
  });

  useEffect(() => {
    fetchVendorRFQs();
  }, []);

  const fetchVendorRFQs = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('vendor_access_token');
      
      if (!token) {
        setError('Please login to view RFQs');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/vendor/rfqs`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('vendor_access_token');
          localStorage.removeItem('vendor_data');
          toast.error('Session expired. Please login again.');
          setTimeout(() => {
            window.location.href = '/vendor/login';
          }, 2000);
          return;
        }
        if (response.status === 403) {
          setError('You don\'t have permission to view RFQs.');
          setRfqs([]);
          setLoading(false);
          return;
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load RFQs');
      }

      const data = await response.json();
      setRfqs(Array.isArray(data) ? data : []);
      setError('');
      
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Unable to load RFQs. Please try again.');
      setRfqs([]);
    } finally {
      setLoading(false);
    }
  };

  const openQuotationModal = (rfq) => {
    setSelectedRFQ(rfq);
    if (rfq.items) {
      setQuotationItems(rfq.items.map(item => ({
        rfq_item_id: item.id,
        item_name: item.item_name,
        description: item.description || '',
        quantity: parseFloat(item.quantity) || 0,
        unit: item.unit || 'unit',
        unit_price: 0,
        total_price: 0,
      })));
    }
    setQuotationForm({
      currency: 'INR',
      tax_amount: 0,
      valid_until: '',
      notes: '',
    });
    setShowQuotationModal(true);
  };

  const updateItemPrice = (index, value) => {
    const newItems = [...quotationItems];
    const unitPrice = parseFloat(value) || 0;
    newItems[index].unit_price = unitPrice;
    newItems[index].total_price = unitPrice * newItems[index].quantity;
    setQuotationItems(newItems);
  };

  const calculateSubtotal = () => {
    return quotationItems.reduce((sum, item) => sum + item.total_price, 0);
  };

  const calculateTotal = () => {
    return calculateSubtotal() + (parseFloat(quotationForm.tax_amount) || 0);
  };

  const handleSubmitQuotation = async (e) => {
  e.preventDefault();
  setProcessing(true);
  setError('');

  try {
    const token = localStorage.getItem('vendor_access_token');
    
    // Check if all items have prices
    const hasEmptyPrices = quotationItems.some(item => item.unit_price <= 0);
    if (hasEmptyPrices) {
      toast.error('Please enter prices for all items');
      setProcessing(false);
      return;
    }

    // Prepare payload matching backend schema
    const payload = {
      rfq_id: selectedRFQ.id,
      currency: quotationForm.currency,
      tax_amount: parseFloat(quotationForm.tax_amount) || 0,
      valid_until: quotationForm.valid_until || null,
      notes: quotationForm.notes || null,
      items: quotationItems.map(item => ({
        rfq_item_id: item.rfq_item_id,
        unit_price: item.unit_price,
      })),
    };

    console.log('Submitting quotation:', payload);

    const response = await fetch(`${API_BASE_URL}/vendor/rfqs/${selectedRFQ.id}/submit-quotation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to submit quotation');
    }

    // Close modal and show success
    setShowQuotationModal(false);
    toast.success('Quotation submitted successfully! 🎉');
    
    // Refresh the list
    await fetchVendorRFQs();
    
  } catch (err) {
    toast.error(err.message || 'Unable to submit quotation. Please try again.');
    setError(err.message || 'Unable to submit quotation. Please try again.');
  } finally {
    setProcessing(false);
  }
};

  const formatDate = (dateString) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleDateString();
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="vendor-rfqs-loading">
        <Loader2 size={32} className="spinner" />
        <span>Loading RFQs...</span>
      </div>
    );
  }

  return (
    <div className="vendor-rfqs-page">
      {/* Toaster Component */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 4000,
            icon: '✅',
            style: {
              background: '#0a1628',
              color: '#fff',
            },
          },
          error: {
            duration: 5000,
            icon: '❌',
            style: {
              background: '#9b2c2c',
              color: '#fff',
            },
          },
        }}
      />

      <div className="vendor-rfqs-header">
        <div>
          <h1 className="vendor-rfqs-title">My RFQs</h1>
          <p className="vendor-rfqs-subtitle">Request for Quotations you've been invited to</p>
          {rfqs.length > 0 && (
            <span className="vendor-rfqs-count">{rfqs.length} RFQ{rfqs.length > 1 ? 's' : ''}</span>
          )}
        </div>
        <button className="refresh-btn" onClick={fetchVendorRFQs}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && <div className="vendor-rfqs-error">{error}</div>}

      {rfqs.length === 0 ? (
        <div className="vendor-rfqs-empty">
          <FileText size={48} className="empty-icon" />
          <p>No RFQs available</p>
          <p className="empty-hint">You haven't been invited to any RFQs yet.</p>
        </div>
      ) : (
        <div className="vendor-rfqs-list">
          {rfqs.map((rfq) => (
            <div key={rfq.id} className="vendor-rfq-card">
              <div className="rfq-card-header">
                <div className="rfq-card-title">
                  <span className="rfq-number">{rfq.rfq_number}</span>
                  <span className="rfq-title">{rfq.title}</span>
                </div>
                <StatusBadge status={rfq.status} />
              </div>
              <div className="rfq-card-body">
                <div className="rfq-meta">
                  <span className="meta-item">
                    <Clock size={14} />
                    Deadline: {formatDateTime(rfq.submission_deadline)}
                  </span>
                  <span className="meta-item">
                    <FileText size={14} />
                    {rfq.items?.length || 0} items
                  </span>
                  {rfq.issue_date && (
                    <span className="meta-item">
                      <Calendar size={14} />
                      Issued: {formatDate(rfq.issue_date)}
                    </span>
                  )}
                </div>
                {rfq.description && (
                  <div className="rfq-description">{rfq.description}</div>
                )}
              </div>
              <div className="rfq-card-actions">
                <button 
                  className="rfq-btn view"
                  onClick={() => setSelectedRFQ(rfq)}
                >
                  <Eye size={16} />
                  View Details
                </button>
                {rfq.status === 'ISSUED' && (
                  <button 
                    className="rfq-btn submit"
                    onClick={() => openQuotationModal(rfq)}
                  >
                    <Send size={16} />
                    Submit Quotation
                  </button>
                )}
                {rfq.status === 'CLOSED' && (
                  <button 
                    className="rfq-btn closed"
                    disabled
                  >
                    <XCircle size={16} />
                    Closed
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* View RFQ Modal */}
      {selectedRFQ && !showQuotationModal && (
        <div className="modal-overlay" onClick={() => setSelectedRFQ(null)}>
          <div className="modal-content detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>{selectedRFQ.rfq_number}</h3>
                <StatusBadge status={selectedRFQ.status} />
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
                  <span>{selectedRFQ.description}</span>
                </div>
              )}
              {selectedRFQ.submission_deadline && (
                <div className="detail-row">
                  <span className="detail-label">Submission Deadline</span>
                  <span>{formatDateTime(selectedRFQ.submission_deadline)}</span>
                </div>
              )}
              {selectedRFQ.issue_date && (
                <div className="detail-row">
                  <span className="detail-label">Issue Date</span>
                  <span>{formatDateTime(selectedRFQ.issue_date)}</span>
                </div>
              )}
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
            </div>
          </div>
        </div>
      )}

      {/* Submit Quotation Modal */}
      {showQuotationModal && selectedRFQ && (
        <div className="modal-overlay" onClick={() => setShowQuotationModal(false)}>
          <div className="modal-content quotation-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Submit Quotation</h3>
              <button className="modal-close" onClick={() => setShowQuotationModal(false)}>×</button>
            </div>
            <form className="modal-body" onSubmit={handleSubmitQuotation}>
              {error && <div className="form-error">{error}</div>}
              
              <div className="quotation-info">
                <p><strong>RFQ:</strong> {selectedRFQ.rfq_number}</p>
                <p><strong>Title:</strong> {selectedRFQ.title}</p>
              </div>

              <div className="quotation-items-list">
                <h4>Items & Pricing</h4>
                {quotationItems.map((item, index) => (
                  <div key={index} className="quotation-item-row">
                    <div className="item-info">
                      <span className="item-name">{item.item_name}</span>
                      <span className="item-specs">
                        {item.quantity} {item.unit}
                        {item.description && ` - ${item.description}`}
                      </span>
                    </div>
                    <div className="item-price-input">
                      <label>Unit Price ({quotationForm.currency})</label>
                      <input
                        type="number"
                        value={item.unit_price || ''}
                        onChange={(e) => updateItemPrice(index, e.target.value)}
                        min="0"
                        step="0.01"
                        required
                        placeholder="0.00"
                      />
                      <span className="item-total">
                        Total: {quotationForm.currency} {item.total_price.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="quotation-totals">
                <div className="total-row">
                  <span>Subtotal:</span>
                  <span>{quotationForm.currency} {calculateSubtotal().toFixed(2)}</span>
                </div>
                <div className="total-row">
                  <span>Tax:</span>
                  <input
                    type="number"
                    value={quotationForm.tax_amount}
                    onChange={(e) => setQuotationForm({ ...quotationForm, tax_amount: parseFloat(e.target.value) || 0 })}
                    min="0"
                    step="0.01"
                    className="tax-input"
                  />
                </div>
                <div className="total-row grand-total">
                  <span>Grand Total:</span>
                  <span>{quotationForm.currency} {calculateTotal().toFixed(2)}</span>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Currency</label>
                  <select
                    value={quotationForm.currency}
                    onChange={(e) => setQuotationForm({ ...quotationForm, currency: e.target.value })}
                  >
                    <option value="INR">INR</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Valid Until</label>
                  <input
                    type="date"
                    value={quotationForm.valid_until}
                    onChange={(e) => setQuotationForm({ ...quotationForm, valid_until: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Notes</label>
                <textarea
                  value={quotationForm.notes}
                  onChange={(e) => setQuotationForm({ ...quotationForm, notes: e.target.value })}
                  rows={3}
                  placeholder="Additional notes for the quotation..."
                />
              </div>

              <div className="modal-actions">
                <button 
                  type="button" 
                  className="modal-btn cancel"
                  onClick={() => {
                    setShowQuotationModal(false);
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
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Submit Quotation
                    </>
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

export default VendorRFQs;