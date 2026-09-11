import React, { useState, useEffect } from 'react';
import { hospitalsAPI } from '../services/api';
import '../styles/HospitalList.css';

const HospitalList = () => {
  const [hospitals, setHospitals] = useState([]);
  const [cities, setCities] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState('');
  const [emergencyOnly, setEmergencyOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedHospital, setSelectedHospital] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadHospitals();
  }, [selectedCity, selectedSpecialization, emergencyOnly]);

  const loadInitialData = async () => {
    try {
      const [citiesData, specsData] = await Promise.all([
        hospitalsAPI.getCities(),
        hospitalsAPI.getSpecializations()
      ]);
      setCities(citiesData.cities);
      setSpecializations(specsData.specializations);
    } catch (error) {
      console.error('Error loading filter data:', error);
    }
  };

  const loadHospitals = async () => {
    setIsLoading(true);
    try {
      const data = await hospitalsAPI.getHospitals({
        city: selectedCity || null,
        specialization: selectedSpecialization || null,
        emergencyOnly
      });
      setHospitals(data);
    } catch (error) {
      console.error('Error loading hospitals:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearFilters = () => {
    setSelectedCity('');
    setSelectedSpecialization('');
    setEmergencyOnly(false);
  };

  if (selectedHospital) {
    return (
      <div className="hospital-detail-container">
        <button className="back-btn" onClick={() => setSelectedHospital(null)}>
          ← Back to Hospitals
        </button>
        
        <div className="hospital-detail-card">
          <div className="hospital-detail-header">
            <div className="hospital-icon-large">🏥</div>
            <div className="hospital-header-info">
              <h2>{selectedHospital.name}</h2>
              <p className="hospital-address">📍 {selectedHospital.address}</p>
              <p className="hospital-city">{selectedHospital.city}</p>
            </div>
            <div className="hospital-rating-large">
              ⭐ {selectedHospital.rating}
            </div>
          </div>

          <div className="hospital-detail-content">
            <div className="detail-section">
              <h3>📞 Contact Information</h3>
              <p><strong>Phone:</strong> {selectedHospital.phone}</p>
              {selectedHospital.email && (
                <p><strong>Email:</strong> {selectedHospital.email}</p>
              )}
            </div>

            <div className="detail-section">
              <h3>🏥 Hospital Information</h3>
              <p><strong>Bed Capacity:</strong> {selectedHospital.bed_count} beds</p>
              <p>
                <strong>Emergency Services:</strong> 
                <span className={`emergency-badge ${selectedHospital.emergency_available ? 'available' : 'unavailable'}`}>
                  {selectedHospital.emergency_available ? '✓ Available 24/7' : '✗ Not Available'}
                </span>
              </p>
            </div>

            <div className="detail-section">
              <h3>🩺 Specializations</h3>
              <div className="tags-container">
                {selectedHospital.specializations.map((spec, index) => (
                  <span key={index} className="spec-tag">{spec}</span>
                ))}
              </div>
            </div>

            <div className="detail-section">
              <h3>🏢 Facilities</h3>
              <div className="tags-container">
                {selectedHospital.facilities.map((facility, index) => (
                  <span key={index} className="facility-tag">{facility}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="hospitals-container">
      <div className="hospitals-header">
        <h2>🏥 Find Hospitals</h2>
        <p>Search for hospitals and medical facilities near you</p>
      </div>

      <div className="hospitals-filters">
        <select 
          value={selectedCity} 
          onChange={(e) => setSelectedCity(e.target.value)}
          className="filter-select"
        >
          <option value="">All Cities</option>
          {cities.map(city => (
            <option key={city} value={city}>{city}</option>
          ))}
        </select>

        <select 
          value={selectedSpecialization} 
          onChange={(e) => setSelectedSpecialization(e.target.value)}
          className="filter-select"
        >
          <option value="">All Specializations</option>
          {specializations.map(spec => (
            <option key={spec} value={spec}>{spec}</option>
          ))}
        </select>

        <label className="emergency-filter">
          <input 
            type="checkbox" 
            checked={emergencyOnly}
            onChange={(e) => setEmergencyOnly(e.target.checked)}
          />
          Emergency Services Only
        </label>

        {(selectedCity || selectedSpecialization || emergencyOnly) && (
          <button className="clear-filters-btn" onClick={clearFilters}>
            Clear Filters
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="hospitals-loading">
          <div className="loading-spinner"></div>
          <p>Loading hospitals...</p>
        </div>
      ) : hospitals.length === 0 ? (
        <div className="no-hospitals">
          <div className="no-hospitals-icon">🏥</div>
          <h3>No Hospitals Found</h3>
          <p>Try adjusting your filters</p>
        </div>
      ) : (
        <div className="hospitals-grid">
          {hospitals.map(hospital => (
            <div 
              key={hospital.id} 
              className="hospital-card"
              onClick={() => setSelectedHospital(hospital)}
            >
              <div className="hospital-card-header">
                <div className="hospital-icon">🏥</div>
                <div className="hospital-rating">⭐ {hospital.rating}</div>
              </div>
              
              <h3>{hospital.name}</h3>
              <p className="hospital-address">{hospital.address}</p>
              <p className="hospital-city">📍 {hospital.city}</p>
              
              <div className="hospital-info-row">
                <span className="bed-count">🛏️ {hospital.bed_count} beds</span>
                {hospital.emergency_available && (
                  <span className="emergency-badge available">🚨 24/7</span>
                )}
              </div>

              <div className="hospital-specs">
                {hospital.specializations.slice(0, 3).map((spec, index) => (
                  <span key={index} className="spec-tag-small">{spec}</span>
                ))}
                {hospital.specializations.length > 3 && (
                  <span className="more-specs">+{hospital.specializations.length - 3} more</span>
                )}
              </div>

              <div className="hospital-contact">
                <span>📞 {hospital.phone}</span>
              </div>

              <button className="view-details-btn">View Details</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HospitalList;
