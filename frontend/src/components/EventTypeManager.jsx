import React, { useState, useEffect } from 'react';
import api from '../services/api';

function EventTypeManager() {
  const [eventTypes, setEventTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingType, setEditingType] = useState(null);
  const [formData, setFormData] = useState({
    event_type: '',
    description: '',
    required_items: '',
    duration_minutes: '',
    extra_notes: ''
  });

  const fetchEventTypes = () => {
    setLoading(true);
    api.get('/event-types')
      .then(response => {
        setEventTypes(response.data || []);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching event types:', error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchEventTypes();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      event_type: formData.event_type,
      description: formData.description || undefined,
      required_items: formData.required_items ? formData.required_items.split(',').map(s => s.trim()) : undefined,
      duration_minutes: formData.duration_minutes ? parseInt(formData.duration_minutes) : undefined,
      extra_notes: formData.extra_notes || undefined
    };

    if (editingType) {
      // Update
      api.patch(`/event-types/${editingType.event_type}`, data)
        .then(() => {
          setShowForm(false);
          setEditingType(null);
          resetForm();
          fetchEventTypes();
        })
        .catch(error => {
          alert('Error updating event type: ' + (error.response?.data?.detail || error.message));
        });
    } else {
      // Create
      api.post('/event-types', data)
        .then(() => {
          setShowForm(false);
          resetForm();
          fetchEventTypes();
        })
        .catch(error => {
          alert('Error creating event type: ' + (error.response?.data?.detail || error.message));
        });
    }
  };

  const handleEdit = (eventType) => {
    setEditingType(eventType);
    setFormData({
      event_type: eventType.event_type,
      description: eventType.description || '',
      required_items: Array.isArray(eventType.required_items) ? eventType.required_items.join(', ') : '',
      duration_minutes: eventType.duration_minutes || '',
      extra_notes: eventType.extra_notes || ''
    });
    setShowForm(true);
  };

  const handleDelete = (eventType) => {
    if (window.confirm(`Delete event type "${eventType.event_type}"?`)) {
      api.delete(`/event-types/${eventType.event_type}`)
        .then(() => {
          fetchEventTypes();
        })
        .catch(error => {
          alert('Error deleting event type: ' + (error.response?.data?.detail || error.message));
        });
    }
  };

  const resetForm = () => {
    setFormData({
      event_type: '',
      description: '',
      required_items: '',
      duration_minutes: '',
      extra_notes: ''
    });
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingType(null);
    resetForm();
  };

  if (loading) return <div>Loading event types...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3>Event Types (MongoDB)</h3>
        <button 
          className="secondary" 
          onClick={() => setShowForm(!showForm)}
          style={{
            backgroundColor: '#2563eb',
            color: 'white',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {showForm ? 'Cancel' : 'Add Event Type'}
        </button>
      </div>

      {showForm && (
        <div style={{
          marginBottom: '2rem',
          padding: '1rem',
          border: '1px solid #ccc',
          borderRadius: '4px',
          backgroundColor: '#fafafa'
        }}>
          <h4>{editingType ? 'Edit' : 'Create'} Event Type</h4>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label>
                Event Type Name (required):
                <input
                  type="text"
                  value={formData.event_type}
                  onChange={(e) => setFormData({...formData, event_type: e.target.value})}
                  required
                  disabled={!!editingType}
                  style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                />
              </label>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label>
                Description:
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem', minHeight: '60px' }}
                />
              </label>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label>
                Required Items (comma-separated):
                <input
                  type="text"
                  value={formData.required_items}
                  onChange={(e) => setFormData({...formData, required_items: e.target.value})}
                  placeholder="Bible, Journal, Pen"
                  style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                />
              </label>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label>
                Duration (minutes):
                <input
                  type="number"
                  value={formData.duration_minutes}
                  onChange={(e) => setFormData({...formData, duration_minutes: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
                />
              </label>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label>
                Extra Notes:
                <textarea
                  value={formData.extra_notes}
                  onChange={(e) => setFormData({...formData, extra_notes: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem', minHeight: '60px' }}
                />
              </label>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button type="submit">{editingType ? 'Update' : 'Create'}</button>
              <button type="button" className="secondary" onClick={handleCancel}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      <div style={{ display: 'grid', gap: '1rem' }}>
        {eventTypes.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>No event types found. Create one above!</p>
        ) : (
          eventTypes.map((et) => (
            <div key={et._id} style={{
              border: '1px solid #e5e7eb',
              borderRadius: '4px',
              padding: '1rem',
              backgroundColor: '#f0f9ff'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                <div>
                  <strong style={{ fontSize: '1.1rem', color: '#2563eb' }}>{et.event_type}</strong>
                  {et.duration_minutes && (
                    <span style={{ marginLeft: '0.5rem', color: '#666', fontSize: '0.9rem' }}>
                      ({et.duration_minutes} minutes)
                    </span>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="secondary" onClick={() => handleEdit(et)}>Edit</button>
                  <button className="secondary outline" onClick={() => handleDelete(et)}>Delete</button>
                </div>
              </div>
              {et.description && (
                <p style={{ marginTop: '0.5rem', color: '#666' }}>{et.description}</p>
              )}
              {et.required_items && Array.isArray(et.required_items) && et.required_items.length > 0 && (
                <div style={{ marginTop: '0.5rem' }}>
                  <strong>Required Items:</strong> {et.required_items.join(', ')}
                </div>
              )}
              {et.extra_notes && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
                  <strong>Notes:</strong> {et.extra_notes}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default EventTypeManager;

