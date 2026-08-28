import React, { useState } from 'react';

export default function ChatHistoryPanel({ chatHistory, onRefreshHistory, isOpen, onClose }) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredHistory = (chatHistory || []).filter((item) => {
    if (!searchTerm) return true;
    const content = item.content || '';
    const role = item.role || '';
    return content.toLowerCase().includes(searchTerm.toLowerCase()) ||
           role.toLowerCase().includes(searchTerm.toLowerCase());
  });

  if (!isOpen) return null;

  return (
    <div className="chat-history-drawer-backdrop" onClick={onClose}>
      <div className="chat-history-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div className="drawer-title-group">
            <span className="drawer-icon">📜</span>
            <span className="drawer-title">CONVERSATION ARCHIVE</span>
            <span className="count-badge">{chatHistory?.length || 0} Entries</span>
          </div>

          <div className="drawer-actions">
            <button className="btn-icon" onClick={onRefreshHistory} title="Refresh chat history">
              ↻
            </button>
            <button className="btn-icon close-btn" onClick={onClose} title="Close drawer">
              ✕
            </button>
          </div>
        </div>

        <div className="drawer-search-bar">
          <input
            type="text"
            placeholder="Search past conversations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="history-messages-list">
          {filteredHistory.length === 0 ? (
            <div className="empty-history">
              <p>No conversation logs found.</p>
            </div>
          ) : (
            filteredHistory.map((entry, index) => {
              const isUser = entry.role?.toLowerCase() === 'user';
              return (
                <div key={index} className={`history-bubble-wrap ${isUser ? 'user-entry' : 'assistant-entry'}`}>
                  <div className="bubble-header">
                    <span className="role-tag">{isUser ? 'YOU' : 'NOVA'}</span>
                  </div>
                  <div className="bubble-body">
                    {entry.content}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
