import React, { useState, useEffect } from 'react';
import { graphqlRequest, mutations } from '../services/api';
import axios from 'axios';

// Note: Fetching attendees/leaders/volunteers lists are not yet available in GraphQL schema
// Using REST API as fallback until GraphQL queries are added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function RegistrationForm({ eventId, onSuccess, onCancel }) {
  const [attendees, setAttendees] = useState([]);
  const [leaders, setLeaders] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    attendeeID: '',
    leaderID: '',
    volunteerID: '',
    emergencyContact: '',
  });

  useEffect(() => {
    // TODO: Replace with GraphQL queries when attendees/leaders/volunteers queries are added to schema
    Promise.all([
      REST_API.get('/attendees'),
      REST_API.get('/leaders'),
      REST_API.get('/volunteers'),
    ])
      .then(([attendeesRes, leadersRes, volunteersRes]) => {
        console.log('Fetched attendees:', attendeesRes.data);
        console.log('Fetched leaders:', leadersRes.data);
        console.log('Fetched volunteers:', volunteersRes.data);
        setAttendees(attendeesRes.data || []);
        setLeaders(leadersRes.data || []);
        setVolunteers(volunteersRes.data || []);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching attendees/leaders/volunteers:', error);
        console.error('Error details:', error.response?.data || error.message);
        setLoading(false);
      });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Clear other role fields when one is selected
    // Don't clear anything when changing emergencyContact
    if (name === 'attendeeID' || name === 'leaderID' || name === 'volunteerID') {
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
        // Clear the other role fields when one is selected
        attendeeID: name === 'attendeeID' ? value : '',
        leaderID: name === 'leaderID' ? value : '',
        volunteerID: name === 'volunteerID' ? value : '',
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
    
    if (!formData.attendeeID && !formData.leaderID && !formData.volunteerID) {
      alert('Please select either an attendee, leader, or volunteer');
      return;
    }

    if (!formData.emergencyContact.trim()) {
      alert('Emergency contact is required');
      return;
    }

    const registrationData = {
      attendeeID: formData.attendeeID ? parseInt(formData.attendeeID) : null,
      leaderID: formData.leaderID ? parseInt(formData.leaderID) : null,
      volunteerID: formData.volunteerID ? parseInt(formData.volunteerID) : null,
      emergencyContact: formData.emergencyContact.trim(),
    };

    // Use GraphQL mutation for registration
    graphqlRequest(mutations.registerForEvent, {
      eventId,
      attendeeId: registrationData.attendeeID || null,
      leaderId: registrationData.leaderID || null,
      volunteerId: registrationData.volunteerID || null,
      emergencyContact: registrationData.emergencyContact
    })
      .then(() => {
        alert('Registration successful!');
        setFormData({
          attendeeID: '',
          leaderID: '',
          volunteerID: '',
          emergencyContact: '',
        });
        if (onSuccess) onSuccess();
      })
      .catch(error => {
        console.error('Error registering:', error);
        alert('Error registering: ' + (error.response?.errors?.[0]?.message || error.message));
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
          Or Register as Volunteer:
          <select
            name="volunteerID"
            value={formData.volunteerID}
            onChange={handleChange}
          >
            <option value="">Select a volunteer...</option>
            {volunteers.length > 0 ? (
              volunteers.map((person) => (
                <option key={person.id} value={person.id}>
                  {person.firstName} {person.lastName}
                </option>
              ))
            ) : (
              <option value="" disabled>No volunteers available</option>
            )}
          </select>
          {volunteers.length === 0 && !loading && (
            <small style={{ color: '#666', fontStyle: 'italic' }}>
              No volunteers found. Make sure volunteers exist in the database.
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

