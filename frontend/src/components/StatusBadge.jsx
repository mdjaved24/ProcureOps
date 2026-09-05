import React from 'react';
import './StatusBadge.css';

function StatusBadge({ status }) {
  const getStatusClass = (status) => {
    if (!status) return 'status-badge-default';
    
    const s = status.toUpperCase();
    
    // Approval statuses
    if (['PENDING', 'APPROVAL_PENDING'].includes(s)) return 'status-badge-pending';
    if (['APPROVED', 'ACCEPTED', 'COMPLETED'].includes(s)) return 'status-badge-approved';
    if (['REJECTED', 'CANCELLED', 'WITHDRAWN', 'BLOCKED'].includes(s)) return 'status-badge-rejected';
    
    // RFQ statuses
    if (['DRAFT'].includes(s)) return 'status-badge-draft';
    if (['ISSUED'].includes(s)) return 'status-badge-issued';
    if (['CLOSED'].includes(s)) return 'status-badge-closed';
    
    // Purchase Request statuses
    if (['SUBMITTED', 'UNDER_REVIEW'].includes(s)) return 'status-badge-submitted';
    if (['CHANGES_REQUESTED'].includes(s)) return 'status-badge-changes-requested';
    
    // Vendor statuses
    if (['ACTIVE'].includes(s)) return 'status-badge-active';
    if (['INACTIVE'].includes(s)) return 'status-badge-inactive';
    
    // Quotation statuses
    if (['SUBMITTED'].includes(s)) return 'status-badge-submitted';
    
    // Default
    return 'status-badge-default';
  };

  return (
    <span className={`status-badge ${getStatusClass(status)}`}>
      {status || 'N/A'}
    </span>
  );
}

export default StatusBadge;