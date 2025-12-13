import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Note: Person profile query is not yet available in GraphQL schema
// Using REST API as fallback until GraphQL query is added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function PersonProfile({ personId, onClose }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (personId) {
      setLoading(true);
      // TODO: Replace with GraphQL query when personProfile query is added to schema
      REST_API.get(`/people/${personId}/profile`)
        .then(response => {
          setProfile(response.data);
          setLoading(false);
        })
        .catch(err => {
          setError(err);
          setLoading(false);
        });
    }
  }, [personId]);

  if (!personId) return null;
  if (loading) return <div>Loading profile...</div>;
  if (error) return <div>Error loading profile: {error.message}</div>;
  if (!profile) return <div>Profile not found</div>;

  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return 'N/A';
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '2rem'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '2rem',
        maxWidth: '900px',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        position: 'relative'
      }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'none',
            border: 'none',
            fontSize: '1.5rem',
            cursor: 'pointer',
            color: '#666'
          }}
        >
          ×
        </button>

        <h2 style={{ marginTop: 0, marginBottom: '1.5rem', color: '#2563eb' }}>
          {profile.person.firstName} {profile.person.lastName}
        </h2>

        {/* Basic Info */}
        <section style={{ marginBottom: '2rem' }}>
          <h3 style={{ borderBottom: '2px solid #2563eb', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            Basic Information
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
            <div>
              <strong>Age:</strong> {profile.person.age || 'N/A'}
            </div>
            <div>
              <strong>Person ID:</strong> {profile.person.id}
            </div>
          </div>
        </section>

        {/* Roles */}
        <section style={{ marginBottom: '2rem' }}>
          <h3 style={{ borderBottom: '2px solid #2563eb', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            Roles
          </h3>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            {profile.roles.isAttendee && (
              <span style={{
                backgroundColor: '#10b981',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                fontSize: '0.9rem'
              }}>
                Attendee {profile.roles.guardian && `(Guardian: ${profile.roles.guardian})`}
              </span>
            )}
            {profile.roles.isLeader && (
              <span style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                fontSize: '0.9rem'
              }}>
                Leader
              </span>
            )}
            {profile.roles.isVolunteer && (
              <span style={{
                backgroundColor: '#f59e0b',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                fontSize: '0.9rem'
              }}>
                Volunteer
              </span>
            )}
            {!profile.roles.isAttendee && !profile.roles.isLeader && !profile.roles.isVolunteer && (
              <span style={{ color: '#666', fontStyle: 'italic' }}>No roles assigned</span>
            )}
          </div>
        </section>

        {/* Small Groups */}
        <section style={{ marginBottom: '2rem' }}>
          <h3 style={{ borderBottom: '2px solid #2563eb', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            Small Groups ({profile.smallGroups.totalGroups})
          </h3>
          {profile.smallGroups.asMember.length > 0 && (
            <div style={{ marginBottom: '1rem' }}>
              <strong style={{ color: '#10b981' }}>As Member:</strong>
              <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                {profile.smallGroups.asMember.map(group => (
                  <li key={group.membershipId}>
                    {group.groupName} (ID: {group.groupId})
                  </li>
                ))}
              </ul>
            </div>
          )}
          {profile.smallGroups.asLeader.length > 0 && (
            <div>
              <strong style={{ color: '#3b82f6' }}>As Leader:</strong>
              <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                {profile.smallGroups.asLeader.map(group => (
                  <li key={group.leadershipId}>
                    {group.groupName} (ID: {group.groupId})
                  </li>
                ))}
              </ul>
            </div>
          )}
          {profile.smallGroups.totalGroups === 0 && (
            <p style={{ color: '#666', fontStyle: 'italic' }}>Not part of any small groups</p>
          )}
        </section>

        {/* Event Statistics */}
        <section style={{ marginBottom: '2rem' }}>
          <h3 style={{ borderBottom: '2px solid #2563eb', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            Event Statistics
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '1rem',
            marginBottom: '1rem'
          }}>
            <div style={{
              backgroundColor: '#f3f4f6',
              padding: '1rem',
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#2563eb' }}>
                {profile.events.statistics.totalRegistrations}
              </div>
              <div style={{ color: '#666', fontSize: '0.9rem' }}>Total Registrations</div>
            </div>
            <div style={{
              backgroundColor: '#f3f4f6',
              padding: '1rem',
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
                {profile.events.statistics.totalAttended}
              </div>
              <div style={{ color: '#666', fontSize: '0.9rem' }}>Events Attended</div>
            </div>
            <div style={{
              backgroundColor: '#f3f4f6',
              padding: '1rem',
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
                {profile.events.statistics.attendanceRate}%
              </div>
              <div style={{ color: '#666', fontSize: '0.9rem' }}>Attendance Rate</div>
            </div>
          </div>
        </section>

        {/* Event Registrations */}
        <section style={{ marginBottom: '2rem' }}>
          <h3 style={{ borderBottom: '2px solid #2563eb', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            Event Registrations ({profile.events.registrations.length})
          </h3>
          {profile.events.registrations.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {profile.events.registrations.map(reg => (
                <div key={reg.registrationId} style={{
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                  padding: '1rem',
                  backgroundColor: '#f9fafb'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                    <div>
                      <strong style={{ fontSize: '1.1rem', color: '#2563eb' }}>{reg.eventName}</strong>
                      <span style={{
                        marginLeft: '0.5rem',
                        padding: '0.25rem 0.5rem',
                        backgroundColor: reg.registrationRole === 'Attendee' ? '#10b981' :
                                        reg.registrationRole === 'Leader' ? '#3b82f6' : '#f59e0b',
                        color: 'white',
                        borderRadius: '4px',
                        fontSize: '0.8rem'
                      }}>
                        {reg.registrationRole}
                      </span>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>
                    <div><strong>Type:</strong> {reg.eventType}</div>
                    <div><strong>Date/Time:</strong> {formatDateTime(reg.eventDateTime)}</div>
                    <div><strong>Location:</strong> {reg.eventLocation}</div>
                    {reg.eventNotes && <div><strong>Notes:</strong> {reg.eventNotes}</div>}
                    <div><strong>Emergency Contact:</strong> {reg.emergencyContact}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No event registrations</p>
          )}
        </section>

        {/* Attendance Records */}
        <section>
          <h3 style={{ borderBottom: '2px solid #2563eb', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            Attendance Records ({profile.events.attendance.length})
          </h3>
          {profile.events.attendance.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {profile.events.attendance.map(att => (
                <div key={att.attendanceId} style={{
                  border: '1px solid #e5e7eb',
                  borderRadius: '4px',
                  padding: '1rem',
                  backgroundColor: '#f0fdf4'
                }}>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong style={{ fontSize: '1.1rem', color: '#10b981' }}>{att.eventName}</strong>
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#666' }}>
                    <div><strong>Type:</strong> {att.eventType}</div>
                    <div><strong>Date/Time:</strong> {formatDateTime(att.eventDateTime)}</div>
                    <div><strong>Location:</strong> {att.eventLocation}</div>
                    {att.eventNotes && <div><strong>Notes:</strong> {att.eventNotes}</div>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#666', fontStyle: 'italic' }}>No attendance records</p>
          )}
        </section>
      </div>
    </div>
  );
}

export default PersonProfile;

