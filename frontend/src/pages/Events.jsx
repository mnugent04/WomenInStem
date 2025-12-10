import React, { useState, useEffect } from 'react';
import EventList from '../components/EventList';
import EventForm from '../components/EventForm';
import RegistrationForm from '../components/RegistrationForm';
import api from '../services/api';

function Events() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedEventId, setExpandedEventId] = useState(null);
  const [eventRegistrations, setEventRegistrations] = useState(null);
  const [loadingRegistrations, setLoadingRegistrations] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [registeringForEventId, setRegisteringForEventId] = useState(null);

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
    // If clicking the same event, collapse it
    if (expandedEventId === eventId) {
      setExpandedEventId(null);
      setEventRegistrations(null);
      return;
    }

    // Expand the clicked event
    setExpandedEventId(eventId);
    setLoadingRegistrations(true);
    setEventRegistrations(null);

    try {
      const response = await api.get(`/events/${eventId}/registrations`);
      setEventRegistrations(response.data);
    } catch (error) {
      console.error('Error fetching event registrations:', error);
      setError(error);
    } finally {
      setLoadingRegistrations(false);
    }
  };

  const handleSave = (eventData) => {
    if (eventData.id) {
      // UPDATE
      const { id, ...updateData } = eventData; // remove id from the body

      api.patch(`/events/${id}`, updateData)
          .then(response => {
            setEditingEvent(null);
            fetchEvents();  // refresh the list
          })
          .catch(error => {
            console.error('Error updating event:', error);
            setError(error);
          });

    } else {
      // CREATE
      const { id, ...createData } = eventData;

      api.post('/events', createData)
          .then(response => {
            setEditingEvent(null);
            fetchEvents();
          })
          .catch(error => {
            console.error('Error creating event:', error);
            setError(error);
          });
    }
  };


  const handleCancel = () => {
    setEditingEvent(null);
  };

  const handleEdit = (event) => {
    setEditingEvent(event);
  };

  const handleDelete = (eventId) => {
    if (window.confirm('Are you sure you want to delete this event?')) {
      // Note: Backend doesn't have DELETE endpoint yet
      console.warn('Event delete not yet implemented in backend');
    }
  };

  const handleRegisterClick = (eventId) => {
    setRegisteringForEventId(eventId);
  };

  const handleRegistrationSuccess = () => {
    // Refresh registrations if the event is expanded
    if (expandedEventId) {
      handleEventClick(expandedEventId);
    }
    setRegisteringForEventId(null);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Events</h1>
      <EventForm event={editingEvent} onSave={handleSave} onCancel={handleCancel} />
      {registeringForEventId && (
        <div style={{ marginTop: '2rem', marginBottom: '2rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '4px' }}>
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
        <div style={{ marginTop: '1rem', fontStyle: 'italic' }}>Loading registrations...</div>
      )}
    </div>
  );
}

export default Events;
