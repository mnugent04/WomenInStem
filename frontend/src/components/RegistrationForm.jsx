import React, { useState, useEffect } from 'react';
import api from '../services/api';

function RegistrationForm({ eventId, onSuccess, onCancel }) {
  const [attendees, setAttendees] = useState([]);
  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    attendeeID: '',
    leaderID: '',
    emergencyContact: '',
  });

  useEffect(() => {
    // Fetch actual Attendee and Leader records (not just Person records)
    Promise.all([
      api.get('/attendees'),
      api.get('/leaders'),
    ])
      .then(([attendeesRes, leadersRes]) => {
        console.log('Fetched attendees:', attendeesRes.data);
        console.log('Fetched leaders:', leadersRes.data);
        setAttendees(attendeesRes.data || []);
        setLeaders(leadersRes.data || []);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching attendees/leaders:', error);
        console.error('Error details:', error.response?.data || error.message);
        // If endpoints don't exist or return errors, try fallback to people
        // But note: this won't work correctly for registration since we need Attendee/Leader IDs
        api.get('/people')
          .then(peopleRes => {
            console.warn('Using people as fallback - registration may not work correctly');
            setAttendees(peopleRes.data || []);
            setLeaders(peopleRes.data || []);
            setLoading(false);
          })
          .catch(err => {
            console.error('Error fetching people:', err);
            setLoading(false);
          });
      });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Only clear the other field if we're changing attendeeID or leaderID
    // Don't clear anything when changing emergencyContact
    if (name === 'attendeeID' || name === 'leaderID') {
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
        // Clear the other field when one is selected
        [name === 'attendeeID' ? 'leaderID' : 'attendeeID']: '',
      }));
    } else {
      // For emergency contact or other fields, just update that field
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.attendeeID && !formData.leaderID) {
      alert('Please select either an attendee or a leader');
      return;
    }

    if (!formData.emergencyContact.trim()) {
      alert('Emergency contact is required');
      return;
    }

    const registrationData = {
      attendeeID: formData.attendeeID ? parseInt(formData.attendeeID) : null,
      leaderID: formData.leaderID ? parseInt(formData.leaderID) : null,
      emergencyContact: formData.emergencyContact.trim(),
    };

    api.post(`/events/${eventId}/registrations`, registrationData)
      .then(response => {
        alert('Registration successful!');
        setFormData({
          attendeeID: '',
          leaderID: '',
          emergencyContact: '',
        });
        if (onSuccess) onSuccess();
      })
      .catch(error => {
        console.error('Error registering:', error);
        alert('Error registering: ' + (error.response?.data?.detail || error.message));
      });
  };

  if (loading) return <div>Loading...</div>;

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid">
        <label>
          Register as Attendee:
          <select
            name="attendeeID"
            value={formData.attendeeID}
            onChange={handleChange}
          >
            <option value="">Select an attendee...</option>
            {attendees.length > 0 ? (
              attendees.map((person) => (
                <option key={person.id} value={person.id}>
                  {person.firstName} {person.lastName}
                </option>
              ))
            ) : (
              <option value="" disabled>No attendees available</option>
            )}
          </select>
          {attendees.length === 0 && !loading && (
            <small style={{ color: '#666', fontStyle: 'italic' }}>
              No attendees found. Make sure attendees exist in the database.
            </small>
          )}
        </label>
        <label>
          Or Register as Leader:
          <select
            name="leaderID"
            value={formData.leaderID}
            onChange={handleChange}
          >
            <option value="">Select a leader...</option>
            {leaders.length > 0 ? (
              leaders.map((person) => (
                <option key={person.id} value={person.id}>
                  {person.firstName} {person.lastName}
                </option>
              ))
            ) : (
              <option value="" disabled>No leaders available</option>
            )}
          </select>
          {leaders.length === 0 && !loading && (
            <small style={{ color: '#666', fontStyle: 'italic' }}>
              No leaders found. Make sure leaders exist in the database.
            </small>
          )}
        </label>
        <label>
          Emergency Contact:
          <input
            type="text"
            name="emergencyContact"
            placeholder="Emergency contact information"
            value={formData.emergencyContact}
            onChange={handleChange}
            required
          />
        </label>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
        <button type="submit">Register</button>
        {onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default RegistrationForm;

