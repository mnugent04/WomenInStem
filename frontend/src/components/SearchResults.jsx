import React from 'react';
import { useNavigate } from 'react-router-dom';

function SearchResults({ results }) {
  const navigate = useNavigate();

  if (!results) return null;

  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return 'N/A';
    const date = new Date(dateTimeStr);
    return date.toLocaleString();
  };

  const totals = results.totals || {};
  const totalResults =
    (totals.events || 0) +
    (totals.people || 0) +
    (totals.leaders || 0) +
    (totals.attendees || 0) +
    (totals.volunteers || 0) +
    (totals.eventTypes || 0);

  const sectionTitle = (title, color) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    marginBottom: '1rem',
    color,
    borderBottom: `2px solid ${color}`,
    paddingBottom: '0.35rem'
  });

  const card = (bg = '#fff', border = '#e5e7eb') => ({
    border: `1px solid ${border}`,
    borderRadius: '8px',
    padding: '1rem',
    backgroundColor: bg,
    boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
  });

  const badge = (bg) => ({
    marginLeft: '0.5rem',
    padding: '0.25rem 0.5rem',
    backgroundColor: bg,
    color: 'white',
    borderRadius: '4px',
    fontSize: '0.8rem'
  });

  const grid = (min = '260px') => ({
    display: 'grid',
    gridTemplateColumns: `repeat(auto-fill, minmax(${min}, 1fr))`,
    gap: '1rem'
  });

  if (totalResults === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
        <p>No results found for "{results.query}"</p>
        <p style={{ fontSize: '0.95rem', marginTop: '0.5rem' }}>
          Try searching for event names, people names, roles (leader, attendee, volunteer), or event types.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>
          Search Results for "{results.query}"
          <span style={{ fontSize: '1rem', color: '#6b7280', marginLeft: '0.5rem', fontWeight: 'normal' }}>
            ({totalResults} total)
          </span>
        </h2>
      </div>

      {/* Event Types */}
      {results.eventTypes && results.eventTypes.length > 0 && (
        <section>
          <div style={sectionTitle('Event Types', '#2563eb')}>
            <h3 style={{ margin: 0, color: '#2563eb' }}>
              Event Types ({totals.eventTypes || 0})
            </h3>
          </div>
          <div style={grid('260px')}>
            {results.eventTypes.map((et) => (
              <div key={et._id} style={card('#f0f9ff', '#dbeafe')}>
                <strong style={{ fontSize: '1.1rem', color: '#2563eb' }}>
                  {et.event_type}
                </strong>
                {et.description && (
                  <p style={{ marginTop: '0.5rem', color: '#4b5563' }}>{et.description}</p>
                )}
                {et.required_items && (
                  <div style={{ marginTop: '0.5rem', color: '#374151' }}>
                    <strong>Required Items:</strong> {et.required_items.join(', ')}
                  </div>
                )}
                {et.extra_notes && (
                  <div style={{ marginTop: '0.5rem', color: '#6b7280', fontSize: '0.95rem' }}>
                    <strong>Notes:</strong> {et.extra_notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Events */}
      {results.events && results.events.length > 0 && (
        <section>
          <div style={sectionTitle('Events', '#10b981')}>
            <h3 style={{ margin: 0, color: '#10b981' }}>
              Events ({totals.events || 0})
            </h3>
          </div>
          <div style={grid('260px')}>
            {results.events.map((event) => (
              <div
                key={event.id}
                onClick={() => navigate(`/events`)}
                style={{ ...card('#f0fdf4', '#d1fae5'), cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <strong style={{ fontSize: '1.05rem', color: '#047857' }}>
                    {event.name}
                  </strong>
                  <span style={badge('#10b981')}>{event.type}</span>
                </div>
                <div style={{ fontSize: '0.95rem', color: '#4b5563', marginTop: '0.5rem', lineHeight: 1.5 }}>
                  <div><strong>Date/Time:</strong> {formatDateTime(event.dateTime)}</div>
                  <div><strong>Location:</strong> {event.location}</div>
                  {event.notes && <div><strong>Notes:</strong> {event.notes}</div>}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* People */}
      {results.people && results.people.length > 0 && (
        <section>
          <div style={sectionTitle('People', '#3b82f6')}>
            <h3 style={{ margin: 0, color: '#3b82f6' }}>
              People ({totals.people || 0})
            </h3>
          </div>
          <div style={grid('220px')}>
            {results.people.map((person) => (
              <div
                key={person.id}
                onClick={() => navigate(`/people`)}
                style={{ ...card('#eff6ff', '#dbeafe'), cursor: 'pointer' }}
              >
                <strong style={{ color: '#1d4ed8' }}>{person.firstName} {person.lastName}</strong>
                {person.age && <div style={{ color: '#4b5563', fontSize: '0.95rem', marginTop: '0.25rem' }}>Age: {person.age}</div>}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Leaders */}
      {results.roles?.leaders && results.roles.leaders.length > 0 && (
        <section>
          <div style={sectionTitle('Leaders', '#3b82f6')}>
            <h3 style={{ margin: 0, color: '#3b82f6' }}>
              Leaders ({totals.leaders || 0})
            </h3>
          </div>
          <div style={grid('220px')}>
            {results.roles.leaders.map((leader) => (
              <div
                key={leader.id}
                onClick={() => navigate(`/people`)}
                style={{ ...card('#eff6ff', '#dbeafe'), cursor: 'pointer' }}
              >
                <strong style={{ color: '#1d4ed8' }}>{leader.firstName} {leader.lastName}</strong>
                <span style={badge('#3b82f6')}>Leader</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Attendees */}
      {results.roles?.attendees && results.roles.attendees.length > 0 && (
        <section>
          <div style={sectionTitle('Attendees', '#10b981')}>
            <h3 style={{ margin: 0, color: '#10b981' }}>
              Attendees ({totals.attendees || 0})
            </h3>
          </div>
          <div style={grid('220px')}>
            {results.roles.attendees.map((attendee) => (
              <div
                key={attendee.id}
                onClick={() => navigate(`/people`)}
                style={{ ...card('#f0fdf4', '#d1fae5'), cursor: 'pointer' }}
              >
                <strong style={{ color: '#047857' }}>{attendee.firstName} {attendee.lastName}</strong>
                {attendee.guardian && (
                  <div style={{ fontSize: '0.95rem', color: '#4b5563', marginTop: '0.25rem' }}>
                    Guardian: {attendee.guardian}
                  </div>
                )}
                <span style={badge('#10b981')}>Attendee</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Volunteers */}
      {results.roles?.volunteers && results.roles.volunteers.length > 0 && (
        <section>
          <div style={sectionTitle('Volunteers', '#f59e0b')}>
            <h3 style={{ margin: 0, color: '#f59e0b' }}>
              Volunteers ({totals.volunteers || 0})
            </h3>
          </div>
          <div style={grid('220px')}>
            {results.roles.volunteers.map((volunteer) => (
              <div
                key={volunteer.id}
                onClick={() => navigate(`/people`)}
                style={{ ...card('#fffbeb', '#fde68a'), cursor: 'pointer' }}
              >
                <strong style={{ color: '#b45309' }}>{volunteer.firstName} {volunteer.lastName}</strong>
                <span style={badge('#f59e0b')}>Volunteer</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default SearchResults;

