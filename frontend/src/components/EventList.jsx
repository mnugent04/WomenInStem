import React from 'react';
import EventNotes from './EventNotes';

function EventList({ events, onEventClick, expandedEventId, eventRegistrations, onEdit, onDelete, onRegister }) {
  return (
    <figure>
      <table role="grid">
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Date & Time</th>
            <th scope="col">Location</th>
            <th scope="col">Type</th>
            {(onEdit || onDelete) && <th scope="col">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <React.Fragment key={event.id}>
              <tr>
                <td>
                  <button
                    onClick={() => onEventClick(event.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'inherit',
                      cursor: 'pointer',
                      textDecoration: 'underline',
                      padding: 0,
                      font: 'inherit',
                    }}
                  >
                    {event.name}
                    {expandedEventId === event.id ? ' ▼' : ' ▶'}
                  </button>
                </td>
                <td>{event.dateTime}</td>
                <td>{event.location}</td>
                <td>{event.type}</td>
                {(onEdit || onDelete) && (
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      {onEdit && (
                        <button className="secondary" onClick={() => onEdit(event)}>
                          Edit
                        </button>
                      )}
                      {onDelete && (
                        <button className="secondary outline" onClick={() => onDelete(event.id)}>
                          Delete
                        </button>
                      )}
                    </div>
                  </td>
                )}
              </tr>
              {expandedEventId === event.id && eventRegistrations && (
                <tr>
                  <td colSpan={onEdit || onDelete ? "5" : "4"} style={{ paddingLeft: '2rem', paddingTop: '1rem', paddingBottom: '1rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <strong>Registered ({eventRegistrations.length}):</strong>
                        {onRegister && (
                          <button className="secondary" onClick={() => onRegister(event.id)}>
                            Register Someone
                          </button>
                        )}
                      </div>
                      {eventRegistrations.length > 0 ? (
                        <ul style={{ marginTop: '0.5rem', marginBottom: 0 }}>
                          {eventRegistrations.map((registration) => {
                            const isLeader = registration.leaderId !== null && registration.leaderId !== undefined;
                            const isAttendee = registration.attendeeId !== null && registration.attendeeId !== undefined;
                            
                            return (
                              <li key={registration.id} style={{ marginBottom: '0.5rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                                  <span>
                                    {registration.firstName} {registration.lastName}
                                  </span>
                                  {isLeader && (
                                    <span style={{
                                      backgroundColor: '#4a90e2',
                                      color: 'white',
                                      padding: '0.2rem 0.5rem',
                                      borderRadius: '4px',
                                      fontSize: '0.85em',
                                      fontWeight: 'bold'
                                    }}>
                                      Leader
                                    </span>
                                  )}
                                  {isAttendee && (
                                    <span style={{
                                      backgroundColor: '#28a745',
                                      color: 'white',
                                      padding: '0.2rem 0.5rem',
                                      borderRadius: '4px',
                                      fontSize: '0.85em',
                                      fontWeight: 'bold'
                                    }}>
                                      Attendee
                                    </span>
                                  )}
                                  {registration.emergencyContact && (
                                    <span style={{ color: '#666', fontSize: '0.9em' }}>
                                      (Emergency Contact: {registration.emergencyContact})
                                    </span>
                                  )}
                                </div>
                              </li>
                            );
                          })}
                        </ul>
                      ) : (
                        <div style={{ fontStyle: 'italic', color: '#666' }}>
                          No registrations yet.
                        </div>
                      )}
                      <EventNotes eventId={event.id} />
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </figure>
  );
}

export default EventList;
