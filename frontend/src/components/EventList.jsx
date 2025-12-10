import React, { useState } from 'react';
import EventNotes from './EventNotes';
import LiveCheckIn from './LiveCheckIn';
import EventComprehensive from './EventComprehensive';

function EventList({ events, onEventClick, expandedEventId, eventRegistrations, onEdit, onDelete, onRegister }) {
  const [openSections, setOpenSections] = useState({}); // { [eventId]: { comprehensive: true, checkIn: false, notes: true } }

  const toggleSection = (eventId, section) => {
    setOpenSections(prev => ({
      ...prev,
      [eventId]: {
        ...prev[eventId],
        [section]: !prev[eventId]?.[section]
      }
    }));
  };

  return (
    <figure>
      <table role="grid">
        <thead>
          <tr>
            <th>Name</th>
            <th>Date & Time</th>
            <th>Location</th>
            <th>Type</th>
            {(onEdit || onDelete) && <th>Actions</th>}
          </tr>
        </thead>
        <tbody>
          {events.map((event) => {
            const sections = openSections[event.id] || {};
            return (
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
                      {event.name} {expandedEventId === event.id ? ' ▼' : ' ▶'}
                    </button>
                  </td>
                  <td>{event.dateTime}</td>
                  <td>{event.location}</td>
                  <td>{event.type}</td>
                  {(onEdit || onDelete) && (
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {onEdit && <button className="secondary" onClick={() => onEdit(event)}>Edit</button>}
                        {onDelete && <button className="secondary outline" onClick={() => onDelete(event.id)}>Delete</button>}
                      </div>
                    </td>
                  )}
                </tr>

                {expandedEventId === event.id && (
                  <tr>
                    <td colSpan={onEdit || onDelete ? "5" : "4"} style={{ paddingLeft: '2rem', paddingTop: '1rem', paddingBottom: '1rem' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

                        {/* Registrations */}
                        {eventRegistrations && (
                          <>
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
                                {eventRegistrations.map(reg => (
                                  <li key={reg.id}>
                                    {reg.firstName} {reg.lastName} {reg.leaderId && '(Leader)'} {reg.attendeeId && '(Attendee)'} {reg.volunteerId && '(Volunteer)'}
                                  </li>
                                ))}
                              </ul>
                            ) : <div style={{ fontStyle: 'italic', color: '#666' }}>No registrations yet.</div>}
                          </>
                        )}

                        {/* Collapsible Sections */}
                        <div>
                          <button className="secondary" onClick={() => toggleSection(event.id, 'comprehensive')}>
                            {sections.comprehensive ? 'Hide' : 'Show'} Comprehensive Summary
                          </button>
                          {sections.comprehensive && <EventComprehensive eventId={event.id} />}
                        </div>

                        <div>
                          <button className="secondary" onClick={() => toggleSection(event.id, 'checkIn')}>
                            {sections.checkIn ? 'Hide' : 'Show'} Live Check-Ins
                          </button>
                          {sections.checkIn && <LiveCheckIn eventId={event.id} />}
                        </div>

                        <div>
                          <button className="secondary" onClick={() => toggleSection(event.id, 'notes')}>
                            {sections.notes ? 'Hide' : 'Show'} Event Notes
                          </button>
                          {sections.notes && <EventNotes eventId={event.id} />}
                        </div>

                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            )
          })}
        </tbody>
      </table>
    </figure>
  );
}

export default EventList;
