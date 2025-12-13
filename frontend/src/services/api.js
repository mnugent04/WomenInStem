import { GraphQLClient } from 'graphql-request';

const endpoint = 'http://127.0.0.1:8099/graphql';

const client = new GraphQLClient(endpoint);

// GraphQL Queries
export const queries = {
  // People queries
  getAllPeople: `
    query {
      people {
        id
        firstName
        lastName
        age
      }
    }
  `,
  
  getPerson: `
    query GetPerson($personId: Int!) {
      person(personId: $personId) {
        id
        firstName
        lastName
        age
      }
    }
  `,
  
  // Event queries
  getAllEvents: `
    query {
      events {
        id
        name
        type
        dateTime
        location
        notes
      }
    }
  `,
  
  getEvent: `
    query GetEvent($eventId: Int!) {
      event(eventId: $eventId) {
        id
        name
        type
        dateTime
        location
        notes
      }
    }
  `,
  
  getEventRegistrations: `
    query GetEventRegistrations($eventId: Int!) {
      eventRegistrations(eventId: $eventId) {
        id
        eventId
        attendeeId
        leaderId
        volunteerId
        emergencyContact
        firstName
        lastName
        personId
      }
    }
  `,
  
  getComprehensiveEventSummary: `
    query GetComprehensiveEventSummary($eventId: Int!) {
      comprehensiveEventSummary(eventId: $eventId) {
        event {
          id
          name
          type
          dateTime
          location
          notes
        }
        registrations {
          total
          attendees
          leaders
          volunteers
        }
        liveCheckIns {
          count
          source
        }
        notes {
          count
          source
        }
        summary {
          totalRegistered
          totalCheckedIn
          attendanceRate
          notesCount
        }
        dataSources {
          eventInfo
          registrations
          liveCheckIns
          notes
        }
      }
    }
  `,
  
  // Small Group queries
  getAllSmallGroups: `
    query {
      smallGroups {
        id
        name
      }
    }
  `,
  
  getSmallGroup: `
    query GetSmallGroup($groupId: Int!) {
      smallGroup(groupId: $groupId) {
        id
        name
      }
    }
  `,
  
  getSmallGroupMembers: `
    query GetSmallGroupMembers($groupId: Int!) {
      smallGroupMembers(groupId: $groupId) {
        id
        attendeeId
        smallGroupId
        firstName
        lastName
      }
    }
  `,
  
  getSmallGroupLeaders: `
    query GetSmallGroupLeaders($groupId: Int!) {
      smallGroupLeaders(groupId: $groupId) {
        id
        leaderId
        smallGroupId
        firstName
        lastName
      }
    }
  `,
  
  // Notes queries
  getPersonNotes: `
    query GetPersonNotes($personId: Int!) {
      personNotes(personId: $personId) {
        id
        personId
        text
        category
        createdBy
        created
        updated
      }
    }
  `,
  
  getParentContacts: `
    query GetParentContacts($personId: Int!) {
      parentContacts(personId: $personId) {
        id
        personId
        method
        summary
        date
        createdBy
        created
        updated
      }
    }
  `,
  
  getEventNotes: `
    query GetEventNotes($eventId: Int!) {
      eventNotes(eventId: $eventId) {
        id
        eventId
        notes
        concerns
        studentWins
        createdBy
        created
        updated
      }
    }
  `,
  
  // Live check-ins
  getLiveCheckIns: `
    query GetLiveCheckIns($eventId: Int!) {
      liveCheckIns(eventId: $eventId) {
        eventId
        count
        message
        students {
          studentId
          firstName
          lastName
          checkInTime
        }
      }
    }
  `,
};

// GraphQL Mutations
export const mutations = {
  createPerson: `
    mutation CreatePerson($firstName: String!, $lastName: String!, $age: Int) {
      createPerson(person: { firstName: $firstName, lastName: $lastName, age: $age }) {
        id
        firstName
        lastName
        age
      }
    }
  `,
  
  updatePerson: `
    mutation UpdatePerson($personId: Int!, $firstName: String, $lastName: String, $age: Int) {
      updatePerson(personId: $personId, person: { firstName: $firstName, lastName: $lastName, age: $age }) {
        id
        firstName
        lastName
        age
      }
    }
  `,
  
  deletePerson: `
    mutation DeletePerson($personId: Int!) {
      deletePerson(personId: $personId)
    }
  `,
  
  createEvent: `
    mutation CreateEvent($name: String!, $type: String!, $dateTime: DateTime!, $location: String!, $notes: String) {
      createEvent(event: { name: $name, type: $type, dateTime: $dateTime, location: $location, notes: $notes }) {
        id
        name
        type
        dateTime
        location
        notes
      }
    }
  `,
  
  createSmallGroup: `
    mutation CreateSmallGroup($name: String!) {
      createSmallGroup(group: { name: $name }) {
        id
        name
      }
    }
  `,
  
  registerForEvent: `
    mutation RegisterForEvent($eventId: Int!, $attendeeId: Int, $leaderId: Int, $volunteerId: Int, $emergencyContact: String!) {
      registerForEvent(eventId: $eventId, registration: { attendeeId: $attendeeId, leaderId: $leaderId, volunteerId: $volunteerId, emergencyContact: $emergencyContact }) {
        id
        eventId
        attendeeId
        leaderId
        volunteerId
        emergencyContact
      }
    }
  `,
  
  addMemberToGroup: `
    mutation AddMemberToGroup($groupId: Int!, $attendeeId: Int!) {
      addMemberToGroup(groupId: $groupId, input: { attendeeId: $attendeeId }) {
        id
        attendeeId
        smallGroupId
      }
    }
  `,
  
  addLeaderToGroup: `
    mutation AddLeaderToGroup($groupId: Int!, $leaderId: Int!) {
      addLeaderToGroup(groupId: $groupId, input: { leaderId: $leaderId }) {
        id
        leaderId
        smallGroupId
      }
    }
  `,
  
  addPersonNote: `
    mutation AddPersonNote($personId: Int!, $text: String!, $category: String, $createdBy: String) {
      addPersonNote(personId: $personId, note: { text: $text, category: $category, createdBy: $createdBy }) {
        id
        personId
        text
        category
        createdBy
        created
      }
    }
  `,
};

// Helper functions for making GraphQL requests
export const graphqlRequest = async (query, variables = {}) => {
  try {
    const data = await client.request(query, variables);
    return data;
  } catch (error) {
    console.error('GraphQL Error:', error);
    throw error;
  }
};

// Export the client for direct use if needed
export default client;
