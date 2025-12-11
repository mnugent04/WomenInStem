import React, { useState, useEffect } from 'react';
import EventList from '../components/EventList';
import EventForm from '../components/EventForm';
import RegistrationForm from '../components/RegistrationForm';
import EventTypeManager from '../components/EventTypeManager';
import api from '../services/api';

function Events() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedEventId, setExpandedEventId] = useState(null);
  const [eventRegistrations, setEventRegistrations] = useState(null);
  const [loadingRegistrations, setLoadingRegistrations] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);

  // NEW: Toggles create-event dropdown
  const [showCreateDropdown, setShowCreateDropdown] = useState(false);

  const [registeringForEventId, setRegisteringForEventId] = useState(null);
  const [showEventTypes, setShowEventTypes] = useState(false);

  const fetchEvents = () => {
    setLoading(true);
    api.get('/events')
      .then(response => {
        setEvents(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleEventClick = async (eventId) => {
    if (expandedEventId === eventId) {
      setExpandedEventId(null);
      setEventRegistrations(null);
      return;
    }

    setExpandedEventId(eventId);
    setLoadingRegistrations(true);
    setEventRegistrations(null);

    try {
      const regResponse = await api.get(`/events/${eventId}/registrations`);
      setEventRegistrations(regResponse.data);
    } catch (error) {
      setError(error);
    } finally {
      setLoadingRegistrations(false);
    }
  };

  const handleSave = (eventData) => {
    if (eventData.id) {
      // UPDATE
      const { id, ...updateData } = eventData;

      api.patch(`/events/${id}`, updateData)
        .then(() => {
          setEditingEvent(null);
          setShowCreateDropdown(false); // close form after update
          fetchEvents();
        })
        .catch(error => setError(error));
    } else {
      // CREATE
      const { id, ...createData } = eventData;

      api.post('/events', createData)
        .then(() => {
          setShowCreateDropdown(false); // auto-close after create
          fetchEvents();
        })
        .catch(error => setError(error));
    }
  };

  const handleCancel = () => {
    setEditingEvent(null);
    setShowCreateDropdown(false);
  };

  const handleEdit = (event) => {
    setEditingEvent(event);
    setShowCreateDropdown(true); // open dropdown when editing
  };

  const handleDelete = (eventId) => {
    if (window.confirm('Are you sure you want to delete this event?')) {
      console.warn('Event delete not yet implemented in backend');
    }
  };

  const handleRegisterClick = (eventId) => {
    setRegisteringForEventId(eventId);
  };

  const handleRegistrationSuccess = () => {
    if (expandedEventId) {
      handleEventClick(expandedEventId);
    }
    setRegisteringForEventId(null);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1>Events</h1>
        <button 
          className="secondary" 
          onClick={() => setShowEventTypes(!showEventTypes)}
          style={{
            backgroundColor: showEventTypes ? '#6b7280' : '#2563eb',
            color: 'white',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {showEventTypes ? 'Hide Event Types' : 'Manage Event Types'}
        </button>
      </div>

      {showEventTypes && (
        <div style={{
          marginBottom: '2rem',
          padding: '1.5rem',
          border: '1px solid #ccc',
          borderRadius: '4px',
          backgroundColor: '#fafafa'
        }}>
          <EventTypeManager />
        </div>
      )}

      {/* --- CREATE EVENT DROPDOWN BUTTON --- */}
      <button
        onClick={() => {
          setEditingEvent(null);
          setShowCreateDropdown(prev => !prev);
        }}
        style={{
          padding: "10px 16px",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          marginBottom: "1rem"
        }}
      >
        {showCreateDropdown || editingEvent ? "Close Form" : "Create New Event"}
      </button>

      {/* --- DROPDOWN CONTENT --- */}
      {showCreateDropdown || editingEvent ? (
        <div style={{
          marginBottom: "1.5rem",
          padding: "1rem",
          border: "1px solid #ccc",
          borderRadius: "6px",
          background: "#f9f9f9"
        }}>
          <EventForm event={editingEvent} onSave={handleSave} onCancel={handleCancel} />
        </div>
      ) : null}

      {registeringForEventId && (
        <div style={{
          marginTop: '2rem',
          marginBottom: '2rem',
          padding: '1rem',
          border: '1px solid #ccc',
          borderRadius: '4px'
        }}>
          <h3>Register for Event</h3>
          <RegistrationForm
            eventId={registeringForEventId}
            onSuccess={handleRegistrationSuccess}
            onCancel={() => setRegisteringForEventId(null)}
          />
        </div>
      )}

      <EventList
        events={events}
        onEventClick={handleEventClick}
        expandedEventId={expandedEventId}
        eventRegistrations={loadingRegistrations ? null : eventRegistrations}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onRegister={handleRegisterClick}
      />

      {loadingRegistrations && expandedEventId && (
        <div style={{ marginTop: '1rem', fontStyle: 'italic' }}>
          Loading registrations...
        </div>
      )}
    </div>
  );
}

export default Events;
