import React, { useState, useEffect } from 'react';
import PersonList from '../components/PersonList';
import PersonForm from '../components/PersonForm';
import PersonNotes from '../components/PersonNotes';
import PersonParentContacts from '../components/PersonParentContacts';
import api from '../services/api';

function People() {
  const [people, setPeople] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingPerson, setEditingPerson] = useState(null);
  const [viewingPerson, setViewingPerson] = useState(null);

  const fetchPeople = () => {
    setLoading(true);
    api.get('/people')
      .then(response => {
        setPeople(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchPeople();
  }, []);

  const handleSave = (person) => {
    if (person.id) {
      // Update - don't send id in body, it's in the URL
      const { id, ...updateData } = person;
      api.put(`/people/${person.id}`, updateData)
        .then(response => {
          setEditingPerson(null);
          fetchPeople();
        })
        .catch(error => {
          console.error('Error updating person:', error);
          setError(error);
        });
    } else {
      // Create - don't send id
      const { id, ...createData } = person;
      api.post('/people', createData)
        .then(response => {
          setEditingPerson(null);
          fetchPeople();
        })
        .catch(error => {
          console.error('Error creating person:', error);
          setError(error);
        });
    }
  };

  const handleCancel = () => {
    setEditingPerson(null);
  };

  const handleEdit = (person) => {
    setEditingPerson(person);
  };

  const handleDelete = (personId) => {
    if (window.confirm('Are you sure you want to delete this person?')) {
      api.delete(`/people/${personId}`)
        .then(response => {
          fetchPeople();
          if (viewingPerson && viewingPerson.id === personId) {
            setViewingPerson(null);
          }
        })
        .catch(error => setError(error));
    }
  };

  const handleView = (person) => {
    setViewingPerson(person);
    setEditingPerson(null);
  };

  const handleCloseView = () => {
    setViewingPerson(null);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>People</h1>
      {viewingPerson ? (
        <article>
          <header>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2>{viewingPerson.firstName} {viewingPerson.lastName}</h2>
              <button className="secondary" onClick={handleCloseView}>Close</button>
            </div>
            <p>Age: {viewingPerson.age || 'N/A'}</p>
          </header>
          <PersonNotes personId={viewingPerson.id} />
          <PersonParentContacts personId={viewingPerson.id} />
        </article>
      ) : (
        <>
          <PersonForm person={editingPerson} onSave={handleSave} onCancel={handleCancel} />
          <PersonList 
            people={people} 
            onEdit={handleEdit} 
            onDelete={handleDelete}
            onView={handleView}
          />
        </>
      )}
    </div>
  );
}

export default People;
