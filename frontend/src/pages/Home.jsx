import React, {useState, useEffect} from 'react';
import {Link} from 'react-router-dom';
import { graphqlRequest, queries } from '../services/api';
import axios from 'axios';

// Note: Upcoming events query is not yet available in GraphQL schema
// Using REST API as fallback until GraphQL query is added
const REST_API = axios.create({ baseURL: 'http://127.0.0.1:8099' });

function Home() {
    const [upcomingEvents, setUpcomingEvents] = useState([]);
    const [stats, setStats] = useState({
        totalPeople: 0,
        totalEvents: 0,
        totalSmallGroups: 0,
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // TODO: Replace with GraphQL query when upcomingEvents is added to schema
                const [upcomingRes, peopleData, eventsData, groupsData] = await Promise.all([
                    REST_API.get('/events/upcoming'),
                    graphqlRequest(queries.getAllPeople),
                    graphqlRequest(queries.getAllEvents),
                    graphqlRequest(queries.getAllSmallGroups),
                ]);
                
                setUpcomingEvents(upcomingRes.data.slice(0, 5)); // Show next 5 upcoming events
                setStats({
                    totalPeople: peopleData.people.length,
                    totalEvents: eventsData.events.length,
                    totalSmallGroups: groupsData.smallGroups.length,
                });
                setLoading(false);
            } catch (err) {
                console.error('Error fetching data:', err);
                setError(err);
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <div>
            <h1>Youth Group Dashboard</h1>

            <article>
                <header>
                    <h2>Upcoming Events</h2>
                </header>
                {upcomingEvents.length > 0 ? (
                    <table role="grid">
                        <thead>
                        <tr>
                            <th scope="col">Event Name</th>
                            <th scope="col">Date & Time</th>
                            <th scope="col">Location</th>
                            <th scope="col">Type</th>
                        </tr>
                        </thead>
                        <tbody>
                        {upcomingEvents.map((event) => (
                            <tr key={event.id}>
                                <td>
                                    <Link to="/events">{event.name}</Link>
                                </td>
                                <td>{new Date(event.dateTime).toLocaleString()}</td>
                                <td>{event.location}</td>
                                <td>{event.type}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No upcoming events scheduled.</p>
                )}
                <footer>
                    <Link to="/events" role="button">View All Events</Link>
                </footer>
            </article>
        </div>
    );
}

export default Home;
