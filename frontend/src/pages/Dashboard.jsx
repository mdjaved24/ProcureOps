import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bot, 
  FileText, 
  FileCheck, 
  Building2, 
  CheckCircle, 
  Clock,
  Package,
  Send,
  TrendingUp,
  Users,
  Briefcase,
  AlertCircle
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import './Dashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function Dashboard({ user }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/dashboard/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          setError('You don\'t have permission to view the dashboard.');
          setLoading(false);
          return;
        }
        throw new Error('Failed to load dashboard data');
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError('Unable to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getStatusColor = (status) => {
    const colors = {
      'DRAFT': 'status-draft',
      'SUBMITTED': 'status-submitted',
      'UNDER_REVIEW': 'status-under-review',
      'APPROVAL_PENDING': 'status-approval-pending',
      'CHANGES_REQUESTED': 'status-changes-requested',
      'APPROVED': 'status-approved',
      'REJECTED': 'status-rejected',
      'CANCELLED': 'status-cancelled',
      'COMPLETED': 'status-completed',
      'ISSUED': 'status-issued',
      'CLOSED': 'status-closed',
      'ACTIVE': 'status-active',
      'INACTIVE': 'status-inactive',
      'BLOCKED': 'status-blocked',
      'SUBMITTED': 'status-submitted',
      'ACCEPTED': 'status-accepted',
      'WITHDRAWN': 'status-withdrawn',
    };
    return colors[status] || 'status-default';
  };

  const getTimeAgo = (timestamp) => {
    if (!timestamp) return '';
    const now = new Date();
    const past = new Date(timestamp);
    const diffMs = now - past;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return past.toLocaleDateString();
  };

  if (loading) {
    return <div className="dashboard-loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="dashboard-error-container">{error}</div>;
  }

  const stats = dashboardData?.stats || {};
  const recentActivity = dashboardData?.recent_activity || [];

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">
            {getGreeting()}, {user?.full_name || user?.email?.split('@')[0] || 'User'}
          </h1>
          <p className="dashboard-subtitle">
            Role: <span className="dashboard-role">{user?.role || 'Employee'}</span>
            {user?.department && (
              <span className="dashboard-department"> • {user.department}</span>
            )}
          </p>
        </div>
        <button className="dashboard-action-btn" onClick={() => navigate('/assistant')}>
          <Bot size={20} />
          Open AI Assistant
        </button>
      </div>

      {/* Stats Cards */}
      <div className="dashboard-stats">
        {/* Procurement Stats */}
        {stats.total_purchase_requests > 0 && (
          <div className="stat-card">
            <div className="stat-icon procurement">
              <Package size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.total_purchase_requests}</div>
              <div className="stat-label">Purchase Requests</div>
            </div>
          </div>
        )}

        {stats.pending_approvals_count > 0 && (
          <div className="stat-card">
            <div className="stat-icon pending">
              <Clock size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.pending_approvals_count}</div>
              <div className="stat-label">Pending Approvals</div>
            </div>
          </div>
        )}

        {/* RFQ Stats */}
        {stats.active_rfqs > 0 && (
          <div className="stat-card">
            <div className="stat-icon rfq">
              <FileText size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.active_rfqs}</div>
              <div className="stat-label">Active RFQs</div>
            </div>
          </div>
        )}

        {stats.issued_rfqs > 0 && (
          <div className="stat-card">
            <div className="stat-icon issued">
              <Send size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.issued_rfqs}</div>
              <div className="stat-label">Issued RFQs</div>
            </div>
          </div>
        )}

        {/* Quotation Stats */}
        {stats.submitted_quotations > 0 && (
          <div className="stat-card">
            <div className="stat-icon quotations">
              <FileCheck size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.submitted_quotations}</div>
              <div className="stat-label">Submitted Quotations</div>
            </div>
          </div>
        )}

        {/* Vendor Stats */}
        {stats.total_vendors > 0 && (
          <div className="stat-card">
            <div className="stat-icon vendors">
              <Building2 size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.total_vendors}</div>
              <div className="stat-label">Total Vendors</div>
            </div>
          </div>
        )}

        {stats.active_vendors > 0 && (
          <div className="stat-card">
            <div className="stat-icon active-vendors">
              <Users size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.active_vendors}</div>
              <div className="stat-label">Active Vendors</div>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="dashboard-quick-actions">
        <h2 className="section-title">Quick Actions</h2>
        <div className="quick-actions-grid">
          <button className="quick-action" onClick={() => navigate('/assistant')}>
            <Bot size={20} />
            <span>AI Assistant</span>
          </button>
          <button className="quick-action" onClick={() => navigate('/procurement')}>
            <Package size={20} />
            <span>New Request</span>
          </button>
          <button className="quick-action" onClick={() => navigate('/rfqs')}>
            <FileText size={20} />
            <span>Create RFQ</span>
          </button>
          <button className="quick-action" onClick={() => navigate('/vendors')}>
            <Building2 size={20} />
            <span>Add Vendor</span>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      {recentActivity.length > 0 && (
        <div className="dashboard-activity">
          <h2 className="section-title">Recent Activity</h2>
          <div className="activity-list">
            {recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon-wrapper">
                  {activity.type === 'purchase_request' && <Package size={16} />}
                  {activity.type === 'rfq' && <FileText size={16} />}
                  {activity.type === 'quotation' && <FileCheck size={16} />}
                </div>
                <div className="activity-content">
                  <div className="activity-main">
                    <span className="activity-description">{activity.description}</span>
                    <span className="activity-time">{getTimeAgo(activity.timestamp)}</span>
                  </div>
                  <div className="activity-meta">
                    {activity.status && (
                      <span className={`status-badge ${getStatusColor(activity.status)}`}>
                        {activity.status}
                      </span>
                    )}
                    <span className="activity-user">by {activity.user}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;