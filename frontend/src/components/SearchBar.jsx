import React, {useState} from 'react';
import axios from 'axios';

// Note: Search operation is not yet available in GraphQL schema
// Using REST API as fallback until GraphQL query is added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function SearchBar({onResults}) {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            // TODO: Replace with GraphQL query when search is added to schema
            const response = await REST_API.get('/search', {
                params: {query: query.trim()}
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
        <form onSubmit={handleSearch} style={{marginBottom: '1.5rem'}}>
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search events, people, roles (leader, attendee, volunteer), event types..."
                style={{
                    // **--- START: Input Improvements ---**
                    flex: 1, // Ensures the input takes up the remaining space (keeps it wide)
                    padding: '1rem 1.25rem', // INCREASED: Taller and slightly wider input area
                    fontSize: '1.1rem', // INCREASED: Larger font size for better visibility
                    border: '2px solid #3b82f6', // CHANGE: Prominent, colored border
                    borderRadius: '8px', // Slightly larger border radius
                    backgroundColor: '#f9fafb', // Light background for better contrast
                    outline: 'none',
                    boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.1)', // ADDED: Subtle intuitive glow
                    transition: 'all 0.2s',
                    // **--- END: Input Improvements ---**
                }}
            />
            <div style={{display: 'flex', gap: '0.75rem', alignItems: 'center'}}>
                <button
                    type="submit"
                    disabled={loading}
                    style={{
                        // The button styles are solid, but ensure padding matches the new input height
                        padding: '1rem 1.5rem', // ADJUSTED: Matches the new input padding for alignment
                        backgroundColor: loading ? '#93c5fd' : '#2563eb',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px', // Matching border radius
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontSize: '1rem',
                        minWidth: '120px',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.1)' // Slightly stronger shadow for the button
                    }}
                >
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </div>
        </form>
    );
}

export default SearchBar;