import React, { useState, useEffect } from 'react';
import api from '../services/api';

function PersonParentContacts({ personId }) {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newContact, setNewContact] = useState({ summary: '', method: '', date: '' });

  useEffect(() => {
    fetchContacts();
  }, [personId]);

  const fetchContacts = () => {
    setLoading(true);
    api.get(`/persons/${personId}/parent-contacts`)
      .then(response => {
        setContacts(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching parent contacts:', error);
        setLoading(false);
      });
  };

  const handleAddContact = (e) => {
    e.preventDefault();
    api.post(`/persons/${personId}/parent-contacts`, {
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
      api.delete(`/parent-contacts/${contactId}`)
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
        <button className="secondary" onClick={() => setShowAddForm(!showAddForm)}>
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
          <button type="submit" style={{ marginTop: '0.5rem' }}>Add Contact</button>
        </form>
      )}

      {contacts.length > 0 ? (
        <ul>
          {contacts.map((contact) => (
            <li key={contact._id} style={{ marginBottom: '1rem', padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
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
                <button 
                  className="secondary outline" 
                  onClick={() => handleDeleteContact(contact._id)}
                  style={{ marginLeft: '1rem' }}
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

