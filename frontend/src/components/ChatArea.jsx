import React from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import '../styles/ChatArea.css';

const ChatArea = ({ activeChat, messages, onSendMessage, isLoading }) => {
  if (!activeChat) {
    return (
      <div className="chat-area">
        <div className="no-chat-selected">
          <h2>Medical LLM Assistant</h2>
          <p>Select a chat from the sidebar or create a new one to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-area">
      <div className="chat-header">
        <h3>{activeChat.title}</h3>
      </div>
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput onSendMessage={onSendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatArea;
