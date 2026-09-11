import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import Dashboard from './components/Dashboard';
import { authAPI, getUser, setAuthData, isTokenExpired, clearAuthData } from './services/api';
import './styles/App.css';

// Protected Route Component
const ProtectedRoute = ({ children, user }) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  const [user, setUser] = useState(() => {
    // Check if token is expired on initial load
    if (isTokenExpired()) {
      clearAuthData();
      return null;
    }
    return getUser();
  });

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleSignup = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    authAPI.logout();
    setUser(null);
  };

  const handleUpdateUser = (updatedUser) => {
    setUser(updatedUser);
  };

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />
          } 
        />
        <Route 
          path="/signup" 
          element={
            user ? <Navigate to="/" replace /> : <Signup onSignup={handleSignup} />
          } 
        />
        <Route
          path="/"
          element={
            <ProtectedRoute user={user}>
              <Dashboard 
                user={user} 
                onLogout={handleLogout}
                onUpdateUser={handleUpdateUser}
              />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
