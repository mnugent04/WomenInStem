import React, {useState, useEffect} from 'react';
import SmallGroupList from '../components/SmallGroupList';
import SmallGroupForm from '../components/SmallGroupForm';
import AddMemberToGroup from '../components/AddMemberToGroup';
import AddLeaderToGroup from '../components/AddLeaderToGroup';
import api from '../services/api';

function SmallGroups() {
    const [smallGroups, setSmallGroups] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedGroupId, setExpandedGroupId] = useState(null);
    const [groupDetails, setGroupDetails] = useState(null);
    const [loadingDetails, setLoadingDetails] = useState(false);
    const [showAddMember, setShowAddMember] = useState(null);
    const [showAddLeader, setShowAddLeader] = useState(null);
    const [showCreateForm, setShowCreateForm] = useState(false);

    const fetchGroups = () => {
        setLoading(true);
        api.get('/smallgroups')
            .then(response => {
                setSmallGroups(response.data);
                setLoading(false);
            })
            .catch(error => {
                setError(error);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchGroups();
    }, []);

    const handleGroupClick = async (groupId) => {
        if (expandedGroupId === groupId) {
            setExpandedGroupId(null);
            setGroupDetails(null);
            setShowAddMember(null);
            setShowAddLeader(null);
            return;
        }

        setExpandedGroupId(groupId);
        setLoadingDetails(true);
        setGroupDetails(null);

        try {
            const [membersResponse, leadersResponse] = await Promise.all([
                api.get(`/smallgroups/${groupId}/members`),
                api.get(`/smallgroups/${groupId}/leaders`)
            ]);

            setGroupDetails({
                members: membersResponse.data,
                leaders: leadersResponse.data
            });
        } catch (error) {
            console.error('Error fetching group details:', error);
            setError(error);
        } finally {
            setLoadingDetails(false);
        }
    };

    const handleCreateGroup = (groupData) => {
        api.post('/smallgroups', groupData)
            .then(() => {
                setShowCreateForm(false);
                fetchGroups();
            })
            .catch(error => {
                console.error('Error creating group:', error);
                alert('Error: ' + (error.response?.data?.detail || error.message));
            });
    };

    const handleDeleteGroup = (groupId) => {
        if (window.confirm('Are you sure you want to delete this small group? This will remove all members and leaders.')) {
            api.delete(`/smallgroups/${groupId}`)
                .then(() => {
                    if (expandedGroupId === groupId) {
                        setExpandedGroupId(null);
                        setGroupDetails(null);
                    }
                    fetchGroups();
                })
                .catch(error => {
                    console.error('Error deleting group:', error);
                    alert('Error: ' + (error.response?.data?.detail || error.message));
                });
        }
    };

    const handleAddMemberClick = (groupId) => {
        // Toggle: if already showing for this group, hide it; otherwise show it
        if (showAddMember === groupId) {
            setShowAddMember(null);
        } else {
            setShowAddMember(groupId);
            setShowAddLeader(null);
        }
    };

    const handleAddLeaderClick = (groupId) => {
        // Toggle: if already showing for this group, hide it; otherwise show it
        if (showAddLeader === groupId) {
            setShowAddLeader(null);
        } else {
            setShowAddLeader(groupId);
            setShowAddMember(null);
        }
    };

    const handleMemberSuccess = () => {
        setShowAddMember(null);
        // Refresh group details
        if (expandedGroupId) {
            handleGroupClick(expandedGroupId);
        }
    };

    const handleLeaderSuccess = () => {
        setShowAddLeader(null);
        // Refresh group details
        if (expandedGroupId) {
            handleGroupClick(expandedGroupId);
        }
    };

    const handleRemoveMember = (groupId, memberId) => {
        if (window.confirm('Remove this member from the group?')) {
            api.delete(`/smallgroups/${groupId}/members/${memberId}`)
                .then(() => {
                    // Refresh group details
                    handleGroupClick(groupId);
                })
                .catch(error => {
                    console.error('Error removing member:', error);
                    alert('Error: ' + (error.response?.data?.detail || error.message));
                });
        }
    };

    const handleRemoveLeader = (groupId, leaderId) => {
        if (window.confirm('Remove this leader from the group?')) {
            api.delete(`/smallgroups/${groupId}/leaders/${leaderId}`)
                .then(() => {
                    // Refresh group details
                    handleGroupClick(groupId);
                })
                .catch(error => {
                    console.error('Error removing leader:', error);
                    alert('Error: ' + (error.response?.data?.detail || error.message));
                });
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <div>
            <h1>Small Groups</h1>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>

                <button onClick={() => setShowCreateForm(!showCreateForm)}
                        style={{
                            padding: "10px 16px",
                            color: "white",
                            border: "none",
                            borderRadius: "6px",
                            cursor: "pointer",
                            marginBottom: "1rem"
                        }}>
                    {showCreateForm ? 'Cancel' : 'Create New Group'}
                </button>
            </div>

            {showCreateForm && (
                <div style={{
                    marginBottom: "2rem",
                    padding: "1rem",
                    border: "1px solid #ccc",
                    borderRadius: "6px",
                    backgroundColor: "#fafafa"
                }}>
                    <h3>Create New Small Group</h3>
                    <SmallGroupForm
                        onSave={handleCreateGroup}
                        onCancel={() => setShowCreateForm(false)}
                    />
                </div>
            )}

            <SmallGroupList
                smallGroups={smallGroups}
                onGroupClick={handleGroupClick}
                expandedGroupId={expandedGroupId}
                groupDetails={loadingDetails ? null : groupDetails}
                onDelete={handleDeleteGroup}
                onAddMember={handleAddMemberClick}
                onAddLeader={handleAddLeaderClick}
                onRemoveMember={handleRemoveMember}
                onRemoveLeader={handleRemoveLeader}
                showAddMemberForm={showAddMember}
                showAddLeaderForm={showAddLeader}
                onMemberSuccess={handleMemberSuccess}
                onLeaderSuccess={handleLeaderSuccess}
            />

            {loadingDetails && expandedGroupId && (
                <div style={{marginTop: '1rem', fontStyle: 'italic'}}>
                    Loading group details...
                </div>
            )}
        </div>
    );
}

export default SmallGroups;
