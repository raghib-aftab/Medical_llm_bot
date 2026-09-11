import React, { useState } from 'react';
import DoctorList from './DoctorList';
import BookAppointment from './BookAppointment';
import AppointmentHistory from './AppointmentHistory';
import Profile from './Profile';
import MedicalChat from './MedicalChat';
import HospitalList from './HospitalList';
import '../styles/Dashboard.css';

const Dashboard = ({ user, onLogout, onUpdateUser }) => {
  const [activeView, setActiveView] = useState('chat');
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [showBooking, setShowBooking] = useState(false);

  const handleSelectDoctor = (doctor) => {
    setSelectedDoctor(doctor);
    setShowBooking(true);
  };

  const handleBookingSuccess = () => {
    setShowBooking(false);
    setSelectedDoctor(null);
    setActiveView('appointments');
  };

  const handleBackToDoctors = () => {
    setShowBooking(false);
    setSelectedDoctor(null);
  };

  const renderContent = () => {
    if (showBooking && selectedDoctor) {
      return (
        <BookAppointment 
          doctor={selectedDoctor}
          onBack={handleBackToDoctors}
          onSuccess={handleBookingSuccess}
        />
      );
    }

    switch (activeView) {
      case 'chat':
        return <MedicalChat />;
      case 'doctors':
        return <DoctorList onSelectDoctor={handleSelectDoctor} />;
      case 'hospitals':
        return <HospitalList />;
      case 'appointments':
        return <AppointmentHistory />;
      case 'profile':
        return <Profile user={user} onUpdateUser={onUpdateUser} />;
      default:
        return <MedicalChat />;
    }
  };

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <span className="nav-logo">🏥</span>
          <h1>MedCare</h1>
        </div>
        <div className="nav-links">
          <button 
            className={`nav-link ${activeView === 'chat' ? 'active' : ''}`}
            onClick={() => {
              setActiveView('chat');
              setShowBooking(false);
            }}
          >
            <span className="nav-icon">💬</span>
            <span className="nav-text">AI Doctor</span>
          </button>
          <button 
            className={`nav-link ${activeView === 'doctors' && !showBooking ? 'active' : ''}`}
            onClick={() => {
              setActiveView('doctors');
              setShowBooking(false);
            }}
          >
            <span className="nav-icon">👨‍⚕️</span>
            <span className="nav-text">Doctors</span>
          </button>
          <button 
            className={`nav-link ${activeView === 'hospitals' ? 'active' : ''}`}
            onClick={() => {
              setActiveView('hospitals');
              setShowBooking(false);
            }}
          >
            <span className="nav-icon">🏥</span>
            <span className="nav-text">Hospitals</span>
          </button>
          <button 
            className={`nav-link ${activeView === 'appointments' ? 'active' : ''}`}
            onClick={() => {
              setActiveView('appointments');
              setShowBooking(false);
            }}
          >
            <span className="nav-icon">📅</span>
            <span className="nav-text">Appointments</span>
          </button>
          <button 
            className={`nav-link ${activeView === 'profile' ? 'active' : ''}`}
            onClick={() => {
              setActiveView('profile');
              setShowBooking(false);
            }}
          >
            <span className="nav-icon">👤</span>
            <span className="nav-text">Profile</span>
          </button>
        </div>
        <div className="nav-user">
          <div className="user-info">
            <div className="user-avatar-small">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="user-name">{user?.name || 'User'}</span>
          </div>
          <button className="logout-btn" onClick={onLogout}>
            Logout
          </button>
        </div>
      </nav>

      <main className="dashboard-content">
        {renderContent()}
      </main>
    </div>
  );
};

export default Dashboard;
