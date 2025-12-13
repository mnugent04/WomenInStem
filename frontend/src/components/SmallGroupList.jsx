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
    // --- Helper function to render Leader/Member List ---
    const renderPersonList = (title, list, onAdd, onRemove, isLeader) => (
        <div>
            {/* Title row: Displays the count and the list */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <strong>{title} ({list ? list.length : 0}):</strong>
            </div>
            {list && list.length > 0 ? (
                <ul style={{ marginTop: '0.5rem', marginBottom: '1rem', listStyle: 'disc', paddingLeft: '20px' }}>
                    {list.map((person) => {
                        // Handle both GraphQL (camelCase) and REST (PascalCase) formats
                        const firstName = person.firstName || person.FirstName || '';
                        const lastName = person.lastName || person.LastName || '';
                        // For remove operations, we need the SmallGroupMember/SmallGroupLeader ID (not person ID)
                        const recordId = person.id || person.ID;
                        // Use recordId for key and remove operations
                        const displayKey = recordId || `${person.attendeeId || person.leaderId}-${expandedGroupId}`;
                        
                        return (
                            <li key={displayKey} style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                marginBottom: '0.25rem',
                            }}>
                                {/* 1. Name Span: Flex to fill space, hides overflow if name is too long */}
                                <span style={{
                                    flexGrow: 1,           // Takes up available space
                                    flexShrink: 1,         // Allows it to shrink
                                    overflow: 'hidden',    // Hides text that exceeds the container
                                    textOverflow: 'ellipsis', // Adds "..." to long names
                                    whiteSpace: 'nowrap',  // Ensures the text stays on one line
                                    marginRight: '0.5rem'  // Small gap before the button
                                }}>
                                    {firstName && lastName ? `${firstName} ${lastName}` : firstName || lastName || 'Unknown'}
                                </span>

                                {onRemove && (
                                    <button
                                        className="secondary"
                                        style={{
                                            padding: '0.25rem 0.5rem',
                                            fontSize: '0.75rem',
                                            // 2. Button: FIXED width (e.g., 5rem) for perfect consistency
                                            width: '5rem',
                                            // Set a consistent height to prevent vertical variation if text wraps
                                            height: '1.75rem',
                                            textAlign: 'center',
                                            flexShrink: 0 // Prevent the button from shrinking
                                        }}
                                        onClick={() => onRemove(expandedGroupId, recordId)}
                                    >
                                        Remove
                                    </button>
                                )}
                            </li>
                        );
                    })}
                </ul>
            ) : (
                <p style={{ fontStyle: 'italic', color: '#666', marginTop: '0.5rem' }}>No {title.toLowerCase()} yet.</p>
            )}

            {/* Add Form (rendered outside of the list) - No changes here */}
            {isLeader ? showAddLeaderForm === expandedGroupId && (
                <div style={{ marginTop: '0.5rem', padding: '0.75rem', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
                    <h5 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Add Leader to Group</h5>
                    <AddLeaderToGroup
                        groupId={expandedGroupId}
                        onSuccess={onLeaderSuccess || (() => { if (onAddLeader) onAddLeader(null); })}
                        onCancel={() => { if (onAddLeader) onAddLeader(null); }}
                    />
                </div>
            ) : showAddMemberForm === expandedGroupId && (
                <div style={{ marginTop: '0.5rem', padding: '0.75rem', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
                    <h5 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Add Member to Group</h5>
                    <AddMemberToGroup
                        groupId={expandedGroupId}
                        onSuccess={onMemberSuccess || (() => { if (onAddMember) onAddMember(null); })}
                        onCancel={() => { if (onAddMember) onAddMember(null); }}
                    />
                </div>
            )}
        </div>
    );

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
                                    style={{ paddingLeft: '2rem', paddingTop: '1rem', paddingBottom: '1rem' }}>

                                    {/* Main Content Area */}
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

                                        {/* Leaders Section */}
                                        {renderPersonList("Leaders", groupDetails.leaders, onAddLeader, onRemoveLeader, true)}

                                        {/* Members Section */}
                                        {renderPersonList("Members", groupDetails.members, onAddMember, onRemoveMember, false)}

                                        <hr style={{ margin: '0.5rem 0' }} />

                                        {/* BUTTON LAYOUT (Add Leader/Member) - No changes here */}
                                        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>

                                            {onAddLeader && (
                                                <button
                                                    className="secondary"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onAddLeader(showAddLeaderForm === group.id ? null : group.id);
                                                    }}
                                                >
                                                    {showAddLeaderForm === group.id ? 'Cancel Adding Leader' : 'Add Leader'}
                                                </button>
                                            )}

                                            {onAddMember && (
                                                <button
                                                    className="secondary"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onAddMember(showAddMemberForm === group.id ? null : group.id);
                                                    }}
                                                >
                                                    {showAddMemberForm === group.id ? 'Cancel Adding Member' : 'Add Member'}
                                                </button>
                                            )}
                                        </div>
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