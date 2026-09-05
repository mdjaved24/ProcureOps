import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Eye, 
  RefreshCw,
  Loader2,
  FileText,
  DollarSign,
  Calendar,
  Building2,
  TrendingUp,
  TrendingDown,
  Minus,
  XCircle
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import './Quotations.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function Quotations({ user }) {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selectedQuotation, setSelectedQuotation] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [showComparison, setShowComparison] = useState(false);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchQuotations();
  }, []);

  const fetchQuotations = async () => {
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/quotations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          setError('You don\'t have permission to view quotations.');
          setQuotations([]);
          setLoading(false);
          return;
        }
        throw new Error('Failed to load quotations');
      }

      const data = await response.json();
      setQuotations(Array.isArray(data) ? data : []);
    } catch (err) {
      setError('Unable to load quotations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchQuotationDetails = async (quotationId) => {
    setProcessing(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/quotations/${quotationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load quotation details');
      }

      const data = await response.json();
      setSelectedQuotation(data);
    } catch (err) {
      setError('Unable to load quotation details. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const fetchComparison = async (rfqId) => {
    setProcessing(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/quotations/rfq/${rfqId}/compare`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error('Quotations can only be compared after the RFQ is closed.');
        }
        throw new Error('Failed to load comparison data');
      }

      const data = await response.json();
      setComparisonData(data);
      setShowComparison(true);
    } catch (err) {
      setError(err.message || 'Unable to load comparison. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleWithdraw = async (quotationId) => {
    if (!window.confirm('Are you sure you want to withdraw this quotation?')) return;
    
    setProcessing(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/quotations/${quotationId}/withdraw`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error('Only submitted quotations can be withdrawn.');
        }
        throw new Error('Failed to withdraw quotation');
      }

      await fetchQuotations();
      if (selectedQuotation && selectedQuotation.id === quotationId) {
        setSelectedQuotation(null);
      }
    } catch (err) {
      setError(err.message || 'Unable to withdraw quotation. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'SUBMITTED': 'status-submitted',
      'ACCEPTED': 'status-accepted',
      'REJECTED': 'status-rejected',
      'WITHDRAWN': 'status-withdrawn',
      'DRAFT': 'status-draft',
    };
    return colors[status] || 'status-default';
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return <TrendingUp size={14} className="rank-icon first" />;
    if (rank === 2) return <TrendingUp size={14} className="rank-icon second" />;
    if (rank === 3) return <TrendingUp size={14} className="rank-icon third" />;
    return <Minus size={14} className="rank-icon other" />;
  };

  const filteredQuotations = quotations.filter(q => {
    const searchLower = search.toLowerCase();
    return (
      (q.quotation_number || '').toLowerCase().includes(searchLower) ||
      (q.vendor_name || '').toLowerCase().includes(searchLower) ||
      (q.rfq_number || '').toLowerCase().includes(searchLower)
    );
  });

  if (loading) {
    return <div className="quotations-loading">Loading quotations...</div>;
  }

  return (
    <div className="quotations-page">
      <div className="quotations-header">
        <div>
          <h1 className="quotations-title">Quotations</h1>
          <p className="quotations-subtitle">Manage vendor quotations</p>
          {quotations.length > 0 && (
            <span className="quotations-count">{quotations.length} quotations</span>
          )}
        </div>
        <button className="refresh-btn" onClick={fetchQuotations}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && <div className="quotations-error">{error}</div>}

      <div className="quotations-toolbar">
        <div className="search-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search by number, vendor, or RFQ..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      {filteredQuotations.length === 0 ? (
        <div className="quotations-empty">
          <FileText size={48} className="empty-icon" />
          <p>No quotations found.</p>
          <p className="empty-hint">Quotations will appear here once vendors submit them.</p>
        </div>
      ) : (
        <div className="quotations-table-wrapper">
          <table className="quotations-table">
            <thead>
              <tr>
                <th>Quotation</th>
                <th>RFQ</th>
                <th>Vendor</th>
                <th>Total Amount</th>
                <th>Status</th>
                <th>Submitted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredQuotations.map((q) => (
                <tr key={q.id}>
                  <td className="q-number">{q.quotation_number}</td>
                  <td>{q.rfq_number || '—'}</td>
                  <td className="q-vendor">{q.vendor_name || '—'}</td>
                  <td className="q-amount">
                    {q.currency || 'INR'} {q.total_amount?.toLocaleString() || '—'}
                  </td>
                  <td>
                    <span className={`status-badge ${getStatusColor(q.status)}`}>
                      {q.status || 'DRAFT'}
                    </span>
                  </td>
                  <td className="q-date">
                    {q.submitted_at ? new Date(q.submitted_at).toLocaleDateString() : '—'}
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn view"
                        onClick={() => fetchQuotationDetails(q.id)}
                        title="View Details"
                      >
                        <Eye size={16} />
                      </button>
                      {q.status === 'SUBMITTED' && q.rfq_id && (
                        <button 
                          className="action-btn compare"
                          onClick={() => fetchComparison(q.rfq_id)}
                          title="Compare Quotations"
                        >
                          <TrendingUp size={16} />
                        </button>
                      )}
                      {q.status === 'SUBMITTED' && (
                        <button 
                          className="action-btn withdraw"
                          onClick={() => handleWithdraw(q.id)}
                          disabled={processing}
                          title="Withdraw Quotation"
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
      {selectedQuotation && (
        <div className="modal-overlay" onClick={() => setSelectedQuotation(null)}>
          <div className="modal-content detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>{selectedQuotation.quotation_number}</h3>
                <span className={`status-badge ${getStatusColor(selectedQuotation.status)}`}>
                  {selectedQuotation.status || 'DRAFT'}
                </span>
              </div>
              <button className="modal-close" onClick={() => setSelectedQuotation(null)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">RFQ Vendor</span>
                  <span className="detail-value">#{selectedQuotation.rfq_vendor_id}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Currency</span>
                  <span className="detail-value">{selectedQuotation.currency || 'INR'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Subtotal</span>
                  <span className="detail-value">₹{selectedQuotation.subtotal?.toLocaleString() || '—'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Tax Amount</span>
                  <span className="detail-value">₹{selectedQuotation.tax_amount?.toLocaleString() || '—'}</span>
                </div>
                <div className="detail-item highlight">
                  <span className="detail-label">Total Amount</span>
                  <span className="detail-value highlight-amount">
                    ₹{selectedQuotation.total_amount?.toLocaleString() || '—'}
                  </span>
                </div>
                {selectedQuotation.valid_until && (
                  <div className="detail-item">
                    <span className="detail-label">Valid Until</span>
                    <span className="detail-value">
                      <Calendar size={14} className="detail-icon" />
                      {new Date(selectedQuotation.valid_until).toLocaleString()}
                    </span>
                  </div>
                )}
                {selectedQuotation.submitted_at && (
                  <div className="detail-item">
                    <span className="detail-label">Submitted</span>
                    <span className="detail-value">
                      {new Date(selectedQuotation.submitted_at).toLocaleString()}
                    </span>
                  </div>
                )}
                {selectedQuotation.notes && (
                  <div className="detail-item full-width">
                    <span className="detail-label">Notes</span>
                    <span className="detail-value notes">{selectedQuotation.notes}</span>
                  </div>
                )}
              </div>

              {/* Items Section */}
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
                          <td>₹{item.unit_price?.toLocaleString()}</td>
                          <td className="item-total">₹{item.total_price?.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="modal-actions">
                {selectedQuotation.status === 'SUBMITTED' && (
                  <button 
                    className="modal-btn withdraw-btn"
                    onClick={() => {
                      handleWithdraw(selectedQuotation.id);
                      setSelectedQuotation(null);
                    }}
                    disabled={processing}
                  >
                    <XCircle size={16} />
                    Withdraw Quotation
                  </button>
                )}
                <button 
                  className="modal-btn close-btn"
                  onClick={() => setSelectedQuotation(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Comparison Modal */}
      {showComparison && comparisonData && (
        <div className="modal-overlay" onClick={() => setShowComparison(false)}>
          <div className="modal-content comparison-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>Quotation Comparison</h3>
                <span className="comparison-subtitle">
                  {comparisonData.rfq_number} - {comparisonData.title}
                </span>
              </div>
              <button className="modal-close" onClick={() => setShowComparison(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="comparison-summary">
                <div className="summary-stat">
                  <span className="stat-label">Total Quotations</span>
                  <span className="stat-value">{comparisonData.quotation_count}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">RFQ Items</span>
                  <span className="stat-value">{comparisonData.item_comparison?.length || 0}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Best Price</span>
                  <span className="stat-value best-price">
                    {comparisonData.quotations?.length > 0 
                      ? `${comparisonData.quotations[0].currency} ${comparisonData.quotations[0].total_amount?.toLocaleString()}`
                      : 'N/A'}
                  </span>
                </div>
              </div>

              {/* Quotation Rankings */}
              {comparisonData.quotations && comparisonData.quotations.length > 0 && (
                <div className="rankings-section">
                  <h4>Vendor Rankings</h4>
                  <div className="rankings-list">
                    {comparisonData.quotations.map((q) => (
                      <div key={q.quotation_id} className={`ranking-item rank-${q.rank}`}>
                        <div className="ranking-rank">
                          {getRankIcon(q.rank)}
                          <span className="rank-number">#{q.rank}</span>
                        </div>
                        <div className="ranking-info">
                          <div className="ranking-vendor">
                            <Building2 size={14} />
                            <span>{q.vendor_name}</span>
                            <span className="vendor-code">{q.vendor_code}</span>
                          </div>
                          <div className="ranking-amount">
                            <DollarSign size={14} />
                            <span className="amount">{q.currency} {q.total_amount?.toLocaleString()}</span>
                          </div>
                        </div>
                        {q.validity_date && (
                          <div className="ranking-validity">
                            <Calendar size={12} />
                            <span>Valid until {new Date(q.validity_date).toLocaleDateString()}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Item-wise Comparison */}
              {comparisonData.item_comparison && comparisonData.item_comparison.length > 0 && (
                <div className="item-comparison-section">
                  <h4>Item-wise Comparison</h4>
                  <div className="comparison-items">
                    {comparisonData.item_comparison.map((item, idx) => (
                      <div key={idx} className="comparison-item">
                        <div className="item-header">
                          <span className="item-name">{item.item_name}</span>
                          <span className="item-meta">
                            {item.quantity} {item.unit}
                          </span>
                        </div>
                        {item.description && (
                          <div className="item-desc">{item.description}</div>
                        )}
                        <div className="item-prices">
                          {item.prices && item.prices.length > 0 ? (
                            item.prices.map((price, pIdx) => (
                              <div 
                                key={pIdx} 
                                className={`price-entry ${pIdx === 0 ? 'best-price' : ''}`}
                              >
                                <span className="price-vendor">{price.vendor_name}</span>
                                <span className="price-amount">
                                  ₹{price.total_price?.toLocaleString()}
                                </span>
                                <span className="price-detail">
                                  {price.quantity} × ₹{price.unit_price?.toLocaleString()}
                                </span>
                              </div>
                            ))
                          ) : (
                            <div className="no-prices">No quotations for this item</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Quotations;