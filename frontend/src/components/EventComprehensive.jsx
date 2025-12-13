import React, { useState, useEffect } from 'react';
import { graphqlRequest, queries } from '../services/api';

function EventComprehensive({ eventId }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSummary();
  }, [eventId]);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await graphqlRequest(queries.getComprehensiveEventSummary, { eventId });
      console.log('Comprehensive summary response:', data);
      setSummary(data.comprehensiveEventSummary);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching comprehensive summary:', err);
      setError(err);
      setLoading(false);
    }
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
        {/* Note: Students list is not included in comprehensiveEventSummary, only count */}
        <p style={{ fontStyle: 'italic', color: '#666' }}>
          {summary.liveCheckIns.count > 0 ? `${summary.liveCheckIns.count} students checked in` : 'No one checked in yet'}
        </p>
      </div>

      {/* Event Notes from MongoDB */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h5>Event Notes & Highlights (MongoDB) - {summary.notes.count} notes</h5>
        <p style={{ fontStyle: 'italic', color: '#666' }}>
          {summary.notes.count > 0 ? `${summary.notes.count} notes recorded` : 'No notes yet'}
        </p>
        <p style={{ fontSize: '0.9em', color: '#999' }}>
          (Note: Individual note details are not included in comprehensive summary. Use Event Notes section to view details.)
        </p>
      </div>

      {/* Data Sources Info */}
      <div style={{ padding: '0.5rem', backgroundColor: '#e3f2fd', borderRadius: '4px', fontSize: '0.9em' }}>
        <strong>Data Sources:</strong> {Object.entries(summary.dataSources).map(([key, value]) => `${key}: ${value}`).join(' | ')}
      </div>
    </div>
  );
}

export default EventComprehensive;

