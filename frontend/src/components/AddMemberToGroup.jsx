import React, { useState, useEffect } from 'react';
import api from '../services/api';

function AddMemberToGroup({ groupId, onSuccess, onCancel }) {
  const [attendees, setAttendees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAttendeeId, setSelectedAttendeeId] = useState('');

  useEffect(() => {
    api.get('/attendees')
      .then(response => {
        setAttendees(response.data || []);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching attendees:', error);
        setLoading(false);
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedAttendeeId) {
      alert('Please select an attendee');
      return;
    }

    api.post(`/smallgroups/${groupId}/members`, {
      attendeeID: parseInt(selectedAttendeeId)
    })
      .then(() => {
        setSelectedAttendeeId('');
        if (onSuccess) onSuccess();
      })
      .catch(error => {
        console.error('Error adding member:', error);
        alert('Error: ' + (error.response?.data?.detail || error.message));
      });
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

