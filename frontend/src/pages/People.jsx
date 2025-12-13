import React, {useState, useEffect} from 'react';
import PersonList from '../components/PersonList';
import PersonForm from '../components/PersonForm';
import PersonNotes from '../components/PersonNotes';
import PersonParentContacts from '../components/PersonParentContacts';
import PersonRoles from '../components/PersonRoles';
import PersonProfile from '../components/PersonProfile';
import { graphqlRequest, queries, mutations } from '../services/api';

function People() {
    const [people, setPeople] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editingPerson, setEditingPerson] = useState(null);
    const [viewingPerson, setViewingPerson] = useState(null);
    const [profilePersonId, setProfilePersonId] = useState(null);

    const fetchPeople = async () => {
        setLoading(true);
        try {
            const data = await graphqlRequest(queries.getAllPeople);
            setPeople(data.people);
            setLoading(false);
        } catch (err) {
            setError(err);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPeople();
    }, []);

    const handleSave = async (person) => {
        try {
            if (person.id) {
                // Update existing person
                await graphqlRequest(mutations.updatePerson, {
                    personId: person.id,
                    firstName: person.firstName,
                    lastName: person.lastName,
                    age: person.age
                });
            } else {
                // Create new person
                await graphqlRequest(mutations.createPerson, {
                    firstName: person.firstName,
                    lastName: person.lastName,
                    age: person.age
                });
            }
            setEditingPerson(null);
            fetchPeople();
        } catch (err) {
            console.error('Error saving person:', err);
            setError(err);
        }
    };

    const handleCancel = () => {
        setEditingPerson(null);
    };

    const handleEdit = (person) => {
        setViewingPerson(null);
        setEditingPerson(person);
    };

    const handleDelete = async (personId) => {
        if (window.confirm('Are you sure you want to delete this person?')) {
            try {
                await graphqlRequest(mutations.deletePerson, { personId });
                fetchPeople();
                if (viewingPerson && viewingPerson.id === personId) {
                    setViewingPerson(null);
                }
            } catch (err) {
                setError(err);
            }
        }
    };

    const handleView = (person) => {
        setEditingPerson(null);
        setViewingPerson(person);
    };

    const handleCloseView = () => {
        setViewingPerson(null);
    };

    const handleViewProfile = (person) => {
        setProfilePersonId(person.id);
    };

    const handleCloseProfile = () => {
        setProfilePersonId(null);
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <div>
            <h1>People</h1>

            {viewingPerson ? (
                <article>
                    <header>
                        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                            <h2>{viewingPerson.firstName} {viewingPerson.lastName}</h2>
                            <button className="secondary" onClick={handleCloseView}>Close</button>
                        </div>
                        <p>Age: {viewingPerson.age || 'N/A'}</p>
                    </header>

                    <PersonRoles personId={viewingPerson.id} onUpdate={fetchPeople}/>
                    <PersonNotes personId={viewingPerson.id}/>
                    <PersonParentContacts personId={viewingPerson.id}/>
                </article>
            ) : (
                <>
                    {/* Toggle Add Person */}
                    <button
                        onClick={() => setEditingPerson(editingPerson ? null : {})}
                        style={{
                            padding: "10px 16px",
                            color: "white",
                            border: "none",
                            borderRadius: "6px",
                            cursor: "pointer",
                            marginBottom: "1rem"
                        }}
                    >
                        {editingPerson ? "Close Add Person" : "Add New Person"}
                    </button>

                    {/* Collapsible Person Form */}
                    {editingPerson && (
                        <div
                            style={{
                                marginBottom: "2rem",
                                padding: "1rem",
                                border: "1px solid #ccc",
                                borderRadius: "6px",
                                backgroundColor: "#fafafa"
                            }}
                        >
                            <PersonForm
                                person={editingPerson}
                                onSave={handleSave}
                                onCancel={handleCancel}
                            />
                        </div>
                    )}

                    <PersonList
                        people={people}
                        onEdit={handleEdit}
                        onDelete={handleDelete}
                        onView={handleView}
                        onViewProfile={handleViewProfile}
                    />
                </>
            )}

            {/* Comprehensive Profile Modal */}
            {profilePersonId && (
                <PersonProfile
                    personId={profilePersonId}
                    onClose={handleCloseProfile}
                />
            )}
        </div>
    );
}

export default People;
