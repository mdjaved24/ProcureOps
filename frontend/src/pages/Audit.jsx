import React, { useState, useEffect } from 'react';
import { 
  Search, 
  RefreshCw,
  Loader2,
  Calendar,
  Filter,
  ChevronLeft,
  ChevronRight,
  User,
  FileText,
  Building2,
  CheckCircle,
  XCircle,
  Send,
  Edit2,
  Plus,
  Eye,
  Clock,
  AlertCircle
} from 'lucide-react';
import './Audit.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function Audit({ user }) {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [offset, setOffset] = useState(0);
  const [limit] = useState(50);
  
  // Filter states
  const [filters, setFilters] = useState({
    resource_type: '',
    resource_id: '',
    actor_id: '',
    action: '',
    start_date: '',
    end_date: '',
  });
  
  const [showFilters, setShowFilters] = useState(false);
  const [expandedLog, setExpandedLog] = useState(null);

  useEffect(() => {
    fetchAuditLogs();
  }, [offset, limit]);

  const fetchAuditLogs = async () => {
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      
      // Build query parameters
      const params = new URLSearchParams();
      params.append('limit', String(limit));
      params.append('offset', String(offset));
      
      if (filters.resource_type) params.append('resource_type', filters.resource_type);
      if (filters.resource_id) params.append('resource_id', filters.resource_id);
      if (filters.actor_id) params.append('actor_id', filters.actor_id);
      if (filters.action) params.append('action', filters.action);
      if (filters.start_date) params.append('start_date', new Date(filters.start_date).toISOString());
      if (filters.end_date) params.append('end_date', new Date(filters.end_date).toISOString());
      
      const url = `${API_BASE_URL}/audit-logs?${params.toString()}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          setError('You don\'t have permission to view audit logs.');
          setLogs([]);
          setTotal(0);
          setLoading(false);
          return;
        }
        throw new Error('Failed to load audit logs');
      }

      const data = await response.json();
      setLogs(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError('Unable to load audit logs. Please try again.');
      setLogs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
  };

  const applyFilters = () => {
    setOffset(0);
    fetchAuditLogs();
  };

  const clearFilters = () => {
    setFilters({
      resource_type: '',
      resource_id: '',
      actor_id: '',
      action: '',
      start_date: '',
      end_date: '',
    });
    setOffset(0);
    setTimeout(() => fetchAuditLogs(), 100);
  };

  const handlePrevPage = () => {
    if (offset > 0) {
      setOffset(Math.max(0, offset - limit));
    }
  };

  const handleNextPage = () => {
    if (offset + limit < total) {
      setOffset(offset + limit);
    }
  };

  const getActorIcon = (actorType) => {
    if (actorType === 'USER') return <User size={14} />;
    if (actorType === 'AGENT') return <Bot size={14} />;
    if (actorType === 'SYSTEM') return <Settings size={14} />;
    return <User size={14} />;
  };

  const getActionIcon = (action) => {
    const actionLower = action?.toLowerCase() || '';
    if (actionLower.includes('create')) return <Plus size={14} />;
    if (actionLower.includes('update') || actionLower.includes('edit')) return <Edit2 size={14} />;
    if (actionLower.includes('delete') || actionLower.includes('cancel') || actionLower.includes('withdraw')) return <XCircle size={14} />;
    if (actionLower.includes('submit') || actionLower.includes('send') || actionLower.includes('issue')) return <Send size={14} />;
    if (actionLower.includes('approve') || actionLower.includes('accept')) return <CheckCircle size={14} />;
    if (actionLower.includes('reject') || actionLower.includes('close')) return <XCircle size={14} />;
    if (actionLower.includes('view') || actionLower.includes('read') || actionLower.includes('list')) return <Eye size={14} />;
    return <FileText size={14} />;
  };

  const getResourceIcon = (resourceType) => {
    const type = resourceType?.toLowerCase() || '';
    if (type.includes('vendor')) return <Building2 size={14} />;
    if (type.includes('rfq')) return <FileText size={14} />;
    if (type.includes('quotation')) return <FileCheck size={14} />;
    if (type.includes('user')) return <User size={14} />;
    if (type.includes('approval')) return <CheckCircle size={14} />;
    return <FileText size={14} />;
  };

  const getActionColor = (action) => {
    const actionLower = action?.toLowerCase() || '';
    if (actionLower.includes('create')) return 'action-create';
    if (actionLower.includes('update') || actionLower.includes('edit')) return 'action-update';
    if (actionLower.includes('delete') || actionLower.includes('cancel') || actionLower.includes('withdraw')) return 'action-delete';
    if (actionLower.includes('submit') || actionLower.includes('send') || actionLower.includes('issue')) return 'action-submit';
    if (actionLower.includes('approve') || actionLower.includes('accept')) return 'action-approve';
    if (actionLower.includes('reject') || actionLower.includes('close')) return 'action-reject';
    return 'action-default';
  };

  const formatJson = (obj) => {
    if (!obj) return '—';
    try {
      return JSON.stringify(obj, null, 2);
    } catch {
      return String(obj);
    }
  };

  if (loading) {
    return <div className="audit-loading">Loading audit logs...</div>;
  }

  return (
    <div className="audit-page">
      <div className="audit-header">
        <div>
          <h1 className="audit-title">Audit Logs</h1>
          <p className="audit-subtitle">System activity and compliance records</p>
          {total > 0 && (
            <span className="audit-count">{total} records</span>
          )}
        </div>
        <div className="audit-header-actions">
          <button 
            className="filter-toggle-btn"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={16} />
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </button>
          <button className="refresh-btn" onClick={fetchAuditLogs}>
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {error && <div className="audit-error">{error}</div>}

      {/* Filters */}
      {showFilters && (
        <div className="audit-filters">
          <div className="filter-row">
            <div className="filter-group">
              <label>Resource Type</label>
              <input
                type="text"
                value={filters.resource_type}
                onChange={(e) => handleFilterChange('resource_type', e.target.value)}
                placeholder="e.g., VENDOR, RFQ, USER"
                className="filter-input"
              />
            </div>
            <div className="filter-group">
              <label>Resource ID</label>
              <input
                type="text"
                value={filters.resource_id}
                onChange={(e) => handleFilterChange('resource_id', e.target.value)}
                placeholder="Resource ID"
                className="filter-input"
              />
            </div>
            <div className="filter-group">
              <label>Actor ID</label>
              <input
                type="text"
                value={filters.actor_id}
                onChange={(e) => handleFilterChange('actor_id', e.target.value)}
                placeholder="User ID"
                className="filter-input"
              />
            </div>
          </div>
          <div className="filter-row">
            <div className="filter-group">
              <label>Action</label>
              <input
                type="text"
                value={filters.action}
                onChange={(e) => handleFilterChange('action', e.target.value)}
                placeholder="e.g., VENDOR_CREATED"
                className="filter-input"
              />
            </div>
            <div className="filter-group">
              <label>Start Date</label>
              <input
                type="datetime-local"
                value={filters.start_date}
                onChange={(e) => handleFilterChange('start_date', e.target.value)}
                className="filter-input"
              />
            </div>
            <div className="filter-group">
              <label>End Date</label>
              <input
                type="datetime-local"
                value={filters.end_date}
                onChange={(e) => handleFilterChange('end_date', e.target.value)}
                className="filter-input"
              />
            </div>
          </div>
          <div className="filter-actions">
            <button className="filter-apply-btn" onClick={applyFilters}>
              Apply Filters
            </button>
            <button className="filter-clear-btn" onClick={clearFilters}>
              Clear All
            </button>
          </div>
        </div>
      )}

      {logs.length === 0 ? (
        <div className="audit-empty">
          <FileText size={48} className="empty-icon" />
          <p>No audit logs found.</p>
          <p className="empty-hint">Audit logs will appear here as system activities occur.</p>
        </div>
      ) : (
        <div className="audit-table-wrapper">
          <table className="audit-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <React.Fragment key={log.id}>
                  <tr 
                    className={`audit-row ${expandedLog === log.id ? 'expanded' : ''}`}
                    onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                  >
                    <td className="audit-time">
                      <Clock size={14} className="time-icon" />
                      {log.created_at ? new Date(log.created_at).toLocaleString() : '—'}
                    </td>
                    <td className="audit-actor">
                      <span className="actor-badge">
                        {getActorIcon(log.actor_type)}
                        <span className="actor-id">{log.actor_id || 'system'}</span>
                        <span className="actor-type">{log.actor_type || 'USER'}</span>
                      </span>
                    </td>
                    <td>
                      <span className={`action-badge ${getActionColor(log.action)}`}>
                        {getActionIcon(log.action)}
                        {log.action || '—'}
                      </span>
                    </td>
                    <td className="audit-resource">
                      <span className="resource-badge">
                        {getResourceIcon(log.resource_type)}
                        <span className="resource-type">{log.resource_type || '—'}</span>
                        <span className="resource-id">#{log.resource_id}</span>
                      </span>
                    </td>
                    <td className="audit-details">
                      {log.metadata ? (
                        <span className="metadata-preview">
                          {Object.entries(log.metadata)
                            .filter(([_, v]) => v !== null && v !== undefined)
                            .slice(0, 2)
                            .map(([key, value]) => (
                              <span key={key} className="metadata-tag">
                                {key}: {typeof value === 'object' ? JSON.stringify(value).slice(0, 20) : String(value).slice(0, 30)}
                              </span>
                            ))}
                        </span>
                      ) : (
                        <span className="no-metadata">—</span>
                      )}
                      <span className="expand-hint">
                        {expandedLog === log.id ? 'Click to collapse' : 'Click to expand'}
                      </span>
                    </td>
                  </tr>
                  {expandedLog === log.id && (
                    <tr className="expand-row">
                      <td colSpan="5">
                        <div className="expand-content">
                          <div className="expand-section">
                            <h4>Previous State</h4>
                            <pre className="json-view">{formatJson(log.previous_state)}</pre>
                          </div>
                          <div className="expand-section">
                            <h4>New State</h4>
                            <pre className="json-view">{formatJson(log.new_state)}</pre>
                          </div>
                          {log.metadata && (
                            <div className="expand-section">
                              <h4>Metadata</h4>
                              <pre className="json-view">{formatJson(log.metadata)}</pre>
                            </div>
                          )}
                          {log.correlation_id && (
                            <div className="expand-section">
                              <h4>Correlation ID</h4>
                              <code className="correlation-id">{log.correlation_id}</code>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {total > 0 && (
        <div className="audit-pagination">
          <div className="pagination-info">
            Showing {offset + 1} - {Math.min(offset + limit, total)} of {total} records
          </div>
          <div className="pagination-controls">
            <button 
              className="pagination-btn"
              onClick={handlePrevPage}
              disabled={offset === 0}
            >
              <ChevronLeft size={16} />
              Previous
            </button>
            <span className="pagination-page">
              Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit)}
            </span>
            <button 
              className="pagination-btn"
              onClick={handleNextPage}
              disabled={offset + limit >= total}
            >
              Next
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper components/icons
function Bot({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="10" rx="2" />
      <circle cx="9" cy="7" r="2" />
      <circle cx="15" cy="7" r="2" />
      <path d="M9 16h6" />
    </svg>
  );
}

function Settings({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function FileCheck({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <polyline points="9 15 11 17 15 13" />
    </svg>
  );
}

export default Audit;