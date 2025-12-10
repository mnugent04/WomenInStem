import React, { useState, useEffect } from 'react';

function EventForm({ event, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    dateTime: '',
    location: '',
    notes: '',
  });

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
        <input
          type="text"
          name="type"
          placeholder="Event Type"
          value={formData.type}
          onChange={handleChange}
          required
        />
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

