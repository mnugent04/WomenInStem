import React, {useState, useEffect} from 'react';
import api from '../services/api';

function AddLeaderToGroup({groupId, onSuccess, onCancel}) {
    const [leaders, setLeaders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedLeaderId, setSelectedLeaderId] = useState('');

    useEffect(() => {
        api.get('/leaders')
            .then(response => {
                setLeaders(response.data || []);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching leaders:', error);
                setLoading(false);
            });
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!selectedLeaderId) {
            alert('Please select a leader');
            return;
        }

        api.post(`/smallgroups/${groupId}/leaders`, {
            leaderID: parseInt(selectedLeaderId)
        })
            .then(() => {
                setSelectedLeaderId('');
                if (onSuccess) onSuccess();
            })
            .catch(error => {
                console.error('Error adding leader:', error);
                alert('Error: ' + (error.response?.data?.detail || error.message));
            });
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

