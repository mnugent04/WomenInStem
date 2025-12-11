import React, { useState, useEffect } from 'react';
import api from '../services/api';

function PersonNotes({ personId }) {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newNote, setNewNote] = useState({ text: '', category: '' });

  useEffect(() => {
    fetchNotes();
  }, [personId]);

  const fetchNotes = () => {
    setLoading(true);
    api.get(`/persons/${personId}/notes`)
      .then(response => {
        setNotes(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching notes:', error);
        setLoading(false);
      });
  };

  const handleAddNote = (e) => {
    e.preventDefault();
    api.post(`/persons/${personId}/notes`, {
      text: newNote.text,
      category: newNote.category || undefined,
      createdBy: 1, // In a real app, this would come from auth context
    })
      .then(() => {
        setNewNote({ text: '', category: '' });
        setShowAddForm(false);
        fetchNotes();
      })
      .catch(error => {
        console.error('Error adding note:', error);
        alert('Error adding note: ' + (error.response?.data?.detail || error.message));
      });
  };

  const handleDeleteNote = (noteId) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      api.delete(`/notes/${noteId}`)
        .then(() => {
          fetchNotes();
        })
        .catch(error => {
          console.error('Error deleting note:', error);
          alert('Error deleting note');
        });
    }
  };

  if (loading) return <div>Loading notes...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3>Notes</h3>
        <button className="secondary" onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'Cancel' : 'Add Note'}
        </button>
      </div>
      
      {showAddForm && (
        <form onSubmit={handleAddNote} style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '4px' }}>
          <div className="grid">
            <textarea
              placeholder="Note text"
              value={newNote.text}
              onChange={(e) => setNewNote({ ...newNote, text: e.target.value })}
              required
              rows="3"
            />
            <input
              type="text"
              placeholder="Category (optional)"
              value={newNote.category}
              onChange={(e) => setNewNote({ ...newNote, category: e.target.value })}
            />
          </div>
          <button type="submit" style={{ marginTop: '0.5rem' }}>Add Note</button>
        </form>
      )}

      {notes.length > 0 ? (
        <ul>
          {notes.map((note) => (
            <li key={note._id} style={{ marginBottom: '1rem', padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ flex: 1 }}>
                  <p>{note.text}</p>
                  {note.category && (
                    <span style={{ fontSize: '0.9em', color: '#666' }}>Category: {note.category}</span>
                  )}
                  {note.created && (
                    <div style={{ fontSize: '0.8em', color: '#999', marginTop: '0.5rem' }}>
                      Created: {new Date(note.created).toLocaleString()}
                    </div>
                  )}
                </div>
                <button 
                  className="secondary"
                  onClick={() => handleDeleteNote(note._id)}
                  style={{ marginLeft: '1rem' }}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ fontStyle: 'italic', color: '#666' }}>No notes yet.</p>
      )}
    </div>
  );
}

export default PersonNotes;


