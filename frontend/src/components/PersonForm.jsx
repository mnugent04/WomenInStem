import React, { useState, useEffect } from 'react';

function PersonForm({ person, onSave }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    age: '',
  });

  useEffect(() => {
    if (person) {
      setFormData(person);
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
    onSave(formData);
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
        />
      </div>
      <button type="submit">Save</button>
    </form>
  );
}

export default PersonForm;
