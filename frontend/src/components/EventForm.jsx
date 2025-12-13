import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Note: Event type operations are not yet available in GraphQL schema
// Using REST API as fallback until GraphQL query is added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function EventForm({ event, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    dateTime: '',
    location: '',
    notes: '',
  });
  const [eventTypes, setEventTypes] = useState([]);
  const [loadingTypes, setLoadingTypes] = useState(true);

  useEffect(() => {
    // TODO: Replace with GraphQL query when eventTypes query is added to schema
    REST_API.get('/event-types')
      .then(response => {
        setEventTypes(response.data || []);
        setLoadingTypes(false);
      })
      .catch(error => {
        console.error('Error fetching event types:', error);
        setLoadingTypes(false);
      });
  }, []);

  useEffect(() => {
    if (event) {
      // Format datetime for input field (YYYY-MM-DDTHH:mm)
      const dateTime = event.dateTime ? new Date(event.dateTime).toISOString().slice(0, 16) : '';
      setFormData({
        name: event.name || '',
        type: event.type || '',
        dateTime: dateTime,
        location: event.location || '',
        notes: event.notes || '',
      });
    } else {
      setFormData({
        name: '',
        type: '',
        dateTime: '',
        location: '',
        notes: '',
      });
    }
  }, [event]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = {
      name: formData.name.trim(),
      type: formData.type.trim(),
      dateTime: formData.dateTime || new Date().toISOString(),
      location: formData.location.trim(),
      notes: formData.notes.trim() || null,
    };
    
    if (event && event.id) {
      submitData.id = event.id;
    }
    
    onSave(submitData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid">
        <input
          type="text"
          name="name"
          placeholder="Event Name"
          value={formData.name}
          onChange={handleChange}
          required
        />
        <select
          name="type"
          value={formData.type}
          onChange={handleChange}
          required
          style={{
            padding: '0.5rem',
            borderRadius: '4px',
            border: '1px solid #ccc',
            fontSize: '1rem'
          }}
        >
          <option value="">Select Event Type</option>
          {eventTypes.map((eventType) => (
            <option key={eventType.event_type} value={eventType.event_type}>
              {eventType.event_type}
            </option>
          ))}
          {/* Show current type if it's not in the list (for editing old events) */}
          {formData.type && !eventTypes.some(et => et.event_type === formData.type) && (
            <option value={formData.type}>{formData.type} (not in list)</option>
          )}
        </select>
        <input
          type="datetime-local"
          name="dateTime"
          placeholder="Date & Time"
          value={formData.dateTime}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="location"
          placeholder="Location"
          value={formData.location}
          onChange={handleChange}
          required
        />
        <textarea
          name="notes"
          placeholder="Notes (optional)"
          value={formData.notes}
          onChange={handleChange}
          rows="3"
        />
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
        <button type="submit">{event && event.id ? 'Update Event' : 'Create Event'}</button>
        {event && event.id && onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default EventForm;


