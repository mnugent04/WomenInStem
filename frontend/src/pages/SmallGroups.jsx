import React, { useState, useEffect } from 'react';
import SmallGroupList from '../components/SmallGroupList';
import api from '../services/api';

function SmallGroups() {
  const [smallGroups, setSmallGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedGroupId, setExpandedGroupId] = useState(null);
  const [groupDetails, setGroupDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    api.get('/smallgroups')
      .then(response => {
        setSmallGroups(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  }, []);

  const handleGroupClick = async (groupId) => {
    // If clicking the same group, collapse it
    if (expandedGroupId === groupId) {
      setExpandedGroupId(null);
      setGroupDetails(null);
      return;
    }

    // Expand the clicked group
    setExpandedGroupId(groupId);
    setLoadingDetails(true);
    setGroupDetails(null);

    try {
      // Fetch both members and leaders in parallel
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

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Small Groups</h1>
      <SmallGroupList 
        smallGroups={smallGroups} 
        onGroupClick={handleGroupClick}
        expandedGroupId={expandedGroupId}
        groupDetails={loadingDetails ? null : groupDetails}
      />
      {loadingDetails && expandedGroupId && (
        <div style={{ marginTop: '1rem', fontStyle: 'italic' }}>Loading group details...</div>
      )}
    </div>
  );
}

export default SmallGroups;
