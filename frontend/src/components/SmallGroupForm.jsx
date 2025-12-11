import React, { useState } from 'react';

function SmallGroupForm({ onSave, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Group name is required');
      return;
    }
    onSave({ name: formData.name.trim() });
    setFormData({ name: '' });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid">
        <input
          type="text"
          name="name"
          placeholder="Small Group Name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
        <button type="submit">Create Small Group</button>
        {onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

export default SmallGroupForm;

