import React, {useState, useEffect} from 'react';
import { graphqlRequest, mutations } from '../services/api';
import axios from 'axios';

// Note: Fetching leaders list is not yet available in GraphQL schema
// Using REST API as fallback until GraphQL query is added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function AddLeaderToGroup({groupId, onSuccess, onCancel}) {
    const [leaders, setLeaders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedLeaderId, setSelectedLeaderId] = useState('');

    useEffect(() => {
        // TODO: Replace with GraphQL query when leaders query is added to schema
        REST_API.get('/leaders')
            .then(response => {
                setLeaders(response.data || []);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching leaders:', error);
                setLoading(false);
            });
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedLeaderId) {
            alert('Please select a leader');
            return;
        }

        try {
            // Note: The GraphQL mutation expects leaderId (the Leader ID), not personId
            // We need to find the leader ID from the selected personId
            const leader = leaders.find(l => l.personId === parseInt(selectedLeaderId));
            if (!leader) {
                alert('Leader not found');
                return;
            }

            await graphqlRequest(mutations.addLeaderToGroup, {
                groupId,
                leaderId: leader.id
            });
            setSelectedLeaderId('');
            if (onSuccess) onSuccess();
        } catch (error) {
            console.error('Error adding leader:', error);
            alert('Error: ' + (error.response?.errors?.[0]?.message || error.message));
        }
    };

    if (loading) return <div>Loading leaders...</div>;

    return (
        <form onSubmit={handleSubmit}>
            <div className="grid">
                <label>
                    Select Leader to Add:
                    <select
                        value={selectedLeaderId}
                        onChange={(e) => setSelectedLeaderId(e.target.value)}
                        required
                    >
                        <option value="">Select a leader...</option>
                        {leaders.map((leader) => (
                            <option key={leader.id} value={leader.personId}>
                                {leader.firstName} {leader.lastName}
                            </option>
                        ))}
                    </select>
                </label>
            </div>
            <div style={{display: 'flex', gap: '0.5rem', marginTop: '0.5rem'}}>
                <button
                    type="submit"
                    style={{
                        padding: '0.35rem 0.7rem',    // smaller padding
                        fontSize: '0.85rem',          // smaller text
                        borderRadius: '6px',          // keeps the rounded look
                        cursor: 'pointer'
                    }}
                >
                    Add Leader
                </button>

                {onCancel && (
                    <button
                        type="button"
                        className="secondary"
                        onClick={onCancel}
                        style={{
                            padding: '0.35rem 0.7rem',   // match submit button
                            fontSize: '0.85rem',
                            borderRadius: '6px',
                            cursor: 'pointer'
                        }}
                    >
                        Cancel
                    </button>
                )}
            </div>
        </form>
    );
}

export default AddLeaderToGroup;

