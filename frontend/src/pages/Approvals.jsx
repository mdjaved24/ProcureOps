import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  Loader2,
  Clock,
  AlertCircle,
  FileText,
  User,
  Calendar,
  DollarSign,
  RefreshCw,
  MessageSquare,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import './Approvals.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function Approvals({ user }) {
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [processing, setProcessing] = useState(null);
  const [expandedApproval, setExpandedApproval] = useState(null);
  const [comments, setComments] = useState({});

  useEffect(() => {
    fetchPendingApprovals();
  }, []);

  const fetchPendingApprovals = async () => {
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/approvals/my-pending`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          setError('You don\'t have permission to view approvals.');
          setApprovals([]);
          setLoading(false);
          return;
        }
        throw new Error('Failed to load approvals');
      }

      const data = await response.json();
      setApprovals(Array.isArray(data) ? data : []);
    } catch (err) {
      setError('Unable to load approvals. Please try again.');
      setApprovals([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (approvalStepId, decision) => {
    setProcessing(approvalStepId);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const comment = comments[approvalStepId] || '';

      // Map frontend decision to backend enum (uppercase)
      const decisionMap = {
        'approve': 'APPROVE',
        'reject': 'REJECT',
        'request_changes': 'REQUEST_CHANGES'
      };
      
      const formattedDecision = decisionMap[decision] || decision.toUpperCase();

      const response = await fetch(`${API_BASE_URL}/approvals/steps/${approvalStepId}/decision`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          decision: formattedDecision,
          comments: comment || null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You don\'t have permission to perform this action.');
        }
        if (response.status === 404) {
          throw new Error('Approval step not found.');
        }
        if (response.status === 409) {
          throw new Error(data.detail || 'This approval has already been processed.');
        }
        if (response.status === 422) {
          throw new Error('Invalid decision. Must be APPROVE, REJECT, or REQUEST_CHANGES.');
        }
        throw new Error(data.detail || data.message || 'Approval action failed');
      }

      // Remove the approval from the list
      setApprovals(prev => prev.filter(a => a.approval_step_id !== approvalStepId));
      
      // Clear comments for this approval
      setComments(prev => {
        const newComments = { ...prev };
        delete newComments[approvalStepId];
        return newComments;
      });

    } catch (err) {
      setError(err.message || 'Unable to process approval. Please try again.');
    } finally {
      setProcessing(null);
    }
  };

  const toggleExpand = (approvalStepId) => {
    setExpandedApproval(expandedApproval === approvalStepId ? null : approvalStepId);
  };

  const handleCommentChange = (approvalStepId, value) => {
    setComments(prev => ({
      ...prev,
      [approvalStepId]: value
    }));
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'PENDING': 'status-pending',
      'APPROVED': 'status-approved',
      'REJECTED': 'status-rejected',
      'CHANGES_REQUESTED': 'status-changes-requested',
      'CANCELLED': 'status-cancelled',
      'DRAFT': 'status-draft',
      'SUBMITTED': 'status-submitted',
      'UNDER_REVIEW': 'status-under-review',
      'APPROVAL_PENDING': 'status-approval-pending',
      'COMPLETED': 'status-completed',
    };
    return statusMap[status] || 'status-default';
  };

  const formatCurrency = (amount, currency = 'INR') => {
    if (amount === undefined || amount === null) return '—';
    return `${currency} ${amount.toLocaleString()}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="approvals-loading">
        <Loader2 size={32} className="spinner" />
        <span>Loading approvals...</span>
      </div>
    );
  }

  const userRole = user?.role?.toUpperCase() || user?.role_name?.toUpperCase() || '';
  const hasApprovalPermission = ['ADMIN', 'PROCUREMENT_MANAGER', 'PROCUREMENT_HEAD', 'FINANCE_OFFICER', 'CFO'].includes(userRole);

  if (!hasApprovalPermission) {
    return (
      <div className="approvals-page">
        <div className="approvals-header">
          <h1 className="approvals-title">Approvals</h1>
          <p className="approvals-subtitle">Pending human approvals</p>
        </div>
        <div className="approvals-readonly">
          <AlertCircle size={48} className="readonly-icon" />
          <p className="readonly-title">Approval Permissions Required</p>
          <p className="readonly-description">
            Your role ({userRole || 'Employee'}) does not have approval permissions.
          </p>
          <p className="readonly-hint">
            Approvals are managed by Procurement Managers, Finance, and other authorized roles.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="approvals-page">
      <div className="approvals-header">
        <div>
          <h1 className="approvals-title">Approvals</h1>
          <p className="approvals-subtitle">Pending human approvals</p>
          {approvals.length > 0 && (
            <span className="approvals-count">{approvals.length} pending approval{approvals.length > 1 ? 's' : ''}</span>
          )}
        </div>
        <button className="refresh-btn" onClick={fetchPendingApprovals}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && <div className="approvals-error">{error}</div>}

      {approvals.length === 0 ? (
        <div className="approvals-empty">
          <CheckCircle size={48} className="empty-icon" />
          <p className="empty-title">No pending approvals</p>
          <p className="empty-subtitle">All approval requests have been reviewed.</p>
        </div>
      ) : (
        <div className="approvals-list">
          {approvals.map((approval) => (
            <div 
              key={approval.approval_step_id} 
              className={`approval-card ${expandedApproval === approval.approval_step_id ? 'expanded' : ''}`}
            >
              <div className="approval-card-header" onClick={() => toggleExpand(approval.approval_step_id)}>
                <div className="approval-card-left">
                  <div className="approval-card-icon">
                    <FileText size={20} />
                  </div>
                  <div className="approval-card-info">
                    <div className="approval-card-title">
                      <span className="request-number">{approval.request_number}</span>
                      <span className="request-title">{approval.title}</span>
                    </div>
                    <div className="approval-card-meta">
                      <span className="meta-item">
                        <User size={14} />
                        Role: {approval.required_role}
                      </span>
                      <span className="meta-item">
                        <DollarSign size={14} />
                        {formatCurrency(approval.estimated_amount, approval.currency)}
                      </span>
                      <span className="meta-item">
                        <Calendar size={14} />
                        {formatDate(approval.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="approval-card-right">
                  <StatusBadge status={approval.approval_status || approval.purchase_request_status} />
                  <span className="expand-icon">
                    {expandedApproval === approval.approval_step_id ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </span>
                </div>
              </div>

              {expandedApproval === approval.approval_step_id && (
                <div className="approval-card-details">
                  <div className="details-grid">
                    <div className="detail-group">
                      <h4>Request Details</h4>
                      <div className="detail-row">
                        <span className="detail-label">Request Number</span>
                        <span className="detail-value">{approval.request_number}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Title</span>
                        <span className="detail-value">{approval.title}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Amount</span>
                        <span className="detail-value highlight">
                          {formatCurrency(approval.estimated_amount, approval.currency)}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Status</span>
                        <StatusBadge status={approval.purchase_request_status} />
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Created</span>
                        <span className="detail-value">{formatDate(approval.created_at)}</span>
                      </div>
                    </div>

                    <div className="detail-group">
                      <h4>Approval Details</h4>
                      <div className="detail-row">
                        <span className="detail-label">Approval ID</span>
                        <span className="detail-value">#{approval.approval_id}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Step ID</span>
                        <span className="detail-value">#{approval.approval_step_id}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Sequence</span>
                        <span className="detail-value">Step {approval.sequence}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Required Role</span>
                        <span className="detail-value role-badge">{approval.required_role}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Step Status</span>
                        <span className={`step-status ${approval.step_status?.toLowerCase()}`}>
                          {approval.step_status || 'PENDING'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="approval-comments">
                    <label htmlFor={`comment-${approval.approval_step_id}`}>
                      <MessageSquare size={16} />
                      Comments (optional)
                    </label>
                    <textarea
                      id={`comment-${approval.approval_step_id}`}
                      value={comments[approval.approval_step_id] || ''}
                      onChange={(e) => handleCommentChange(approval.approval_step_id, e.target.value)}
                      placeholder="Add comments for this approval decision..."
                      rows={3}
                      disabled={processing === approval.approval_step_id}
                      className="comment-input"
                    />
                  </div>

                  <div className="approval-actions">
                    <button
                      className="approval-btn reject"
                      onClick={() => handleDecision(approval.approval_step_id, 'reject')}
                      disabled={processing === approval.approval_step_id}
                    >
                      {processing === approval.approval_step_id ? (
                        <Loader2 size={16} className="spinner" />
                      ) : (
                        <XCircle size={16} />
                      )}
                      Reject
                    </button>
                    <button
                      className="approval-btn approve"
                      onClick={() => handleDecision(approval.approval_step_id, 'approve')}
                      disabled={processing === approval.approval_step_id}
                    >
                      {processing === approval.approval_step_id ? (
                        <Loader2 size={16} className="spinner" />
                      ) : (
                        <CheckCircle size={16} />
                      )}
                      Approve
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Approvals;