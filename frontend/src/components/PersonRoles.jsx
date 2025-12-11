import React, { useState, useEffect } from 'react';
import api from '../services/api';

function PersonRoles({ personId, onUpdate }) {
  const [roles, setRoles] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAddAttendee, setShowAddAttendee] = useState(false);
  const [guardian, setGuardian] = useState('');

  useEffect(() => {
    fetchRoles();
  }, [personId]);

  const fetchRoles = () => {
    setLoading(true);
    api.get(`/people/${personId}/roles`)
      .then(response => {
        setRoles(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching roles:', error);
        setLoading(false);
      });
  };

  const handleAddAttendee = (e) => {
    e.preventDefault();
    api.post(`/people/${personId}/attendee`, { guardian: guardian.trim() })
      .then(() => {
        setGuardian('');
        setShowAddAttendee(false);
        fetchRoles();
        if (onUpdate) onUpdate();
      })
      .catch(error => {
        console.error('Error adding attendee:', error);
        alert('Error: ' + (error.response?.data?.detail || error.message));
      });
  };

  const handleAddLeader = () => {
    api.post(`/people/${personId}/leader`)
      .then(() => {
        fetchRoles();
        if (onUpdate) onUpdate();
      })
      .catch(error => {
        console.error('Error adding leader:', error);
        alert('Error: ' + (error.response?.data?.detail || error.message));
      });
  };

  const handleAddVolunteer = () => {
    api.post(`/people/${personId}/volunteer`)
      .then(() => {
        fetchRoles();
        if (onUpdate) onUpdate();
      })
      .catch(error => {
        console.error('Error adding volunteer:', error);
        alert('Error: ' + (error.response?.data?.detail || error.message));
      });
  };

  const handleRemoveAttendee = () => {
    if (window.confirm('Are you sure you want to remove the Attendee role?')) {
      api.delete(`/attendees/${roles.attendee.id}`)
        .then(() => {
          fetchRoles();
          if (onUpdate) onUpdate();
        })
        .catch(error => {
          console.error('Error removing attendee:', error);
          alert('Error: ' + (error.response?.data?.detail || error.message));
        });
    }
  };

  const handleRemoveLeader = () => {
    if (window.confirm('Are you sure you want to remove the Leader role?')) {
      api.delete(`/leaders/${roles.leader.id}`)
        .then(() => {
          fetchRoles();
          if (onUpdate) onUpdate();
        })
        .catch(error => {
          console.error('Error removing leader:', error);
          alert('Error: ' + (error.response?.data?.detail || error.message));
        });
    }
  };

  const handleRemoveVolunteer = () => {
    if (window.confirm('Are you sure you want to remove the Volunteer role?')) {
      api.delete(`/volunteers/${roles.volunteer.id}`)
        .then(() => {
          fetchRoles();
          if (onUpdate) onUpdate();
        })
        .catch(error => {
          console.error('Error removing volunteer:', error);
          alert('Error: ' + (error.response?.data?.detail || error.message));
        });
    }
  };

  if (loading) return <div>Loading roles...</div>;
  if (!roles) return <div>Error loading roles</div>;

  return (
    <div style={{ marginTop: '1rem' }}>
      <h3>Roles</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Attendee Role */}
        <div style={{ padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <strong>Attendee</strong>
              {roles.attendee && (
                <div style={{ fontSize: '0.9em', color: '#666', marginTop: '0.25rem' }}>
                  Guardian: {roles.attendee.guardian}
                </div>
              )}
            </div>
            {roles.attendee ? (
              <button className="secondary outline" onClick={handleRemoveAttendee}>
                Remove
              </button>
            ) : (
              <button className="secondary" onClick={() => setShowAddAttendee(true)}>
                Add Attendee
              </button>
            )}
          </div>
          {showAddAttendee && !roles.attendee && (
            <form onSubmit={handleAddAttendee} style={{ marginTop: '0.5rem' }}>
              <input
                type="text"
                placeholder="Guardian name (required)"
                value={guardian}
                onChange={(e) => setGuardian(e.target.value)}
                required
                style={{ marginRight: '0.5rem' }}
              />
              <button type="submit">Add</button>
              <button type="button" className="secondary" onClick={() => setShowAddAttendee(false)}>
                Cancel
              </button>
            </form>
          )}
        </div>

        {/* Leader Role */}
        <div style={{ padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>Leader</strong>
            {roles.leader ? (
              <button className="secondary outline" onClick={handleRemoveLeader}>
                Remove
              </button>
            ) : (
              <button className="secondary" onClick={handleAddLeader}>
                Add Leader
              </button>
            )}
          </div>
        </div>

        {/* Volunteer Role */}
        <div style={{ padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong>Volunteer</strong>
            {roles.volunteer ? (
              <button className="secondary outline" onClick={handleRemoveVolunteer}>
                Remove
              </button>
            ) : (
              <button className="secondary" onClick={handleAddVolunteer}>
                Add Volunteer
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default PersonRoles;


