import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2, CheckCircle, XCircle, AlertCircle, FileText } from 'lucide-react';
import './AIAssistant.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function AIAssistant({ user }) {
  const [messages, setMessages] = useState(() => {
    const saved = sessionStorage.getItem('procureops_messages');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return [];
      }
    }
    return [];
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conversationId, setConversationId] = useState(() => {
    return sessionStorage.getItem('procureops_conversation_id') || null;
  });
  const [processingApproval, setProcessingApproval] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    sessionStorage.setItem('procureops_messages', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    if (conversationId) {
      sessionStorage.setItem('procureops_conversation_id', conversationId);
    }
  }, [conversationId]);

  useEffect(() => {
    if (!conversationId) {
      const newConvId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setConversationId(newConvId);
      sessionStorage.setItem('procureops_conversation_id', newConvId);
    }
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 100);
  };

  // ============================================================
  // TABLE RENDERING FUNCTIONS
  // ============================================================

  const parseMarkdownTable = (content) => {
    if (!content) return null;

    const lines = content.split('\n');
    let tables = [];
    let inTable = false;
    let headerRow = null;
    let dataRows = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
        const cells = line.split('|').map(c => c.trim()).filter(c => c !== '');
        
        if (cells.length === 0) continue;
        
        const isSeparator = cells.every(c => c.includes('---'));
        
        if (isSeparator) {
          inTable = true;
          continue;
        }
        
        if (!headerRow) {
          headerRow = cells;
        } else if (inTable) {
          dataRows.push(cells);
        }
      } else {
        if (inTable && headerRow && dataRows.length > 0) {
          tables.push({
            headers: headerRow,
            rows: dataRows,
            isComparison: headerRow.some(h => 
              h.toLowerCase().includes('rank') || 
              h.toLowerCase().includes('vendor') ||
              h.toLowerCase().includes('quotation') ||
              h.toLowerCase().includes('total')
            )
          });
        }
        headerRow = null;
        dataRows = [];
        inTable = false;
      }
    }

    if (inTable && headerRow && dataRows.length > 0) {
      tables.push({
        headers: headerRow,
        rows: dataRows,
        isComparison: headerRow.some(h => 
          h.toLowerCase().includes('rank') || 
          h.toLowerCase().includes('vendor') ||
          h.toLowerCase().includes('quotation') ||
          h.toLowerCase().includes('total')
        )
      });
    }

    return tables;
  };

  const renderComparisonTable = (headers, rows) => {
    return `
      <div class="ai-table-wrapper comparison-table">
        <table class="ai-table">
          <thead>
            <tr>
              ${headers.map(h => `<th>${h}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${rows.map((row, index) => {
              const isBest = index === 0;
              return `
                <tr class="${isBest ? 'best-row' : ''}">
                  ${row.map(cell => {
                    const isPrice = cell.includes('₹') || cell.includes('INR');
                    return `<td class="${isPrice ? 'price-cell' : ''}">${cell}</td>`;
                  }).join('')}
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  };

  const renderRegularTable = (headers, rows) => {
    return `
      <div class="ai-table-wrapper">
        <table class="ai-table">
          <thead>
            <tr>
              ${headers.map(h => `<th>${h}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${rows.map(row => `
              <tr>
                ${row.map(cell => `<td>${cell}</td>`).join('')}
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  };

  const formatAIResponse = (content) => {
    if (!content) return '';

    const tables = parseMarkdownTable(content);
    
    if (!tables || tables.length === 0) {
      return content.split('\n').map(line => {
        if (line.trim() === '') return '<br>';
        let formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        return `<div>${formatted}</div>`;
      }).join('');
    }

    let result = '';
    let remainingContent = content;
    
    for (const table of tables) {
      const tableStart = remainingContent.indexOf('|');
      if (tableStart === -1) break;
      
      const textBefore = remainingContent.substring(0, tableStart);
      if (textBefore.trim()) {
        result += textBefore.split('\n').map(line => {
          if (line.trim() === '') return '<br>';
          let formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
          return `<div>${formatted}</div>`;
        }).join('');
      }
      
      if (table.isComparison) {
        result += renderComparisonTable(table.headers, table.rows);
      } else {
        result += renderRegularTable(table.headers, table.rows);
      }
      
      const tableEnd = remainingContent.indexOf('\n', tableStart + 1);
      if (tableEnd !== -1) {
        remainingContent = remainingContent.substring(tableEnd + 1);
      } else {
        remainingContent = '';
      }
    }
    
    if (remainingContent.trim()) {
      result += remainingContent.split('\n').map(line => {
        if (line.trim() === '') return '<br>';
        let formatted = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        return `<div>${formatted}</div>`;
      }).join('');
    }
    
    return result;
  };

  // ============================================================
  // COMPARISON DATA RENDERER
  // ============================================================

  const renderComparisonData = (liveData) => {
    if (!liveData) return null;
    
    // Check if it's comparison data
    const comparisonData = liveData.comparison || liveData;
    if (!comparisonData.quotations || comparisonData.quotations.length === 0) {
      return null;
    }
    
    const { rfq_number, title, quotations, item_comparison } = comparisonData;
    
    let html = `<div class="comparison-container">`;
    
    // Header
    html += `<div class="comparison-header">
      <h3>${rfq_number || 'RFQ Comparison'}${title ? ` - ${title}` : ''}</h3>
      <span class="quotation-count">${quotations.length} quotations</span>
    </div>`;
    
    // Quotation Summary Table
    html += `<div class="ai-table-wrapper comparison-table">
      <table class="ai-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Vendor</th>
            <th>Total Amount</th>
            <th>Validity Date</th>
          </tr>
        </thead>
        <tbody>`;
    
    quotations.forEach((q) => {
      const isBest = q.rank === 1;
      html += `<tr class="${isBest ? 'best-row' : ''}">
        <td>#${q.rank}</td>
        <td>${q.vendor_name || 'Unknown'}${q.vendor_code ? ` (${q.vendor_code})` : ''}</td>
        <td class="price-cell">${q.currency || 'INR'} ${(q.total_amount || 0).toLocaleString()}</td>
        <td>${q.validity_date ? new Date(q.validity_date).toLocaleDateString() : '—'}</td>
      </tr>`;
    });
    
    html += `</tbody></table></div>`;
    
    // Item-wise Comparison
    if (item_comparison && item_comparison.length > 0) {
      html += `<div class="item-comparison-section">
        <h4>Item-wise Price Comparison</h4>`;
      
      item_comparison.forEach((item) => {
        html += `<div class="item-comparison-group">
          <div class="item-header">
            <strong>${item.item_name || 'Unknown Item'}</strong>
            ${item.description ? `<span class="item-desc">${item.description}</span>` : ''}
            <span class="item-meta">${item.quantity || 0} ${item.unit || ''}</span>
          </div>
          <div class="ai-table-wrapper">
            <table class="ai-table item-table">
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>Unit Price</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>`;
        
        // Sort prices by total (lowest first)
        const sortedPrices = [...(item.prices || [])].sort((a, b) => (a.total_price || 0) - (b.total_price || 0));
        
        sortedPrices.forEach((price, idx) => {
          const isBest = idx === 0;
          const currency = quotations[0]?.currency || 'INR';
          html += `<tr class="${isBest ? 'best-row' : ''}">
            <td>${price.vendor_name || 'Unknown'}</td>
            <td>${currency} ${(price.unit_price || 0).toLocaleString()}</td>
            <td class="price-cell">${currency} ${(price.total_price || 0).toLocaleString()}</td>
          </tr>`;
        });
        
        html += `</tbody></table></div></div>`;
      });
      
      html += `</div>`;
    }
    
    // Key observation
    if (quotations.length > 0) {
      const best = quotations.find(q => q.rank === 1);
      if (best) {
        html += `<div class="key-observation">
          💡 <strong>Key observation:</strong> ${best.vendor_name || 'Unknown vendor'} offers the lowest total amount at ${best.currency || 'INR'} ${(best.total_amount || 0).toLocaleString()} and is ranked 1st.
          ${quotations.length > 1 ? ` There are ${quotations.length} quotations available for comparison.` : ''}
        </div>`;
      }
    }
    
    html += `</div>`;
    
    return html;
  };

  // ============================================================
  // CHAT FUNCTIONS
  // ============================================================

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setError('');
    setLoading(true);

    const userMsg = { role: 'user', content: userMessage, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);

    try {
      const token = localStorage.getItem('access_token');
      
      let convId = conversationId;
      if (!convId) {
        convId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        setConversationId(convId);
        sessionStorage.setItem('procureops_conversation_id', convId);
      }

      const response = await fetch(`${API_BASE_URL}/AI/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_query: userMessage,
          conversation_id: convId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'AI request failed');
      }

      if (data.status === 'awaiting_approval') {
        const aiMsg = {
          role: 'assistant',
          content: data.hitl_request?.message || 'Human approval required.',
          rawContent: data.hitl_request?.message || 'Human approval required.',
          timestamp: new Date(),
          needs_approval: true,
          approval_data: {
            conversation_id: data.conversation_id || convId,
            hitl_request: data.hitl_request,
            action: data.hitl_request?.action || 'Approve',
            entity_type: data.hitl_request?.entity_type || 'Quotation',
            entity_id: data.hitl_request?.entity_id,
            details: data.hitl_request?.details || {},
          },
          status: 'awaiting_approval',
        };
        setMessages(prev => [...prev, aiMsg]);
      } else if (data.status === 'completed') {
        const formattedContent = formatAIResponse(data.response || 'I processed your request.');
        
        const aiMsg = {
          role: 'assistant',
          content: formattedContent,
          rawContent: data.response || 'I processed your request.',
          timestamp: new Date(),
          sources: data.sources || [],
          hitl_result: data.hitl_result,
          liveData: data.live_data, // Store live data for comparison rendering
          status: 'completed',
        };
        setMessages(prev => [...prev, aiMsg]);
      } else {
        throw new Error('Unexpected response status');
      }

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
        sessionStorage.setItem('procureops_conversation_id', data.conversation_id);
      }
    } catch (err) {
      setError(err.message || 'Unable to process your request. Please try again.');
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleApproval = async (messageIndex, decision, approvalData) => {
    setProcessingApproval(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`${API_BASE_URL}/AI/decision`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          conversation_id: approvalData.conversation_id,
          decision: decision,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('You don\'t have permission to perform this action.');
        }
        throw new Error(data.detail || data.message || 'Approval action failed');
      }

      if (data.status === 'awaiting_approval') {
        setMessages(prev => {
          const updated = [...prev];
          updated[messageIndex] = {
            ...updated[messageIndex],
            needs_approval: true,
            approval_data: {
              ...approvalData,
              hitl_request: data.hitl_request,
            },
            content: data.hitl_request?.message || 'Additional approval required.',
          };
          return updated;
        });
      } else if (data.status === 'completed') {
        const formattedContent = formatAIResponse(data.response || 'Approval completed.');
        
        setMessages(prev => {
          const updated = [...prev];
          updated[messageIndex] = {
            ...updated[messageIndex],
            needs_approval: false,
            approval_result: {
              action: decision,
              status: 'completed',
              message: data.hitl_result || `${decision} action completed successfully.`,
            },
            content: formattedContent,
            rawContent: data.response || updated[messageIndex].content,
            hitl_result: data.hitl_result,
            status: 'completed',
          };
          return updated;
        });
      }

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
        sessionStorage.setItem('procureops_conversation_id', data.conversation_id);
      }
    } catch (err) {
      setError(err.message || 'Unable to process approval. Please try again.');
    } finally {
      setProcessingApproval(false);
    }
  };

  // ============================================================
  // RENDER FUNCTIONS
  // ============================================================

  const renderApprovalCard = (message, index) => {
    if (!message.needs_approval || !message.approval_data) return null;

    const { approval_data } = message;
    const hitlRequest = approval_data.hitl_request || {};
    const details = approval_data.details || {};

    return (
      <div className="approval-card">
        <div className="approval-header">
          <AlertCircle size={20} />
          <span className="approval-title">Human approval required</span>
        </div>
        <div className="approval-body">
          <div className="approval-row">
            <span className="approval-label">Action</span>
            <span className="approval-value">{hitlRequest.action || approval_data.action || 'Approve'}</span>
          </div>
          <div className="approval-row">
            <span className="approval-label">Entity</span>
            <span className="approval-value">{hitlRequest.entity_type || approval_data.entity_type || 'Quotation'}</span>
          </div>
          {hitlRequest.entity_id && (
            <div className="approval-row">
              <span className="approval-label">ID</span>
              <span className="approval-value">{hitlRequest.entity_id}</span>
            </div>
          )}
          {hitlRequest.message && (
            <div className="approval-row full-width">
              <span className="approval-label">Message</span>
              <span className="approval-value">{hitlRequest.message}</span>
            </div>
          )}
          
          {Object.entries(details).map(([key, value]) => {
            if (value && typeof value !== 'object') {
              return (
                <div key={key} className="approval-row">
                  <span className="approval-label">{key.replace(/_/g, ' ').toUpperCase()}</span>
                  <span className="approval-value">{String(value)}</span>
                </div>
              );
            }
            return null;
          })}
          
          {hitlRequest.reason && (
            <div className="approval-description">
              {hitlRequest.reason}
            </div>
          )}
        </div>
        <div className="approval-actions">
          <button
            className="approval-btn reject"
            onClick={() => handleApproval(index, 'reject', approval_data)}
            disabled={processingApproval}
          >
            {processingApproval ? 'Processing...' : 'Reject'}
          </button>
          <button
            className="approval-btn approve"
            onClick={() => handleApproval(index, 'approve', approval_data)}
            disabled={processingApproval}
          >
            {processingApproval ? 'Processing...' : 'Approve'}
          </button>
        </div>
      </div>
    );
  };

  const renderSources = (sources) => {
    if (!sources || sources.length === 0) return null;
    
    const sourcesArray = Array.isArray(sources) ? sources : [sources];
    
    return (
      <div className="sources-section">
        <div className="sources-title">Sources</div>
        <div className="sources-list">
          {sourcesArray.map((source, idx) => {
            if (typeof source === 'string') {
              return (
                <div key={idx} className="source-item">
                  <FileText size={12} />
                  <span>{source}</span>
                </div>
              );
            }
            
            const sourceName = source?.document_name || 
                              source?.source || 
                              source?.name || 
                              'Source';
            
            return (
              <div key={idx} className="source-item">
                <FileText size={12} />
                <span>{sourceName}</span>
                {source?.operation && (
                  <span className="source-operation">({source.operation})</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderHitlResult = (hitlResult) => {
    if (!hitlResult) return null;
    
    const resultStr = typeof hitlResult === 'string' ? hitlResult : String(hitlResult);
    const isSuccess = resultStr.toLowerCase().includes('success') || 
                      resultStr.toLowerCase().includes('completed') ||
                      resultStr.toLowerCase().includes('approved');
    
    return (
      <div className={`hitl-result ${isSuccess ? 'success' : 'info'}`}>
        {isSuccess ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
        <span>{resultStr}</span>
      </div>
    );
  };

  const renderMessageContent = (message) => {
    const content = message.content;
    const liveData = message.liveData;
    
    if (!content) return null;
    
    // Check if we have comparison data to render
    if (liveData && liveData.comparison && liveData.comparison.quotations && liveData.comparison.quotations.length > 0) {
      const comparisonHtml = renderComparisonData(liveData);
      if (comparisonHtml) {
        return <div className="formatted-content" dangerouslySetInnerHTML={{ __html: comparisonHtml }} />;
      }
    }
    
    // Check if content contains HTML
    if (content.includes('<table') || content.includes('<div>') || content.includes('<br>')) {
      return <div className="formatted-content" dangerouslySetInnerHTML={{ __html: content }} />;
    }
    
    // Plain text with formatting
    return content.split('\n').map((line, i) => {
      if (line.trim() === '') return <br key={i} />;
      const boldRegex = /\*\*(.*?)\*\*/g;
      const parts = line.split(boldRegex);
      if (parts.length > 1) {
        return (
          <div key={i}>
            {parts.map((part, idx) => {
              if (idx % 2 === 1) {
                return <strong key={idx}>{part}</strong>;
              }
              return part;
            })}
          </div>
        );
      }
      return <div key={i}>{line}</div>;
    });
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const startNewConversation = () => {
    const newConvId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setConversationId(newConvId);
    sessionStorage.setItem('procureops_conversation_id', newConvId);
    setMessages([]);
    sessionStorage.removeItem('procureops_messages');
    setError('');
    inputRef.current?.focus();
  };

  return (
    <div className="assistant">
      <div className="assistant-header">
        <div>
          <h1 className="assistant-title">ProcureOps AI Assistant</h1>
          <p className="assistant-subtitle">Procurement intelligence and operations</p>
          {conversationId && (
            <span className="assistant-conversation-id">
              Conversation: {conversationId.slice(0, 12)}...
            </span>
          )}
        </div>
        <button className="new-conversation-btn" onClick={startNewConversation}>
          New Conversation
        </button>
      </div>

      {error && <div className="assistant-error">{error}</div>}

      <div className="assistant-chat">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <Bot size={48} className="empty-icon" />
              <p className="empty-title">Ready to assist with procurement</p>
              <p className="empty-subtitle">
                Ask about RFQs, quotations, vendors, approvals, or any procurement operation.
              </p>
              <div className="example-prompts">
                <button 
                  className="example-prompt"
                  onClick={() => setInput('Show me recent RFQs')}
                >
                  Show me recent RFQs
                </button>
                <button 
                  className="example-prompt"
                  onClick={() => setInput('What are the pending approvals?')}
                >
                  What are the pending approvals?
                </button>
                <button 
                  className="example-prompt"
                  onClick={() => setInput('Find vendors for office supplies')}
                >
                  Find vendors for office supplies
                </button>
                <button 
                  className="example-prompt"
                  onClick={() => setInput('Compare quotations for RFQ-000001')}
                >
                  Compare quotations for RFQ-000001
                </button>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`message-wrapper ${message.role}`}>
                <div className="message-avatar">
                  {message.role === 'user' 
                    ? user?.full_name?.[0]?.toUpperCase() || 'U' 
                    : <Bot size={18} />
                  }
                </div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-role">
                      {message.role === 'user' ? 'You' : 'ProcureOps AI'}
                    </span>
                    {message.timestamp && (
                      <span className="message-time">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                  <div className="message-text">
                    {message.role === 'assistant' 
                      ? renderMessageContent(message)
                      : message.content
                    }
                  </div>
                  
                  {message.sources && renderSources(message.sources)}
                  {message.hitl_result && renderHitlResult(message.hitl_result)}
                  
                  {message.role === 'assistant' && renderApprovalCard(message, index)}
                  
                  {message.approval_result && (
                    <div className={`approval-result ${message.approval_result.action}`}>
                      {message.approval_result.action === 'approve' ? (
                        <CheckCircle size={16} />
                      ) : (
                        <XCircle size={16} />
                      )}
                      <span>
                        {message.approval_result.action === 'approve' 
                          ? 'Approved' 
                          : 'Rejected'} — {message.approval_result.message}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {loading && (
            <div className="message-wrapper assistant">
              <div className="message-avatar">
                <Bot size={18} />
              </div>
              <div className="message-content">
                <div className="message-header">
                  <span className="message-role">ProcureOps AI</span>
                </div>
                <div className="message-text loading-text">
                  <Loader2 size={18} className="spinner" />
                  <span>Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <form className="input-form" onSubmit={handleSend}>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask ProcureOps anything..."
              disabled={loading || processingApproval}
              className="assistant-input"
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={!input.trim() || loading || processingApproval}
            >
              {loading ? <Loader2 size={18} className="spinner" /> : <Send size={18} />}
            </button>
          </form>
          <div className="input-hint">
            Press Enter to send
          </div>
        </div>
      </div>
    </div>
  );
}

export default AIAssistant;