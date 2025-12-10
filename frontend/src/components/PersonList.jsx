import React from 'react';

function PersonList({ people, onEdit, onDelete, onView }) {
  return (
    <figure>
      <table role="grid">
        <thead>
          <tr>
            <th scope="col">First Name</th>
            <th scope="col">Last Name</th>
            <th scope="col">Age</th>
            <th scope="col" colSpan={onView ? "3" : "2"}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {people.map((person) => (
            <tr key={person.id}>
              <td>{person.firstName}</td>
              <td>{person.lastName}</td>
              <td>{person.age}</td>
              {onView && (
                <td>
                  <button className="secondary" onClick={() => onView(person)}>View Details</button>
                </td>
              )}
              <td><button className="secondary" onClick={() => onEdit(person)}>Edit</button></td>
              <td><button className="secondary outline" onClick={() => onDelete(person.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}

export default PersonList;
