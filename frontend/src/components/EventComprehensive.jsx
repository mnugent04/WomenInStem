import React, { useState, useEffect } from 'react';
import api from '../services/api';

function EventComprehensive({ eventId }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSummary();
  }, [eventId]);

  const fetchSummary = () => {
    setLoading(true);
    setError(null);
    api.get(`/events/${eventId}/comprehensive`)
      .then(response => {
        console.log('Comprehensive summary response:', response.data);
        setSummary(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching comprehensive summary:', error);
        console.error('Error response:', error.response?.data);
        console.error('Error status:', error.response?.status);
        setError(error);
        setLoading(false);
      });
  };

  if (loading) return <div>Loading comprehensive summary...</div>;
  if (error) {
    return (
      <div style={{ padding: '1rem', border: '1px solid #f44336', borderRadius: '4px', backgroundColor: '#ffebee' }}>
        <strong>Error loading comprehensive summary:</strong>
        <p>{error.response?.data?.detail || error.message || 'Unknown error'}</p>
        <button className="secondary" onClick={fetchSummary}>Retry</button>
      </div>
    );
  }
  if (!summary) return <div>No data available</div>;

  return (
    <div style={{ marginTop: '1rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h4>📊 Comprehensive Event Summary</h4>
        <button className="secondary" onClick={fetchSummary}>Refresh</button>
      </div>

      {/* Summary Statistics */}
      <div className="grid" style={{ marginBottom: '1.5rem' }}>
        <article style={{ padding: '1rem', textAlign: 'center', backgroundColor: 'white' }}>
          <h5>{summary.summary.totalRegistered}</h5>
          <p>Total Registered</p>
          <small style={{ color: '#666' }}>Source: MySQL</small>
        </article>
        <article style={{ padding: '1rem', textAlign: 'center', backgroundColor: 'white' }}>
          <h5>{summary.summary.totalCheckedIn}</h5>
          <p>Checked In</p>
          <small style={{ color: '#666' }}>Source: Redis</small>
        </article>
        <article style={{ padding: '1rem', textAlign: 'center', backgroundColor: 'white' }}>
          <h5>{summary.summary.attendanceRate}%</h5>
          <p>Attendance Rate</p>
          <small style={{ color: '#666' }}>Calculated</small>
        </article>
        <article style={{ padding: '1rem', textAlign: 'center', backgroundColor: 'white' }}>
          <h5>{summary.summary.notesCount}</h5>
          <p>Event Notes</p>
          <small style={{ color: '#666' }}>Source: MongoDB</small>
        </article>
      </div>

      {/* Registration Breakdown */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h5>Registration Breakdown (MySQL)</h5>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
          <span style={{ padding: '0.5rem', backgroundColor: '#28a745', color: 'white', borderRadius: '4px' }}>
            Attendees: {summary.registrations.attendees}
          </span>
          <span style={{ padding: '0.5rem', backgroundColor: '#4a90e2', color: 'white', borderRadius: '4px' }}>
            Leaders: {summary.registrations.leaders}
          </span>
          {summary.registrations.volunteers !== undefined && (
            <span style={{ padding: '0.5rem', backgroundColor: '#ff9800', color: 'white', borderRadius: '4px' }}>
              Volunteers: {summary.registrations.volunteers}
            </span>
          )}
        </div>
      </div>

      {/* Live Check-Ins from Redis */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h5>Live Check-Ins (Redis) - {summary.liveCheckIns.count} checked in</h5>
        {summary.liveCheckIns.students.length > 0 ? (
          <ul style={{ marginTop: '0.5rem' }}>
            {summary.liveCheckIns.students.map((student) => (
              <li key={student.personId} style={{ marginBottom: '0.5rem', padding: '0.5rem', backgroundColor: '#e8f5e9', borderRadius: '4px' }}>
                <strong>{student.firstName} {student.lastName}</strong>
                {student.checkInTime && (
                  <span style={{ fontSize: '0.9em', color: '#666', marginLeft: '0.5rem' }}>
                    - Checked in: {new Date(student.checkInTime).toLocaleString()}
                  </span>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ fontStyle: 'italic', color: '#666' }}>No one checked in yet</p>
        )}
      </div>

      {/* Event Notes from MongoDB */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h5>Event Notes & Highlights (MongoDB) - {summary.notes.count} notes</h5>
        {summary.notes.list.length > 0 ? (
          <ul style={{ marginTop: '0.5rem' }}>
            {summary.notes.list.map((note) => (
              <li key={note._id} style={{ marginBottom: '0.5rem', padding: '0.5rem', backgroundColor: 'white', border: '1px solid #eee', borderRadius: '4px' }}>
                {note.notes && <p><strong>Notes:</strong> {note.notes}</p>}
                {note.concerns && (
                  <p style={{ color: '#d32f2f' }}><strong>Concerns:</strong> {note.concerns}</p>
                )}
                {note.studentWins && (
                  <p style={{ color: '#2e7d32' }}><strong>Student Wins:</strong> {note.studentWins}</p>
                )}
                {note.created && (
                  <small style={{ color: '#999' }}>
                    Created: {new Date(note.created).toLocaleString()}
                  </small>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ fontStyle: 'italic', color: '#666' }}>No notes yet</p>
        )}
      </div>

      {/* Data Sources Info */}
      <div style={{ padding: '0.5rem', backgroundColor: '#e3f2fd', borderRadius: '4px', fontSize: '0.9em' }}>
        <strong>Data Sources:</strong> {Object.entries(summary.dataSources).map(([key, value]) => `${key}: ${value}`).join(' | ')}
      </div>
    </div>
  );
}

export default EventComprehensive;

