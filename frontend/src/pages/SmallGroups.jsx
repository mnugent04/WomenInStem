import React, { useState, useEffect } from 'react';
import SmallGroupList from '../components/SmallGroupList';
import api from '../services/api';

function SmallGroups() {
  const [smallGroups, setSmallGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Small Groups</h1>
      <SmallGroupList smallGroups={smallGroups} />
    </div>
  );
}

export default SmallGroups;
