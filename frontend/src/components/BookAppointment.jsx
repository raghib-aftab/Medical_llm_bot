import React, { useState, useEffect } from 'react';
import { appointmentsAPI } from '../services/api';
import '../styles/BookAppointment.css';

const BookAppointment = ({ doctor, onBack, onSuccess }) => {
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [reason, setReason] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [availableDates, setAvailableDates] = useState([]);
  const [activeWeek, setActiveWeek] = useState(0);

  useEffect(() => {
    generateAvailableDates();
  }, [doctor]);

  const generateAvailableDates = () => {
    const dates = [];
    const today = new Date();
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    for (let i = 1; i <= 60; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      const dayName = dayNames[date.getDay()];
      
      if (doctor.available_days.includes(dayName)) {
        dates.push({
          dateString: date.toISOString().split('T')[0],
          day: date.getDate(),
          dayShort: dayName.slice(0, 3),
          month: monthNames[date.getMonth()],
          isToday: i === 0
        });
      }
    }
    setAvailableDates(dates);
  };

  // Group dates into weeks (7 dates per group for display)
  const getWeekDates = () => {
    const datesPerPage = 7;
    const start = activeWeek * datesPerPage;
    return availableDates.slice(start, start + datesPerPage);
  };

  const totalWeeks = Math.ceil(availableDates.length / 7);

  const handlePrevWeek = () => {
    if (activeWeek > 0) setActiveWeek(activeWeek - 1);
  };

  const handleNextWeek = () => {
    if (activeWeek < totalWeeks - 1) setActiveWeek(activeWeek + 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedDate || !selectedTime) {
      setError('Please select a date and time');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await appointmentsAPI.createAppointment({
        doctor_id: doctor.id,
        doctor_name: doctor.name,
        specialization: doctor.specialization,
        appointment_date: selectedDate,
        appointment_time: selectedTime,
        reason: reason || null
      });
      
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to book appointment');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="book-appointment-container">
      <button className="back-btn" onClick={onBack}>
        ← Back to Doctors
      </button>

      <div className="appointment-content">
        <div className="doctor-summary">
          <div className="doctor-avatar-large">
            {doctor.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
          </div>
          <div className="doctor-summary-info">
            <h2>{doctor.name}</h2>
            <p className="specialization">{doctor.specialization}</p>
            <p className="experience">{doctor.experience_years} years experience</p>
            <p className="fee">Consultation Fee: <strong>${doctor.consultation_fee}</strong></p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="appointment-form">
          <h3>Select Appointment Date & Time</h3>
          
          {error && <div className="appointment-error">{error}</div>}

          <div className="form-section">
            <label>📅 Select Appointment Date</label>
            <div className="date-picker-container">
              <button 
                type="button" 
                className="date-nav-btn" 
                onClick={handlePrevWeek}
                disabled={activeWeek === 0}
              >
                ‹
              </button>
              <div className="date-cards-wrapper">
                {getWeekDates().map((dateItem) => (
                  <div
                    key={dateItem.dateString}
                    className={`date-card ${selectedDate === dateItem.dateString ? 'selected' : ''}`}
                    onClick={() => setSelectedDate(dateItem.dateString)}
                  >
                    <span className="date-card-day">{dateItem.dayShort}</span>
                    <span className="date-card-number">{dateItem.day}</span>
                    <span className="date-card-month">{dateItem.month}</span>
                  </div>
                ))}
              </div>
              <button 
                type="button" 
                className="date-nav-btn" 
                onClick={handleNextWeek}
                disabled={activeWeek >= totalWeeks - 1}
              >
                ›
              </button>
            </div>
            <div className="date-week-indicator">
              {Array.from({ length: totalWeeks }, (_, i) => (
                <span 
                  key={i} 
                  className={`week-dot ${i === activeWeek ? 'active' : ''}`}
                  onClick={() => setActiveWeek(i)}
                />
              ))}
            </div>
          </div>

          <div className="form-section">
            <label>Available Time Slots</label>
            <div className="time-grid">
              {doctor.available_time_slots.map((time) => (
                <button
                  key={time}
                  type="button"
                  className={`time-option ${selectedTime === time ? 'selected' : ''}`}
                  onClick={() => setSelectedTime(time)}
                >
                  {time}
                </button>
              ))}
            </div>
          </div>

          <div className="form-section">
            <label htmlFor="reason">Reason for Visit (Optional)</label>
            <textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Describe your symptoms or reason for visit..."
              rows={4}
            />
          </div>

          <div className="appointment-summary">
            {selectedDate && selectedTime && (
              <p>
                <strong>Appointment:</strong> {new Date(selectedDate).toLocaleDateString('en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })} at {selectedTime}
              </p>
            )}
          </div>

          <button 
            type="submit" 
            className="confirm-btn"
            disabled={isLoading || !selectedDate || !selectedTime}
          >
            {isLoading ? 'Booking...' : 'Confirm Appointment'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default BookAppointment;
