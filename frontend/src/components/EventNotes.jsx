import React, { useState, useEffect } from 'react';
import { graphqlRequest, queries } from '../services/api';
import axios from 'axios';

// Note: Add/delete event note operations are not yet available in GraphQL schema
// Using REST API as fallback until GraphQL mutations are added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function EventNotes({ eventId }) {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newNote, setNewNote] = useState({ notes: '', concerns: '', studentWins: '' });

  useEffect(() => {
    fetchNotes();
  }, [eventId]);

  const fetchNotes = async () => {
    setLoading(true);
    try {
      const data = await graphqlRequest(queries.getEventNotes, { eventId });
      setNotes(data.eventNotes || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching event notes:', error);
      setLoading(false);
    }
  };

  const handleAddNote = (e) => {
    e.preventDefault();
    // TODO: Replace with GraphQL mutation when addEventNote is added to schema
    REST_API.post(`/events/${eventId}/notes`, {
      notes: newNote.notes || undefined,
      concerns: newNote.concerns || undefined,
      studentWins: newNote.studentWins || undefined,
      createdBy: 1, // In a real app, this would come from auth context
    })
      .then(() => {
        setNewNote({ notes: '', concerns: '', studentWins: '' });
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
      // TODO: Replace with GraphQL mutation when deleteEventNote is added to schema
      REST_API.delete(`/notes/${noteId}`)
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
    <div style={{ marginTop: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h4>Event Notes & Highlights</h4>
        <button className="secondary" onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'Cancel' : 'Add Note'}
        </button>
      </div>
      
      {showAddForm && (
        <form onSubmit={handleAddNote} style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '4px' }}>
          <div className="grid">
            <textarea
              placeholder="Notes/Highlights"
              value={newNote.notes}
              onChange={(e) => setNewNote({ ...newNote, notes: e.target.value })}
              rows="3"
            />
            <textarea
              placeholder="Concerns (optional)"
              value={newNote.concerns}
              onChange={(e) => setNewNote({ ...newNote, concerns: e.target.value })}
              rows="2"
            />
            <textarea
              placeholder="Student Wins (optional)"
              value={newNote.studentWins}
              onChange={(e) => setNewNote({ ...newNote, studentWins: e.target.value })}
              rows="2"
            />
          </div>
          <button type="submit" style={{ marginTop: '0.5rem' }}>Add Note</button>
        </form>
      )}

      {notes.length > 0 ? (
        <ul>
          {notes.map((note) => (
            <li key={note.id} style={{ marginBottom: '1rem', padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div style={{ flex: 1 }}>
                  {note.notes && (
                    <p><strong>Notes:</strong> {note.notes}</p>
                  )}
                  {note.concerns && (
                    <p style={{ color: '#d32f2f' }}><strong>Concerns:</strong> {note.concerns}</p>
                  )}
                  {note.studentWins && (
                    <p style={{ color: '#2e7d32' }}><strong>Student Wins:</strong> {note.studentWins}</p>
                  )}
                  {note.created && (
                    <div style={{ fontSize: '0.8em', color: '#999', marginTop: '0.5rem' }}>
                      Created: {new Date(note.created).toLocaleString()}
                    </div>
                  )}
                </div>
                <button 
                  className="secondary outline" 
                  onClick={() => handleDeleteNote(note.id)}
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

export default EventNotes;


