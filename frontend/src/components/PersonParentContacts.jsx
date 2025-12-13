import React, { useState, useEffect } from 'react';
import { graphqlRequest, queries } from '../services/api';
import axios from 'axios';

// Note: Add/delete parent contact operations are not yet available in GraphQL schema
// Using REST API as fallback until GraphQL mutations are added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function PersonParentContacts({ personId }) {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newContact, setNewContact] = useState({ summary: '', method: '', date: '' });

  // 🎯 DEFINING THE CONSISTENT SMALL BUTTON STYLE
  const smallButtonStyle = {
    padding: '0.25rem 0.5rem',
    fontSize: '0.75rem',
    width: '6rem', // Consistent width for uniformity
    height: '1.75rem',
    textAlign: 'center',
    flexShrink: 0
  };

  // 🎯 DEFINING THE STYLE FOR SMALL FORM BUTTONS (like the secondary 'Cancel' button)
  const smallSecondaryButtonStyle = {
    ...smallButtonStyle,
    marginLeft: '0.5rem' // Adds a small gap next to the primary button
  };

  useEffect(() => {
    fetchContacts();
  }, [personId]);

  const fetchContacts = async () => {
    setLoading(true);
    try {
      const data = await graphqlRequest(queries.getParentContacts, { personId });
      setContacts(data.parentContacts || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching parent contacts:', error);
      setLoading(false);
    }
  };

  const handleAddContact = (e) => {
    e.preventDefault();
    // TODO: Replace with GraphQL mutation when addParentContact is added to schema
    REST_API.post(`/persons/${personId}/parent-contacts`, {
      summary: newContact.summary,
      method: newContact.method || undefined,
      date: newContact.date || undefined,
      createdBy: 1, // In a real app, this would come from auth context
    })
        .then(() => {
          setNewContact({ summary: '', method: '', date: '' });
          setShowAddForm(false);
          fetchContacts();
        })
        .catch(error => {
          console.error('Error adding contact:', error);
          alert('Error adding contact: ' + (error.response?.data?.detail || error.message));
        });
  };

  const handleDeleteContact = (contactId) => {
    if (window.confirm('Are you sure you want to delete this contact record?')) {
      // TODO: Replace with GraphQL mutation when deleteParentContact is added to schema
      REST_API.delete(`/parent-contacts/${contactId}`)
          .then(() => {
            fetchContacts();
          })
          .catch(error => {
            console.error('Error deleting contact:', error);
            alert('Error deleting contact');
          });
    }
  };

  if (loading) return <div>Loading contacts...</div>;

  return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3>Parent Contacts</h3>
          {/* 1. TOP ADD/CANCEL BUTTON */}
          <button
              className="secondary"
              onClick={() => setShowAddForm(!showAddForm)}
              style={smallButtonStyle} // 🎯 Applied Consistent Style
          >
            {showAddForm ? 'Cancel' : 'Add Contact'}
          </button>
        </div>

        {showAddForm && (
            <form onSubmit={handleAddContact} style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '4px' }}>
              <div className="grid">
            <textarea
                placeholder="Contact summary"
                value={newContact.summary}
                onChange={(e) => setNewContact({ ...newContact, summary: e.target.value })}
                required
                rows="3"
            />
                <input
                    type="text"
                    placeholder="Method (phone, email, etc.)"
                    value={newContact.method}
                    onChange={(e) => setNewContact({ ...newContact, method: e.target.value })}
                />
                <input
                    type="date"
                    placeholder="Date"
                    value={newContact.date}
                    onChange={(e) => setNewContact({ ...newContact, date: e.target.value })}
                />
              </div>
              {/* 2. FORM SUBMIT BUTTON */}
              <button type="submit" style={{ ...smallButtonStyle, marginTop: '0.5rem' }}>
                Add Contact
              </button>

              {/* 3. FORM CANCEL BUTTON (if you decide to add one later) */}
              {/* The top button acts as cancel, so we'll leave this form simple for now */}

            </form>
        )}

        {contacts.length > 0 ? (
            <ul>
              {contacts.map((contact) => (
                  <li key={contact.id} style={{ marginBottom: '1rem', padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div style={{ flex: 1 }}>
                        <p><strong>{contact.summary}</strong></p>
                        {contact.method && (
                            <p style={{ fontSize: '0.9em', color: '#666' }}>Method: {contact.method}</p>
                        )}
                        {contact.date && (
                            <p style={{ fontSize: '0.9em', color: '#666' }}>Date: {new Date(contact.date).toLocaleDateString()}</p>
                        )}
                        {contact.created && (
                            <div style={{ fontSize: '0.8em', color: '#999', marginTop: '0.5rem' }}>
                              Recorded: {new Date(contact.created).toLocaleString()}
                            </div>
                        )}
                      </div>
                      {/* 4. DELETE BUTTON (already small, but let's ensure it's fully consistent) */}
                      <button
                          className="secondary outline"
                          onClick={() => handleDeleteContact(contact.id)}
                          style={smallSecondaryButtonStyle} // 🎯 Applied Consistent Style (using the smallSecondary style)
                      >
                        Delete
                      </button>
                    </div>
                  </li>
              ))}
            </ul>
        ) : (
            <p style={{ fontStyle: 'italic', color: '#666' }}>No parent contacts recorded yet.</p>
        )}
      </div>
  );
}

export default PersonParentContacts;