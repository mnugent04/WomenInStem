import React from 'react';
import AddMemberToGroup from './AddMemberToGroup';
import AddLeaderToGroup from './AddLeaderToGroup';

function SmallGroupList({
                            smallGroups,
                            onGroupClick,
                            expandedGroupId,
                            groupDetails,
                            onDelete,
                            onAddMember,
                            onAddLeader,
                            onRemoveMember,
                            onRemoveLeader,
                            showAddMemberForm,
                            showAddLeaderForm,
                            onMemberSuccess,
                            onLeaderSuccess
                        }) {
    return (
        <figure>
            <table role="grid">
                <thead>
                <tr>
                    <th scope="col">Name</th>
                    {onDelete && <th scope="col">Actions</th>}
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
                            {onDelete && (
                                <td>
                                    <button className="secondary outline" onClick={() => onDelete(group.id)}>
                                        Delete
                                    </button>
                                </td>
                            )}
                        </tr>
                        {expandedGroupId === group.id && groupDetails && (
                            <tr>
                                <td colSpan={onDelete ? "2" : "1"}
                                    style={{paddingLeft: '2rem', paddingTop: '1rem', paddingBottom: '1rem'}}>
                                    <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
                                        {groupDetails.leaders && groupDetails.leaders.length > 0 && (
                                            <div>
                                                <div style={{
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center'
                                                }}>
                                                    <strong>Leaders:</strong>
                                                    {onAddLeader && (
                                                        <button
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    onAddLeader(group.id);
                                                                }}
                                                                style={{
                                                                    fontSize: '0.85em',
                                                                    padding: '0.2rem 0.5rem'
                                                                }}>
                                                            Add Leader
                                                        </button>
                                                    )}
                                                </div>
                                                <ul style={{marginTop: '0.5rem', marginBottom: 0}}>
                                                    {groupDetails.leaders.map((leader) => (
                                                        <li key={leader.ID} style={{
                                                            display: 'flex',
                                                            justifyContent: 'space-between',
                                                            alignItems: 'center',
                                                            marginBottom: '0.25rem'
                                                        }}>
                                                            <span>{leader.FirstName} {leader.LastName}</span>
                                                            {onRemoveLeader && (
                                                                <button
                                                                    className="secondary"
                                                                    onClick={() => onRemoveLeader(group.id, leader.ID)}
                                                                    style={{
                                                                        fontSize: '0.85em',
                                                                        padding: '0.2rem 0.5rem'
                                                                    }}
                                                                >
                                                                    Remove
                                                                </button>
                                                            )}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        {(!groupDetails.leaders || groupDetails.leaders.length === 0) && (
                                            <div>
                                                <div style={{
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center'
                                                }}>
                                                    <strong>Leaders:</strong>
                                                    {onAddLeader && (
                                                        <button className="secondary"
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    onAddLeader(group.id);
                                                                }}>
                                                            Add Leader
                                                        </button>
                                                    )}
                                                </div>
                                                <p style={{fontStyle: 'italic', color: '#666', marginTop: '0.5rem'}}>No
                                                    leaders yet.</p>
                                            </div>
                                        )}
                                        {showAddLeaderForm === group.id && (
                                            <div style={{
                                                marginTop: '0.5rem',
                                                padding: '0.75rem',
                                                border: '1px solid #ccc',
                                                borderRadius: '4px',
                                                backgroundColor: '#f9f9f9'
                                            }}>
                                                <h5 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Add Leader to Group</h5>
                                                <AddLeaderToGroup
                                                    groupId={group.id}
                                                    onSuccess={onLeaderSuccess || (() => {
                                                        if (onAddLeader) onAddLeader(null);
                                                    })}
                                                    onCancel={() => {
                                                        if (onAddLeader) onAddLeader(null);
                                                    }}
                                                />
                                            </div>
                                        )}
                                        {groupDetails.members && groupDetails.members.length > 0 && (
                                            <div>
                                                <div style={{
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center'
                                                }}>
                                                    <strong>Members:</strong>
                                                    {onAddMember && (
                                                        <button
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    onAddMember(group.id);
                                                                }}
                                                                style={{
                                                                    fontSize: '0.85em',
                                                                    padding: '0.2rem 0.5rem'
                                                                }}>
                                                            Add Member
                                                        </button>
                                                    )}
                                                </div>
                                                <ul style={{marginTop: '0.5rem', marginBottom: 0}}>
                                                    {groupDetails.members.map((member) => (
                                                        <li key={member.ID} style={{
                                                            display: 'flex',
                                                            justifyContent: 'space-between',
                                                            alignItems: 'center',
                                                            marginBottom: '0.25rem'
                                                        }}>
                                                            <span>{member.FirstName} {member.LastName}</span>
                                                            {onRemoveMember && (
                                                                <button
                                                                    className="secondary"
                                                                    onClick={() => onRemoveMember(group.id, member.ID)}
                                                                    style={{
                                                                        fontSize: '0.85em',
                                                                        padding: '0.2rem 0.5rem'
                                                                    }}
                                                                >
                                                                    Remove
                                                                </button>
                                                            )}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        {(!groupDetails.members || groupDetails.members.length === 0) && (
                                            <div>
                                                <div style={{
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center'
                                                }}>
                                                    <strong>Members:</strong>
                                                    {onAddMember && (
                                                        <button className="secondary"
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    onAddMember(group.id);
                                                                }}>
                                                            Add Member
                                                        </button>
                                                    )}
                                                </div>
                                                <p style={{fontStyle: 'italic', color: '#666', marginTop: '0.5rem'}}>No
                                                    members yet.</p>
                                            </div>
                                        )}
                                        {showAddMemberForm === group.id && (
                                            <div style={{
                                                marginTop: '0.5rem',
                                                padding: '0.75rem',
                                                border: '1px solid #ccc',
                                                borderRadius: '4px',
                                                backgroundColor: '#f9f9f9'
                                            }}>
                                                <h5 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Add Member to Group</h5>
                                                <AddMemberToGroup
                                                    groupId={group.id}
                                                    onSuccess={onMemberSuccess || (() => {
                                                        if (onAddMember) onAddMember(null);
                                                    })}
                                                    onCancel={() => {
                                                        if (onAddMember) onAddMember(null);
                                                    }}
                                                />
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

