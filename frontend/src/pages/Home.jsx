import React, {useState, useEffect} from 'react';
import {Link} from 'react-router-dom';
import api from '../services/api';

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
        Promise.all([
            api.get('/events/upcoming'),
            api.get('/people'),
            api.get('/events'),
            api.get('/smallgroups'),
        ])
            .then(([upcomingRes, peopleRes, eventsRes, groupsRes]) => {
                setUpcomingEvents(upcomingRes.data.slice(0, 5)); // Show next 5 upcoming events
                setStats({
                    totalPeople: peopleRes.data.length,
                    totalEvents: eventsRes.data.length,
                    totalSmallGroups: groupsRes.data.length,
                });
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                setError(error);
                setLoading(false);
            });
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
