import React, { useState } from 'react';

function SmallGroupList({ smallGroups, onGroupClick, expandedGroupId, groupDetails }) {
  return (
    <figure>
      <table role="grid">
        <thead>
          <tr>
            <th scope="col">Name</th>
          </tr>
        </thead>
        <tbody>
          {smallGroups.map((group) => (
            <React.Fragment key={group.id}>
              <tr>
                <td>
                  <button
                    onClick={() => onGroupClick(group.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'inherit',
                      cursor: 'pointer',
                      textDecoration: 'underline',
                      padding: 0,
                      font: 'inherit',
                    }}
                  >
                    {group.name}
                    {expandedGroupId === group.id ? ' ▼' : ' ▶'}
                  </button>
                </td>
              </tr>
              {expandedGroupId === group.id && groupDetails && (
                <tr>
                  <td colSpan="1" style={{ paddingLeft: '2rem', paddingTop: '1rem', paddingBottom: '1rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {groupDetails.leaders && groupDetails.leaders.length > 0 && (
                        <div>
                          <strong>Leaders:</strong>
                          <ul style={{ marginTop: '0.5rem', marginBottom: 0 }}>
                            {groupDetails.leaders.map((leader) => (
                              <li key={leader.ID}>
                                {leader.FirstName} {leader.LastName}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {groupDetails.members && groupDetails.members.length > 0 && (
                        <div>
                          <strong>Members:</strong>
                          <ul style={{ marginTop: '0.5rem', marginBottom: 0 }}>
                            {groupDetails.members.map((member) => (
                              <li key={member.ID}>
                                {member.FirstName} {member.LastName}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {(!groupDetails.leaders || groupDetails.leaders.length === 0) &&
                        (!groupDetails.members || groupDetails.members.length === 0) && (
                          <div style={{ fontStyle: 'italic', color: '#666' }}>
                            No leaders or members found.
                          </div>
                        )}
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </figure>
  );
}

export default SmallGroupList;
