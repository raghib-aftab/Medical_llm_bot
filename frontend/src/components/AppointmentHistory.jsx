import React, { useState, useEffect } from 'react';
import { appointmentsAPI } from '../services/api';
import '../styles/AppointmentHistory.css';

const AppointmentHistory = () => {
  const [appointments, setAppointments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadAppointments();
  }, [statusFilter]);

  const loadAppointments = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await appointmentsAPI.getAppointments(statusFilter || null);
      setAppointments(data);
    } catch (err) {
      setError('Failed to load appointments');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelAppointment = async (appointmentId) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) {
      return;
    }

    try {
      await appointmentsAPI.cancelAppointment(appointmentId);
      loadAppointments();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to cancel appointment');
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'scheduled': return 'status-scheduled';
      case 'completed': return 'status-completed';
      case 'cancelled': return 'status-cancelled';
      default: return '';
    }
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="appointments-loading">
        <div className="loading-spinner"></div>
        <p>Loading appointments...</p>
      </div>
    );
  }

  return (
    <div className="appointments-container">
      <div className="appointments-header">
        <h2>My Appointments</h2>
        <select 
          value={statusFilter} 
          onChange={(e) => setStatusFilter(e.target.value)}
          className="status-filter"
        >
          <option value="">All Status</option>
          <option value="scheduled">Scheduled</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {error && <div className="appointments-error">{error}</div>}

      {appointments.length === 0 ? (
        <div className="no-appointments">
          <div className="no-appointments-icon">📅</div>
          <h3>No Appointments</h3>
          <p>You haven't booked any appointments yet.</p>
        </div>
      ) : (
        <div className="appointments-list">
          {appointments.map((apt) => (
            <div key={apt.id} className="appointment-card">
              <div className="appointment-left">
                <div className="appointment-date-box">
                  <span className="date-day">
                    {new Date(apt.appointment_date).getDate()}
                  </span>
                  <span className="date-month">
                    {new Date(apt.appointment_date).toLocaleDateString('en-US', { month: 'short' })}
                  </span>
                </div>
              </div>
              <div className="appointment-middle">
                <h3>{apt.doctor_name}</h3>
                <p className="appointment-specialization">{apt.specialization}</p>
                {apt.hospital_name && <p className="appointment-hospital">🏥 {apt.hospital_name}</p>}
                <p className="appointment-time">🕐 {apt.appointment_time}</p>
                {apt.reason && <p className="appointment-reason">📝 {apt.reason}</p>}
              </div>
              <div className="appointment-right">
                <span className={`status-badge ${getStatusClass(apt.status)}`}>
                  {apt.status.charAt(0).toUpperCase() + apt.status.slice(1)}
                </span>
                {apt.status === 'scheduled' && (
                  <button 
                    className="cancel-btn"
                    onClick={() => handleCancelAppointment(apt.id)}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AppointmentHistory;
