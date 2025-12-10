import React, { useState, useEffect } from 'react';
import PersonList from '../components/PersonList';
import PersonForm from '../components/PersonForm';
import api from '../services/api';

function People() {
  const [people, setPeople] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingPerson, setEditingPerson] = useState(null);

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
      // Update
      api.put(`/people/${person.id}`, person)
        .then(response => {
          setEditingPerson(null);
          fetchPeople();
        })
        .catch(error => setError(error));
    } else {
      // Create
      api.post('/people', person)
        .then(response => {
          fetchPeople();
        })
        .catch(error => setError(error));
    }
  };

  const handleEdit = (person) => {
    setEditingPerson(person);
  };

  const handleDelete = (personId) => {
    api.delete(`/people/${personId}`)
      .then(response => {
        fetchPeople();
      })
      .catch(error => setError(error));
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>People</h1>
      <PersonForm person={editingPerson} onSave={handleSave} />
      <PersonList people={people} onEdit={handleEdit} onDelete={handleDelete} />
    </div>
  );
}

export default People;
