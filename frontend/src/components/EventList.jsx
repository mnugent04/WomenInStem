import React from 'react';

function EventList({ events }) {
  return (
    <figure>
      <table role="grid">
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Date & Time</th>
            <th scope="col">Location</th>
            <th scope="col">Type</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id}>
              <td>{event.name}</td>
              <td>{event.dateTime}</td>
              <td>{event.location}</td>
              <td>{event.type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}

export default EventList;
