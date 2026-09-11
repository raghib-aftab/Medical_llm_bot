import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';
import '../styles/MedicalChat.css';

// Simple markdown-like formatter for bold text and line breaks
const formatMessage = (text) => {
  if (!text) return '';
  
  // Split by lines first
  const lines = text.split('\n');
  
  return lines.map((line, lineIndex) => {
    // Process bold text (**text** or __text__)
    const parts = line.split(/(\*\*[^*]+\*\*|__[^_]+__)/g);
    
    const formattedParts = parts.map((part, partIndex) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={partIndex}>{part.slice(2, -2)}</strong>;
      } else if (part.startsWith('__') && part.endsWith('__')) {
        return <strong key={partIndex}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
    
    return (
      <React.Fragment key={lineIndex}>
        {formattedParts}
        {lineIndex < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });
};

const MedicalChat = () => {
  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showChatList, setShowChatList] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadChats();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChats = async () => {
    try {
      const chatList = await chatAPI.getAllChats();
      setChats(chatList);
    } catch (error) {
      console.error('Error loading chats:', error);
    }
  };

  const handleNewChat = async () => {
    try {
      const newChat = await chatAPI.createChat();
      setChats([newChat, ...chats]);
      setActiveChat(newChat);
      setMessages([]);
      setShowChatList(false);
    } catch (error) {
      console.error('Error creating chat:', error);
    }
  };

  const handleSelectChat = async (chatId) => {
    try {
      const chat = await chatAPI.getChat(chatId);
      setActiveChat(chat);
      setMessages(chat.messages || []);
      setShowChatList(false);
    } catch (error) {
      console.error('Error loading chat:', error);
    }
  };

  const handleDeleteChat = async (e, chatId) => {
    e.stopPropagation();
    // if (!window.confirm('Delete this conversation?')) return;
    
    try {
      await chatAPI.deleteChat(chatId);
      setChats(chats.filter(c => c.id !== chatId));
      if (activeChat?.id === chatId) {
        setActiveChat(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    let chatToUse = activeChat;
    
    // Create new chat if needed
    if (!chatToUse) {
      try {
        const newChat = await chatAPI.createChat();
        setChats([newChat, ...chats]);
        setActiveChat(newChat);
        chatToUse = newChat;
      } catch (error) {
        console.error('Error creating chat:', error);
        return;
      }
    }

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(chatToUse.id, inputMessage);
      setMessages(prev => [...prev, response]);
      loadChats(); // Refresh chat list for updated titles
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => prev.slice(0, -1));
      alert('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="medical-chat-container">
      <div className="chat-header-bar">
        <div className="chat-header-left">
          <button 
            className="toggle-chats-btn"
            onClick={() => setShowChatList(!showChatList)}
          >
            {showChatList ? '✕' : '☰'}
          </button>
          <h2>🩺 Medical AI Assistant</h2>
        </div>
        <button className="new-chat-btn" onClick={handleNewChat}>
          + New Consultation
        </button>
      </div>

      <div className="chat-body">
        {/* Chat List Sidebar */}
        <div className={`chat-sidebar ${showChatList ? 'show' : ''}`}>
          <div className="chat-list-header">
            <h3>Conversations</h3>
          </div>
          <div className="chat-list">
            {chats.length === 0 ? (
              <div className="no-chats">
                <p>No conversations yet</p>
                <p>Start a new consultation!</p>
              </div>
            ) : (
              chats.map(chat => (
                <div 
                  key={chat.id}
                  className={`chat-list-item ${activeChat?.id === chat.id ? 'active' : ''}`}
                  onClick={() => handleSelectChat(chat.id)}
                >
                  <div className="chat-list-item-content">
                    <span className="chat-title">{chat.title}</span>
                    <span className="chat-date">
                      {new Date(chat.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                  <button 
                    className="delete-chat-btn"
                    onClick={(e) => handleDeleteChat(e, chat.id)}
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Messages Area */}
        <div className="chat-main">
          {!activeChat && messages.length === 0 ? (
            <div className="welcome-message">
              <div className="welcome-icon">🏥</div>
              <h3>Welcome to Medical AI Assistant</h3>
              <p>Get instant medical advice and health information from our AI doctor.</p>
              <div className="welcome-tips">
                <h4>You can ask about:</h4>
                <ul>
                  <li>🩺 Symptoms and conditions</li>
                  <li>💊 Medications and treatments</li>
                  <li>👨‍⚕️ Find doctors - "Show me cardiologists"</li>
                  <li>🏥 Find hospitals - "Show hospitals near me"</li>
                  <li>📅 Book appointments - "Book appointment"</li>
                  <li>📋 View appointments - "My appointments"</li>
                  <li>🔐 Change password - "Change my password"</li>
                </ul>
              </div>
              <p className="disclaimer">
                ⚠️ This is for informational purposes only. Always consult a real doctor for medical decisions.
              </p>
            </div>
          ) : (
            <div className="messages-container">
              {messages.map((msg, index) => (
                <div 
                  key={index} 
                  className={`message ${msg.role === 'user' ? 'user' : 'assistant'}`}
                >
                  <div className="message-avatar">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{formatMessage(msg.content)}</div>
                    <div className="message-time">{formatTime(msg.timestamp)}</div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message assistant">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Message Input */}
          <form className="message-input-form" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Describe your symptoms or ask a health question..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !inputMessage.trim()}>
              {isLoading ? '...' : '➤'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default MedicalChat;
