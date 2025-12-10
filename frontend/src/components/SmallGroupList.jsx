import React from 'react';

function SmallGroupList({ smallGroups }) {
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
            <tr key={group.id}>
              <td>{group.name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}

export default SmallGroupList;
