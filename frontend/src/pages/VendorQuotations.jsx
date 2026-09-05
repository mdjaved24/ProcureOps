import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  Loader2,
  FileCheck,
  Eye,
  XCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Calendar
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import StatusBadge from '../components/StatusBadge';
import './VendorQuotations.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function VendorQuotations({ vendorData }) {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedQuotation, setSelectedQuotation] = useState(null);

  useEffect(() => {
    fetchVendorQuotations();
  }, []);

  const fetchVendorQuotations = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('vendor_access_token');
      
      if (!token) {
        setError('Please login to view quotations');
        setLoading(false);
        return;
      }

      // Use vendor-specific endpoint
      const response = await fetch(`${API_BASE_URL}/vendor/quotations`, {
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
          setError('You don\'t have permission to view quotations.');
          setQuotations([]);
          setLoading(false);
          return;
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load quotations');
      }

      const data = await response.json();
      setQuotations(Array.isArray(data) ? data : []);
      
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Unable to load quotations. Please try again.');
      setQuotations([]);
    } finally {
      setLoading(false);
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

  const formatCurrency = (amount, currency = 'INR') => {
    if (amount === undefined || amount === null) return '—';
    return `${currency} ${Number(amount).toFixed(2)}`;
  };

  const getStatusIcon = (status) => {
    switch (status?.toUpperCase()) {
      case 'SUBMITTED':
        return <Clock size={16} className="status-icon submitted" />;
      case 'ACCEPTED':
        return <CheckCircle size={16} className="status-icon accepted" />;
      case 'REJECTED':
        return <XCircle size={16} className="status-icon rejected" />;
      case 'WITHDRAWN':
        return <XCircle size={16} className="status-icon withdrawn" />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="vendor-quotations-loading">
        <Loader2 size={32} className="spinner" />
        <span>Loading quotations...</span>
      </div>
    );
  }

  return (
    <div className="vendor-quotations-page">
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

      <div className="vendor-quotations-header">
        <div>
          <h1 className="vendor-quotations-title">My Quotations</h1>
          <p className="vendor-quotations-subtitle">Quotations you've submitted</p>
          {quotations.length > 0 && (
            <span className="vendor-quotations-count">
              {quotations.length} Quotation{quotations.length > 1 ? 's' : ''}
            </span>
          )}
        </div>
        <button className="refresh-btn" onClick={fetchVendorQuotations}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && <div className="vendor-quotations-error">{error}</div>}

      {quotations.length === 0 ? (
        <div className="vendor-quotations-empty">
          <FileCheck size={48} className="empty-icon" />
          <p>No quotations submitted</p>
          <p className="empty-hint">Submit your first quotation from the RFQs page.</p>
        </div>
      ) : (
        <div className="vendor-quotations-list">
          {quotations.map((quotation) => (
            <div key={quotation.id} className="vendor-quotation-card">
              <div className="quotation-card-header">
                <div className="quotation-card-title">
                  <span className="quotation-number">{quotation.quotation_number}</span>
                  <span className="quotation-rfq">
                    {quotation.rfq_vendor_id ? `RFQ-Vendor #${quotation.rfq_vendor_id}` : '—'}
                  </span>
                </div>
                <div className="quotation-status">
                  {getStatusIcon(quotation.status)}
                  <StatusBadge status={quotation.status} />
                </div>
              </div>
              <div className="quotation-card-body">
                <div className="quotation-meta">
                  <span className="meta-item">
                    <DollarSign size={14} />
                    Amount: {formatCurrency(quotation.total_amount, quotation.currency)}
                  </span>
                  <span className="meta-item">
                    <Calendar size={14} />
                    Submitted: {formatDateTime(quotation.submitted_at)}
                  </span>
                  {quotation.valid_until && (
                    <span className="meta-item">
                      <Calendar size={14} />
                      Valid until: {formatDate(quotation.valid_until)}
                    </span>
                  )}
                </div>
                {quotation.notes && (
                  <div className="quotation-notes">{quotation.notes}</div>
                )}
              </div>
              <div className="quotation-card-actions">
                <button 
                  className="quotation-btn view"
                  onClick={() => setSelectedQuotation(quotation)}
                >
                  <Eye size={16} />
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* View Quotation Modal */}
      {selectedQuotation && (
        <div className="modal-overlay" onClick={() => setSelectedQuotation(null)}>
          <div className="modal-content detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>{selectedQuotation.quotation_number}</h3>
                <StatusBadge status={selectedQuotation.status} />
              </div>
              <button className="modal-close" onClick={() => setSelectedQuotation(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-row">
                <span className="detail-label">RFQ Vendor</span>
                <span>#{selectedQuotation.rfq_vendor_id}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Currency</span>
                <span>{selectedQuotation.currency || 'INR'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Subtotal</span>
                <span>{formatCurrency(selectedQuotation.subtotal, selectedQuotation.currency)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Tax</span>
                <span>{formatCurrency(selectedQuotation.tax_amount, selectedQuotation.currency)}</span>
              </div>
              <div className="detail-row highlight">
                <span className="detail-label">Total Amount</span>
                <span className="highlight-amount">
                  {formatCurrency(selectedQuotation.total_amount, selectedQuotation.currency)}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Submitted</span>
                <span>{formatDateTime(selectedQuotation.submitted_at)}</span>
              </div>
              {selectedQuotation.valid_until && (
                <div className="detail-row">
                  <span className="detail-label">Valid Until</span>
                  <span>{formatDate(selectedQuotation.valid_until)}</span>
                </div>
              )}
              {selectedQuotation.notes && (
                <div className="detail-row full-width">
                  <span className="detail-label">Notes</span>
                  <span className="notes-text">{selectedQuotation.notes}</span>
                </div>
              )}

              {selectedQuotation.items && selectedQuotation.items.length > 0 && (
                <div className="items-section">
                  <h4>Items ({selectedQuotation.items.length})</h4>
                  <table className="items-table">
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th>Description</th>
                        <th>Qty</th>
                        <th>Unit</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedQuotation.items.map((item, idx) => (
                        <tr key={idx}>
                          <td className="item-name">{item.item_name}</td>
                          <td className="item-desc">{item.description || '—'}</td>
                          <td>{item.quantity}</td>
                          <td>{item.unit}</td>
                          <td>{formatCurrency(item.unit_price, selectedQuotation.currency)}</td>
                          <td className="item-total">
                            {formatCurrency(item.total_price, selectedQuotation.currency)}
                          </td>
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
    </div>
  );
}

export default VendorQuotations;