import React, { useState, useEffect } from 'react';
import api from '../services/api';

function LiveCheckIn({ eventId }) {
  const [checkIns, setCheckIns] = useState(null);
  const [loading, setLoading] = useState(false);
  const [people, setPeople] = useState([]);
  const [selectedPersonId, setSelectedPersonId] = useState('');

  useEffect(() => {
    fetchCheckIns();
    fetchPeople();
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchCheckIns, 5000);
    return () => clearInterval(interval);
  }, [eventId]);

  const fetchCheckIns = () => {
    setLoading(true);
    api.get(`/event/${eventId}/live-checkins`)
      .then(response => {
        setCheckIns(response.data);
        setLoading(false);
      })
      .catch(error => {
        if (error.response?.status === 404) {
          // No check-ins yet
          setCheckIns({ count: 0, students: [], message: 'No one checked in yet' });
        } else {
          console.error('Error fetching check-ins:', error);
        }
        setLoading(false);
      });
  };

  const fetchPeople = () => {
    api.get('/people')
      .then(response => {
        setPeople(response.data);
      })
      .catch(error => {
        console.error('Error fetching people:', error);
      });
  };

  const handleCheckIn = () => {
    if (!selectedPersonId) {
      alert('Please select a person');
      return;
    }

    api.post(`/event/${eventId}/checkin/${selectedPersonId}`)
      .then(() => {
        setSelectedPersonId('');
        fetchCheckIns();
      })
      .catch(error => {
        console.error('Error checking in:', error);
        alert('Error: ' + (error.response?.data?.detail || error.message));
      });
  };

  const handleCheckOut = (personId) => {
    if (window.confirm('Check out this person?')) {
      api.delete(`/event/${eventId}/checkin/${personId}`)
        .then(() => {
          fetchCheckIns();
        })
        .catch(error => {
          console.error('Error checking out:', error);
          alert('Error: ' + (error.response?.data?.detail || error.message));
        });
    }
  };

  return (
    <div style={{ marginTop: '1rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '4px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h4>Live Check-In (Redis)</h4>
        <span style={{ fontSize: '0.9em', color: '#666' }}>
          Auto-refreshes every 5 seconds
        </span>
      </div>

      {/* Check In Form */}
      <div style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <select
            value={selectedPersonId}
            onChange={(e) => setSelectedPersonId(e.target.value)}
            style={{ flex: '1', minWidth: '200px' }}
          >
            <option value="">Select a person to check in...</option>
            {people.map((person) => (
              <option key={person.id} value={person.id}>
                {person.firstName} {person.lastName}
              </option>
            ))}
          </select>
          <button onClick={handleCheckIn}>Check In</button>
        </div>
      </div>

      {/* Check-In List */}
      {loading ? (
        <div>Loading...</div>
      ) : checkIns ? (
        <div>
          <div style={{ marginBottom: '0.5rem' }}>
            <strong>Checked In: {checkIns.count || 0}</strong>
          </div>
          {checkIns.students && checkIns.students.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {checkIns.students.map((student) => (
                <li
                  key={student.studentId}
                  style={{
                    padding: '0.5rem',
                    marginBottom: '0.5rem',
                    backgroundColor: '#e8f5e9',
                    borderRadius: '4px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div>
                    <strong>{student.firstName} {student.lastName}</strong>
                    {student.checkInTime && (
                      <div style={{ fontSize: '0.85em', color: '#666' }}>
                        Checked in: {new Date(student.checkInTime).toLocaleString()}
                      </div>
                    )}
                  </div>
                  <button
                    className="secondary outline"
                    onClick={() => handleCheckOut(student.studentId)}
                  >
                    Check Out
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div style={{ fontStyle: 'italic', color: '#666' }}>
              {checkIns.message || 'No one checked in yet'}
            </div>
          )}
        </div>
      ) : (
        <div>Error loading check-ins</div>
      )}
    </div>
  );
}

export default LiveCheckIn;


