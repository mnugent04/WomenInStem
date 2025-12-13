import React, { useState, useEffect } from 'react';
import { graphqlRequest, mutations } from '../services/api';
import axios from 'axios';

// Note: Fetching attendees list is not yet available in GraphQL schema
// Using REST API as fallback until GraphQL query is added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function AddMemberToGroup({ groupId, onSuccess, onCancel }) {
  const [attendees, setAttendees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAttendeeId, setSelectedAttendeeId] = useState('');

  useEffect(() => {
    // TODO: Replace with GraphQL query when attendees query is added to schema
    REST_API.get('/attendees')
      .then(response => {
        setAttendees(response.data || []);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching attendees:', error);
        setLoading(false);
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedAttendeeId) {
      alert('Please select an attendee');
      return;
    }

    try {
      // Note: The GraphQL mutation expects attendeeId (the Attendee ID), not personId
      // We need to find the attendee ID from the selected personId
      const attendee = attendees.find(a => a.personId === parseInt(selectedAttendeeId));
      if (!attendee) {
        alert('Attendee not found');
        return;
      }

      await graphqlRequest(mutations.addMemberToGroup, {
        groupId,
        attendeeId: attendee.id
      });
      setSelectedAttendeeId('');
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error('Error adding member:', error);
      alert('Error: ' + (error.response?.errors?.[0]?.message || error.message));
    }
  };

  if (loading) return <div>Loading attendees...</div>;

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid">
        <label>
          Select Attendee to Add:
          <select
            value={selectedAttendeeId}
            onChange={(e) => setSelectedAttendeeId(e.target.value)}
            required
          >
            <option value="">Select an attendee...</option>
            {attendees.map((attendee) => (
              <option key={attendee.id} value={attendee.personId}>
                {attendee.firstName} {attendee.lastName}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
        <button type="submit">Add Member</button>
        {onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default AddMemberToGroup;

