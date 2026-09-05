import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  RefreshCw,
  Eye,
  Send,
  Building2,
  Loader2,
  Calendar,
  DollarSign
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import StatusBadge from '../components/StatusBadge';
import './VendorDashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function VendorDashboard({ vendorData }) {
  const [rfqs, setRfqs] = useState([]);
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    responded: 0,
    totalQuotations: 0,
  });
  const [selectedRFQ, setSelectedRFQ] = useState(null);
  const [showQuotationModal, setShowQuotationModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchVendorData();
  }, []);

  const fetchVendorData = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('vendor_access_token');
      
      if (!token) {
        setError('Please login to view dashboard');
        setLoading(false);
        return;
      }

      // Fetch RFQs
      const rfqResponse = await fetch(`${API_BASE_URL}/vendor/rfqs`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!rfqResponse.ok) {
        if (rfqResponse.status === 401) {
          localStorage.removeItem('vendor_access_token');
          localStorage.removeItem('vendor_data');
          toast.error('Session expired. Please login again.');
          setTimeout(() => {
            window.location.href = '/vendor/login';
          }, 2000);
          return;
        }
        throw new Error('Failed to load RFQs');
      }

      const rfqData = await rfqResponse.json();
      
      // Fetch Quotations
      const quotationResponse = await fetch(`${API_BASE_URL}/vendor/quotations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      let quotationData = [];
      if (quotationResponse.ok) {
        quotationData = await quotationResponse.json();
        setQuotations(Array.isArray(quotationData) ? quotationData : []);
      }

      // Process RFQs
      const vendorRFQs = Array.isArray(rfqData) ? rfqData : [];
      setRfqs(vendorRFQs);
      
      // Calculate stats
      const pending = vendorRFQs.filter(rfq => 
        rfq.status === 'ISSUED' && !rfq.has_submitted_quotation
      ).length;
      
      const responded = vendorRFQs.filter(rfq => 
        rfq.has_submitted_quotation
      ).length;
      
      setStats({
        total: vendorRFQs.length,
        pending: pending,
        responded: responded,
        totalQuotations: quotationData.length,
      });
      
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Unable to load dashboard data. Please try again.');
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
        return <AlertCircle size={16} className="status-icon rejected" />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="vendor-dashboard-loading">
        <Loader2 size={32} className="spinner" />
        <span>Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="vendor-dashboard">
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

      <div className="vendor-dashboard-header">
        <div>
          <h1>Vendor Dashboard</h1>
          <p className="vendor-dashboard-subtitle">
            Welcome, {vendorData?.vendor_name || 'Vendor'}
          </p>
          <span className="vendor-id-badge">Vendor ID: {vendorData?.vendor_id || 'N/A'}</span>
        </div>
        <button className="refresh-btn" onClick={fetchVendorData}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && <div className="vendor-dashboard-error">{error}</div>}

      {/* Stats Cards */}
      <div className="vendor-stats">
        <div className="stat-card">
          <div className="stat-icon total">
            <FileText size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total RFQs</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon pending">
            <Clock size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.pending}</div>
            <div className="stat-label">Pending Quotations</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon responded">
            <CheckCircle size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.responded}</div>
            <div className="stat-label">Submitted Quotations</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon quotations">
            <DollarSign size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalQuotations}</div>
            <div className="stat-label">Total Quotations</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="vendor-quick-actions">
        <h3>Quick Actions</h3>
        <div className="quick-actions-grid">
          <button 
            className="quick-action-btn"
            onClick={() => navigate('/vendor/rfqs')}
          >
            <FileText size={20} />
            <span>View RFQs</span>
          </button>
          <button 
            className="quick-action-btn"
            onClick={() => navigate('/vendor/quotations')}
          >
            <CheckCircle size={20} />
            <span>My Quotations</span>
          </button>
        </div>
      </div>

      {/* Recent RFQs */}
      <div className="vendor-recent-rfqs">
        <h3>Recent RFQs</h3>
        
        {rfqs.length === 0 ? (
          <div className="vendor-rfqs-empty">
            <FileText size={32} className="empty-icon" />
            <p>No RFQs available</p>
            <p className="empty-hint">You haven't been invited to any RFQs yet.</p>
          </div>
        ) : (
          <div className="vendor-rfqs-list">
            {rfqs.slice(0, 3).map((rfq) => (
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
                  </div>
                  {rfq.description && (
                    <div className="rfq-description">{rfq.description}</div>
                  )}
                </div>
                <div className="rfq-card-actions">
                  <button 
                    className="rfq-btn view"
                    onClick={() => navigate('/vendor/rfqs')}
                  >
                    <Eye size={16} />
                    View Details
                  </button>
                  {rfq.status === 'ISSUED' && !rfq.has_submitted_quotation && (
                    <button 
                      className="rfq-btn submit"
                      onClick={() => navigate('/vendor/rfqs')}
                    >
                      <Send size={16} />
                      Submit Quotation
                    </button>
                  )}
                  {rfq.status === 'ISSUED' && rfq.has_submitted_quotation && (
                    <button 
                      className="rfq-btn submitted"
                      disabled
                    >
                      <CheckCircle size={16} />
                      Quotation Submitted
                    </button>
                  )}
                </div>
              </div>
            ))}
            {rfqs.length > 3 && (
              <button 
                className="view-all-btn"
                onClick={() => navigate('/vendor/rfqs')}
              >
                View All RFQs
              </button>
            )}
          </div>
        )}
      </div>

      {/* Recent Quotations */}
      {quotations.length > 0 && (
        <div className="vendor-recent-quotations">
          <h3>Recent Quotations</h3>
          <div className="vendor-quotations-list">
            {quotations.slice(0, 3).map((quotation) => (
              <div key={quotation.id} className="vendor-quotation-card">
                <div className="quotation-card-header">
                  <div className="quotation-card-title">
                    <span className="quotation-number">{quotation.quotation_number}</span>
                    <span className="quotation-status-badge">
                      {getStatusIcon(quotation.status)}
                      <StatusBadge status={quotation.status} />
                    </span>
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
                  </div>
                  {quotation.notes && (
                    <div className="quotation-notes">{quotation.notes}</div>
                  )}
                </div>
                <div className="quotation-card-actions">
                  <button 
                    className="quotation-btn view"
                    onClick={() => navigate('/vendor/quotations')}
                  >
                    <Eye size={16} />
                    View Details
                  </button>
                </div>
              </div>
            ))}
            {quotations.length > 3 && (
              <button 
                className="view-all-btn"
                onClick={() => navigate('/vendor/quotations')}
              >
                View All Quotations
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default VendorDashboard;