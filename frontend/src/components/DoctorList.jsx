import React, { useState, useEffect } from 'react';
import { appointmentsAPI } from '../services/api';
import '../styles/Doctors.css';

const DoctorList = ({ onSelectDoctor }) => {
  const [doctors, setDoctors] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [selectedSpecialization, setSelectedSpecialization] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDoctors();
    loadSpecializations();
  }, []);

  const loadDoctors = async (specialization = null) => {
    setIsLoading(true);
    setError('');
    try {
      const data = await appointmentsAPI.getDoctors(specialization);
      setDoctors(data);
    } catch (err) {
      setError('Failed to load doctors');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSpecializations = async () => {
    try {
      const data = await appointmentsAPI.getSpecializations();
      setSpecializations(data.specializations);
    } catch (err) {
      console.error('Failed to load specializations:', err);
    }
  };

  const handleSpecializationChange = (e) => {
    const spec = e.target.value;
    setSelectedSpecialization(spec);
    loadDoctors(spec || null);
  };

  if (isLoading) {
    return (
      <div className="doctors-loading">
        <div className="loading-spinner"></div>
        <p>Loading doctors...</p>
      </div>
    );
  }

  return (
    <div className="doctors-container">
      <div className="doctors-header">
        <h2>Find a Doctor</h2>
        <p>Choose from our experienced medical professionals</p>
      </div>

      <div className="doctors-filter">
        <select 
          value={selectedSpecialization} 
          onChange={handleSpecializationChange}
          className="specialization-select"
        >
          <option value="">All Specializations</option>
          {specializations.map((spec) => (
            <option key={spec} value={spec}>{spec}</option>
          ))}
        </select>
      </div>

      {error && <div className="doctors-error">{error}</div>}

      <div className="doctors-grid">
        {doctors.map((doctor) => (
          <div key={doctor.id} className="doctor-card">
            <div className="doctor-card-header">
              <div className="doctor-avatar">
                {doctor.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
              </div>
              <div className="doctor-badge">
                <span className="availability-badge">Available</span>
              </div>
            </div>
            <div className="doctor-info">
              <h3>{doctor.name}</h3>
              <p className="doctor-specialization">{doctor.specialization}</p>
              <p className="doctor-hospital">
                <span className="hospital-icon">🏥</span>
                {doctor.hospital}
              </p>
              <div className="doctor-meta">
                <div className="meta-item">
                  <span className="meta-icon">🎓</span>
                  <span>{doctor.experience_years} years</span>
                </div>
                <div className="meta-item">
                  <span className="meta-icon">⭐</span>
                  <span>{doctor.rating}/5</span>
                </div>
                <div className="meta-item">
                  <span className="meta-icon">👥</span>
                  <span>{doctor.patients_count}+</span>
                </div>
              </div>
              <div className="doctor-availability">
                <span className="availability-label">Available:</span>
                <div className="availability-days">
                  {doctor.available_days?.slice(0, 3).map((day, i) => (
                    <span key={i} className="day-badge">{day.slice(0, 3)}</span>
                  ))}
                  {doctor.available_days?.length > 3 && (
                    <span className="day-badge more">+{doctor.available_days.length - 3}</span>
                  )}
                </div>
              </div>
              <div className="doctor-footer">
                <div className="doctor-fee">
                  <span className="fee-label">Consultation</span>
                  <span className="fee-amount">₹{doctor.consultation_fee}</span>
                </div>
                <button 
                  className="book-btn"
                  onClick={() => onSelectDoctor(doctor)}
                >
                  Book Now
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {doctors.length === 0 && !error && (
        <div className="no-doctors">
          <p>No doctors found for the selected specialization.</p>
        </div>
      )}
    </div>
  );
};

export default DoctorList;
