import React, { useState, useEffect } from 'react';

function PersonForm({ person, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    age: '',
  });

  useEffect(() => {
    if (person) {
      setFormData({
        firstName: person.firstName || '',
        lastName: person.lastName || '',
        age: person.age !== null && person.age !== undefined ? person.age : '',
      });
    } else {
      setFormData({
        firstName: '',
        lastName: '',
        age: '',
      });
    }
  }, [person]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Prepare data for API - convert age to number or null
    const submitData = {
      firstName: formData.firstName.trim(),
      lastName: formData.lastName.trim(),
      age: formData.age === '' || formData.age === null ? null : parseInt(formData.age, 10),
    };
    
    // Include id only if editing
    if (person && person.id) {
      submitData.id = person.id;
    }
    
    onSave(submitData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid">
        <input
          type="text"
          name="firstName"
          placeholder="First Name"
          value={formData.firstName}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="lastName"
          placeholder="Last Name"
          value={formData.lastName}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="age"
          placeholder="Age"
          value={formData.age}
          onChange={handleChange}
          min="0"
        />
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
        <button type="submit">{person && person.id ? 'Update' : 'Add Person'}</button>
        {person && person.id && onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default PersonForm;
