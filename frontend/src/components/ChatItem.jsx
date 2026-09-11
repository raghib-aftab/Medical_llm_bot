import React from 'react';
import '../styles/ChatItem.css';

const ChatItem = ({ chat, isActive, onClick, onDelete }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    onDelete(chat.id);
  };

  return (
    <div 
      className={`chat-item ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      <div className="chat-item-content">
        <div className="chat-item-title">{chat.title}</div>
        <div className="chat-item-date">{formatDate(chat.updated_at)}</div>
      </div>
      <button 
        className="chat-item-delete"
        onClick={handleDelete}
        title="Delete chat"
      >
        ×
      </button>
    </div>
  );
};

export default ChatItem;
