import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';

function Search() {
  const [searchResults, setSearchResults] = useState(null);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{
        padding: '1.25rem 1.5rem',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        backgroundColor: '#fff',
        boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
      }}>
        <h1 style={{ margin: 0, marginBottom: '0.5rem' }}>Search</h1>
        <p style={{ color: '#6b7280', marginBottom: '0.75rem', lineHeight: 1.5 }}>
          Search across events, people, roles (leader, attendee, volunteer), and event types.
        </p>
        <SearchBar onResults={setSearchResults} />
      </div>

      {searchResults && (
        <div style={{
          padding: '1.25rem 1.5rem',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          backgroundColor: '#fff',
          boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
        }}>
          <SearchResults results={searchResults} />
        </div>
      )}
    </div>
  );
}

export default Search;

