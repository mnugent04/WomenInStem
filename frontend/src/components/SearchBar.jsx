import React, { useState } from 'react';
import api from '../services/api';

function SearchBar({ onResults }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await api.get('/search', {
        params: { query: query.trim() }
      });
      if (onResults) {
        onResults(response.data);
      }
    } catch (error) {
      console.error('Search error:', error);
      alert('Error performing search: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSearch} style={{ marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search events, people, roles (leader, attendee, volunteer), event types..."
          style={{
            flex: 1,
            padding: '0.9rem 1rem',
            fontSize: '1rem',
            border: '1px solid #d1d5db',
            borderRadius: '6px',
            backgroundColor: '#fff',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '0.9rem 1.5rem',
            backgroundColor: loading ? '#93c5fd' : '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            minWidth: '120px',
            boxShadow: '0 1px 2px rgba(0,0,0,0.08)'
          }}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </form>
  );
}

export default SearchBar;

