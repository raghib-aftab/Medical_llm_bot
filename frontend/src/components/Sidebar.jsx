import React from 'react';
import ChatItem from './ChatItem';
import '../styles/Sidebar.css';

const Sidebar = ({ chats, activeChat, onChatSelect, onNewChat, onDeleteChat, user, onLogout }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="user-info">
          <div className="user-avatar">
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="user-details">
            <span className="user-name">{user?.name || 'User'}</span>
            <span className="user-email">{user?.email || ''}</span>
          </div>
        </div>
        <button className="logout-btn" onClick={onLogout} title="Logout">
          ⎋
        </button>
      </div>
      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>
      <div className="chat-list">
        {chats.length === 0 ? (
          <div className="no-chats">No chats yet. Start a new conversation!</div>
        ) : (
          chats.map((chat) => (
            <ChatItem
              key={chat.id}
              chat={chat}
              isActive={activeChat?.id === chat.id}
              onClick={() => onChatSelect(chat.id)}
              onDelete={onDeleteChat}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;
