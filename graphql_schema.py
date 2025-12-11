# graphql_schema.py

"""
This file defines the GraphQL schema for the Youth Group API.

GraphQL provides a flexible query language that allows clients to request exactly the data they need.
This schema wraps our existing REST API endpoints, providing a GraphQL interface to the same functionality.

Key Concepts:
1. Schema: Defines the types of data that can be queried - the contract between client and server
2. Types: Building blocks representing our data models (Person, Event, SmallGroup, etc.)
3. Query: Read operations - fetching data from MySQL, MongoDB, and Redis
4. Mutation: Write operations - creating, updating, and deleting data
5. Resolver: Functions that fetch/process data for each field
"""

import strawberry
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException

# Import existing FastAPI functions to reuse logic
# Note: We'll need to import the actual database functions since FastAPI endpoints
# are route handlers, not reusable functions. We'll create wrapper functions or
# call the database logic directly.

# For now, we'll import what we can and create resolvers that make HTTP-like calls
# or directly access the database. In a real implementation, you'd refactor the
# FastAPI endpoints to separate business logic from route handlers.

from youthGroupFastAPI import (
    db_pool,
    get_mongo_db,
    get_redis_conn,
    get_db_connection
)
import mysql.connector
import redis
from bson import ObjectId

# --- Strawberry Types ---
# These represent our data models in GraphQL

@strawberry.type
class Person:
    """GraphQL type representing a person."""
    id: int
    firstName: str
    lastName: str
    age: Optional[int] = None

@strawberry.type
class Attendee:
    """GraphQL type representing an attendee."""
    id: int
    personId: int
    guardian: str
    person: Optional[Person] = None  # Nested person data

@strawberry.type
class Leader:
    """GraphQL type representing a leader."""
    id: int
    personId: int
    person: Optional[Person] = None  # Nested person data

@strawberry.type
class Volunteer:
    """GraphQL type representing a volunteer."""
    id: int
    personId: int
    person: Optional[Person] = None  # Nested person data

@strawberry.type
class SmallGroup:
    """GraphQL type representing a small group."""
    id: int
    name: str

@strawberry.type
class SmallGroupMember:
    """GraphQL type for a member in a small group."""
    id: int
    attendeeId: int
    smallGroupId: int
    firstName: Optional[str] = None
    lastName: Optional[str] = None

@strawberry.type
class SmallGroupLeader:
    """GraphQL type for a leader in a small group."""
    id: int
    leaderId: int
    smallGroupId: int
    firstName: Optional[str] = None
    lastName: Optional[str] = None

@strawberry.type
class Event:
    """GraphQL type representing an event."""
    id: int
    name: str
    type: str
    dateTime: datetime
    location: str
    notes: Optional[str] = None

@strawberry.type
class Registration:
    """GraphQL type representing an event registration."""
    id: int
    eventId: int
    attendeeId: Optional[int] = None
    leaderId: Optional[int] = None
    volunteerId: Optional[int] = None
    emergencyContact: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    personId: Optional[int] = None

@strawberry.type
class PersonNote:
    """GraphQL type for a note about a person (MongoDB)."""
    id: str
    personId: int
    text: str
    category: Optional[str] = None
    createdBy: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

@strawberry.type
class ParentContact:
    """GraphQL type for a parent contact record (MongoDB)."""
    id: str
    personId: int
    method: Optional[str] = None
    summary: str
    date: Optional[str] = None
    createdBy: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

@strawberry.type
class EventNote:
    """GraphQL type for event notes/highlights (MongoDB)."""
    id: str
    eventId: int
    notes: Optional[str] = None
    concerns: Optional[str] = None
    studentWins: Optional[str] = None
    createdBy: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

@strawberry.type
class CheckedInStudent:
    """GraphQL type for a checked-in student (Redis + MySQL)."""
    studentId: int
    firstName: str
    lastName: str
    checkInTime: Optional[str] = None

@strawberry.type
class LiveCheckInSummary:
    """GraphQL type for live check-in summary."""
    eventId: int
    count: int
    students: List[CheckedInStudent]
    message: str

@strawberry.type
class RegistrationSummary:
    """Summary of event registrations."""
    total: int
    attendees: int
    leaders: int
    volunteers: int

@strawberry.type
class LiveCheckInData:
    """Live check-in data summary."""
    count: int
    source: str

@strawberry.type
class NotesSummary:
    """Event notes summary."""
    count: int
    source: str

@strawberry.type
class EventStatistics:
    """Event statistics."""
    totalRegistered: int
    totalCheckedIn: int
    attendanceRate: float
    notesCount: int

@strawberry.type
class DataSources:
    """Information about data sources."""
    eventInfo: str
    registrations: str
    liveCheckIns: str
    notes: str

@strawberry.type
class ComprehensiveEventSummary:
    """GraphQL type for comprehensive event data from all DBMS."""
    event: Event
    registrations: RegistrationSummary
    liveCheckIns: LiveCheckInData
    notes: NotesSummary
    summary: EventStatistics
    dataSources: DataSources

# --- Input Types for Mutations ---

@strawberry.input
class PersonCreateInput:
    """Input type for creating a person."""
    firstName: str
    lastName: str
    age: Optional[int] = None

@strawberry.input
class PersonUpdateInput:
    """Input type for updating a person."""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    age: Optional[int] = None

@strawberry.input
class EventCreateInput:
    """Input type for creating an event."""
    name: str
    type: str
    dateTime: datetime
    location: str
    notes: Optional[str] = None

@strawberry.input
class EventUpdateInput:
    """Input type for updating an event."""
    name: Optional[str] = None
    type: Optional[str] = None
    dateTime: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None

@strawberry.input
class SmallGroupCreateInput:
    """Input type for creating a small group."""
    name: str

@strawberry.input
class RegistrationInput:
    """Input type for registering for an event."""
    attendeeId: Optional[int] = None
    leaderId: Optional[int] = None
    volunteerId: Optional[int] = None
    emergencyContact: str

@strawberry.input
class AddMemberToGroupInput:
    """Input type for adding a member to a small group."""
    attendeeId: int

@strawberry.input
class AddLeaderToGroupInput:
    """Input type for adding a leader to a small group."""
    leaderId: int

@strawberry.input
class PersonNoteInput:
    """Input type for creating a person note."""
    text: str
    category: Optional[str] = None
    createdBy: Optional[str] = None

@strawberry.input
class ParentContactInput:
    """Input type for creating a parent contact."""
    method: Optional[str] = None
    summary: str
    date: Optional[str] = None
    createdBy: Optional[str] = None

@strawberry.input
class EventNoteInput:
    """Input type for creating an event note."""
    notes: Optional[str] = None
    concerns: Optional[str] = None
    studentWins: Optional[str] = None
    createdBy: Optional[str] = None

# --- Resolver Functions ---
# These functions fetch data from the database

def get_all_people_resolver() -> List[Person]:
    """Resolver to fetch all people."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person ORDER BY lastName, firstName;")
        people_data = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [Person(**p) for p in people_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_person_by_id_resolver(person_id: int) -> Optional[Person]:
    """Resolver to fetch a person by ID."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s;", (person_id,))
        person_data = cursor.fetchone()
        cursor.close()
        cnx.close()
        if not person_data:
            return None
        return Person(**person_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_all_events_resolver() -> List[Event]:
    """Resolver to fetch all events."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event
            ORDER BY DateTime DESC;
        """)
        events_data = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [Event(**e) for e in events_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_event_by_id_resolver(event_id: int) -> Optional[Event]:
    """Resolver to fetch an event by ID."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event
            WHERE ID = %s;
        """, (event_id,))
        event_data = cursor.fetchone()
        cursor.close()
        cnx.close()
        if not event_data:
            return None
        return Event(**event_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_all_small_groups_resolver() -> List[SmallGroup]:
    """Resolver to fetch all small groups."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID AS id, Name AS name FROM SmallGroup ORDER BY name;")
        groups_data = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [SmallGroup(**g) for g in groups_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_small_group_by_id_resolver(group_id: int) -> Optional[SmallGroup]:
    """Resolver to fetch a small group by ID."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID AS id, Name AS name FROM SmallGroup WHERE ID = %s;", (group_id,))
        group_data = cursor.fetchone()
        cursor.close()
        cnx.close()
        if not group_data:
            return None
        return SmallGroup(**group_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_small_group_members_resolver(group_id: int) -> List[SmallGroupMember]:
    """Resolver to fetch members of a small group."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT SGM.ID AS id, SGM.AttendeeID AS attendeeId, SGM.SmallGroupID AS smallGroupId,
                   P.FirstName AS firstName, P.LastName AS lastName
            FROM SmallGroupMember SGM
            JOIN Attendee A ON SGM.AttendeeID = A.PersonID
            JOIN Person P ON A.PersonID = P.ID
            WHERE SGM.SmallGroupID = %s;
        """, (group_id,))
        members_data = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [SmallGroupMember(**m) for m in members_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_small_group_leaders_resolver(group_id: int) -> List[SmallGroupLeader]:
    """Resolver to fetch leaders of a small group."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT L.ID AS id, L.LeaderID AS leaderId, L.SmallGroupID AS smallGroupId,
                   P.FirstName AS firstName, P.LastName AS lastName
            FROM SmallGroupLeader L
            JOIN Person P ON L.LeaderID = P.ID
            WHERE L.SmallGroupID = %s;
        """, (group_id,))
        leaders_data = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [SmallGroupLeader(**l) for l in leaders_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_event_registrations_resolver(event_id: int) -> List[Registration]:
    """Resolver to fetch registrations for an event."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Try with VolunteerID first
        try:
            cursor.execute("""
                SELECT R.ID AS id, R.EventID AS eventId,
                       R.AttendeeID AS attendeeId, R.LeaderID AS leaderId, R.VolunteerID AS volunteerId,
                       R.EmergencyContact AS emergencyContact,
                       P.FirstName AS firstName, P.LastName AS lastName, P.ID AS personId
                FROM Registration R
                LEFT JOIN Attendee A ON R.AttendeeID = A.ID
                LEFT JOIN Leader L ON R.LeaderID = L.ID
                LEFT JOIN Volunteer V ON R.VolunteerID = V.ID
                LEFT JOIN Person P ON (A.PersonID = P.ID OR L.PersonID = P.ID OR V.PersonID = P.ID)
                WHERE R.EventID = %s;
            """, (event_id,))
        except:
            cursor.execute("""
                SELECT R.ID AS id, R.EventID AS eventId,
                       R.AttendeeID AS attendeeId, R.LeaderID AS leaderId, NULL AS volunteerId,
                       R.EmergencyContact AS emergencyContact,
                       P.FirstName AS firstName, P.LastName AS lastName, P.ID AS personId
                FROM Registration R
                LEFT JOIN Attendee A ON R.AttendeeID = A.ID
                LEFT JOIN Leader L ON R.LeaderID = L.ID
                LEFT JOIN Person P ON (A.PersonID = P.ID OR L.PersonID = P.ID)
                WHERE R.EventID = %s;
            """, (event_id,))
        registrations_data = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [Registration(**r) for r in registrations_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_person_notes_resolver(person_id: int) -> List[PersonNote]:
    """Resolver to fetch notes for a person from MongoDB."""
    try:
        db = get_mongo_db()
        notes = list(db["personNotes"].find({"personId": person_id}))
        result = []
        for note in notes:
            result.append(PersonNote(
                id=str(note["_id"]),
                personId=note["personId"],
                text=note.get("text", ""),
                category=note.get("category"),
                createdBy=note.get("createdBy"),
                created=note.get("created"),
                updated=note.get("updated")
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

def get_parent_contacts_resolver(person_id: int) -> List[ParentContact]:
    """Resolver to fetch parent contacts for a person from MongoDB."""
    try:
        db = get_mongo_db()
        contacts = list(db["parentContacts"].find({"personId": person_id}))
        result = []
        for contact in contacts:
            result.append(ParentContact(
                id=str(contact["_id"]),
                personId=contact["personId"],
                method=contact.get("method"),
                summary=contact.get("summary", ""),
                date=contact.get("date"),
                createdBy=contact.get("createdBy"),
                created=contact.get("created"),
                updated=contact.get("updated")
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

def get_event_notes_resolver(event_id: int) -> List[EventNote]:
    """Resolver to fetch notes for an event from MongoDB."""
    try:
        db = get_mongo_db()
        notes = list(db["eventNotes"].find({"eventId": event_id}))
        result = []
        for note in notes:
            result.append(EventNote(
                id=str(note["_id"]),
                eventId=note["eventId"],
                notes=note.get("notes"),
                concerns=note.get("concerns"),
                studentWins=note.get("studentWins"),
                createdBy=note.get("createdBy"),
                created=note.get("created"),
                updated=note.get("updated")
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

def get_live_checkins_resolver(event_id: int) -> Optional[LiveCheckInSummary]:
    """Resolver to fetch live check-ins from Redis."""
    try:
        r = get_redis_conn()
        checked_in_key = f"event:{event_id}:checkedIn"
        times_key = f"event:{event_id}:checkInTimes"
        
        student_ids = r.smembers(checked_in_key)
        if not student_ids:
            return None
        
        timestamps = r.hgetall(times_key)
        student_ids_int = [int(sid) for sid in student_ids]
        
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        format_strings = ",".join(["%s"] * len(student_ids_int))
        query = f"SELECT ID, FirstName, LastName FROM Person WHERE ID IN ({format_strings});"
        cursor.execute(query, tuple(student_ids_int))
        people = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        students = [
            CheckedInStudent(
                studentId=p["ID"],
                firstName=p["FirstName"],
                lastName=p["LastName"],
                checkInTime=timestamps.get(str(p["ID"]))
            )
            for p in people
        ]
        
        return LiveCheckInSummary(
            eventId=event_id,
            count=len(students),
            students=students,
            message=f"{len(students)} students are currently checked in."
        )
    except redis.RedisError as e:
        return None  # Redis might not be available
    except Exception as e:
        return None

def get_comprehensive_event_summary_resolver(event_id: int) -> Optional[ComprehensiveEventSummary]:
    """Resolver for comprehensive event summary combining all DBMS."""
    try:
        event = get_event_by_id_resolver(event_id)
        if not event:
            return None
        
        registrations = get_event_registrations_resolver(event_id)
        live_checkins = get_live_checkins_resolver(event_id)
        notes = get_event_notes_resolver(event_id)
        
        # Build summary objects
        reg_summary = RegistrationSummary(
            total=len(registrations),
            attendees=sum(1 for r in registrations if r.attendeeId),
            leaders=sum(1 for r in registrations if r.leaderId),
            volunteers=sum(1 for r in registrations if r.volunteerId)
        )
        
        live_summary = LiveCheckInData(
            count=live_checkins.count if live_checkins else 0,
            source="Redis"
        )
        
        notes_summary = NotesSummary(
            count=len(notes),
            source="MongoDB"
        )
        
        overall_summary = EventStatistics(
            totalRegistered=len(registrations),
            totalCheckedIn=live_checkins.count if live_checkins else 0,
            attendanceRate=round((live_checkins.count / len(registrations) * 100) if registrations and live_checkins else 0, 2),
            notesCount=len(notes)
        )
        
        data_sources = DataSources(
            eventInfo="MySQL",
            registrations="MySQL",
            liveCheckIns="Redis",
            notes="MongoDB"
        )
        
        return ComprehensiveEventSummary(
            event=event,
            registrations=reg_summary,
            liveCheckIns=live_summary,
            notes=notes_summary,
            summary=overall_summary,
            dataSources=data_sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# --- Mutation Resolvers ---

def create_person_resolver(person: PersonCreateInput) -> Person:
    """Resolver to create a new person."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO Person (FirstName, LastName, Age)
            VALUES (%s, %s, %s)
        """, (person.firstName, person.lastName, person.age))
        cnx.commit()
        person_id = cursor.lastrowid
        cursor.execute(
            "SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s",
            (person_id,)
        )
        new_person = cursor.fetchone()
        cursor.close()
        cnx.close()
        return Person(**new_person)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def update_person_resolver(person_id: int, person: PersonUpdateInput) -> Person:
    """Resolver to update a person."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        
        # Get existing person
        cursor.execute("SELECT * FROM Person WHERE ID = %s;", (person_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Build update query
        fields = []
        values = []
        if person.firstName is not None:
            fields.append("FirstName = %s")
            values.append(person.firstName)
        if person.lastName is not None:
            fields.append("LastName = %s")
            values.append(person.lastName)
        if person.age is not None:
            fields.append("Age = %s")
            values.append(person.age)
        
        if fields:
            sql = f"UPDATE Person SET {', '.join(fields)} WHERE ID = %s"
            values.append(person_id)
            cursor.execute(sql, values)
            cnx.commit()
        
        cursor.execute("SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s;", (person_id,))
        updated = cursor.fetchone()
        cursor.close()
        cnx.close()
        return Person(**updated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def delete_person_resolver(person_id: int) -> bool:
    """Resolver to delete a person."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Person not found")
        cursor.execute("DELETE FROM Person WHERE ID = %s;", (person_id,))
        cnx.commit()
        cursor.close()
        cnx.close()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def create_event_resolver(event: EventCreateInput) -> Event:
    """Resolver to create a new event."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO Event (Name, Type, DateTime, Location, Notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (event.name, event.type, event.dateTime, event.location, event.notes))
        cnx.commit()
        event_id = cursor.lastrowid
        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event WHERE ID = %s
        """, (event_id,))
        new_event = cursor.fetchone()
        cursor.close()
        cnx.close()
        return Event(**new_event)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def create_small_group_resolver(group: SmallGroupCreateInput) -> SmallGroup:
    """Resolver to create a new small group."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroup;")
        next_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO SmallGroup (ID, Name) VALUES (%s, %s);", (next_id, group.name.strip()))
        cnx.commit()
        cursor.close()
        cnx.close()
        return SmallGroup(id=next_id, name=group.name.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def register_for_event_resolver(event_id: int, registration: RegistrationInput) -> Registration:
    """Resolver to register someone for an event."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT IFNULL(MAX(ID),0) + 1 AS nextId FROM Registration;")
        next_id = cursor.fetchone()[0]
        
        # Try with VolunteerID if provided
        if registration.volunteerId:
            try:
                cursor.execute("""
                    INSERT INTO Registration (ID, EventID, AttendeeID, LeaderID, VolunteerID, EmergencyContact)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (next_id, event_id, registration.attendeeId, registration.leaderId, registration.volunteerId, registration.emergencyContact))
            except:
                raise HTTPException(400, "Volunteer registration requires VolunteerID column")
        else:
            cursor.execute("""
                INSERT INTO Registration (ID, EventID, AttendeeID, LeaderID, EmergencyContact)
                VALUES (%s, %s, %s, %s, %s);
            """, (next_id, event_id, registration.attendeeId, registration.leaderId, registration.emergencyContact))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        # Return the registration (simplified)
        return Registration(
            id=next_id,
            eventId=event_id,
            attendeeId=registration.attendeeId,
            leaderId=registration.leaderId,
            volunteerId=registration.volunteerId,
            emergencyContact=registration.emergencyContact
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def add_member_to_group_resolver(group_id: int, input: AddMemberToGroupInput) -> SmallGroupMember:
    """Resolver to add a member to a small group."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroupMember;")
        next_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO SmallGroupMember (ID, AttendeeID, SmallGroupID)
            VALUES (%s, %s, %s);
        """, (next_id, input.attendeeId, group_id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return SmallGroupMember(id=next_id, attendeeId=input.attendeeId, smallGroupId=group_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def add_leader_to_group_resolver(group_id: int, input: AddLeaderToGroupInput) -> SmallGroupLeader:
    """Resolver to add a leader to a small group."""
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroupLeader;")
        next_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO SmallGroupLeader (ID, LeaderID, SmallGroupID)
            VALUES (%s, %s, %s);
        """, (next_id, input.leaderId, group_id))
        cnx.commit()
        cursor.close()
        cnx.close()
        return SmallGroupLeader(id=next_id, leaderId=input.leaderId, smallGroupId=group_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def add_person_note_resolver(person_id: int, note: PersonNoteInput) -> PersonNote:
    """Resolver to add a note for a person."""
    try:
        db = get_mongo_db()
        from datetime import datetime
        note_doc = {
            "personId": person_id,
            "text": note.text,
            "category": note.category,
            "createdBy": note.createdBy,
            "created": datetime.utcnow(),
        }
        result = db["personNotes"].insert_one(note_doc)
        return PersonNote(
            id=str(result.inserted_id),
            personId=person_id,
            text=note.text,
            category=note.category,
            createdBy=note.createdBy,
            created=note_doc["created"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

# --- Query Type ---

@strawberry.type
class Query:
    """Defines all read operations (queries) in the GraphQL API."""
    
    # People queries
    people: List[Person] = strawberry.field(
        resolver=get_all_people_resolver,
        description="Retrieves a list of all people from MySQL."
    )
    
    person: Optional[Person] = strawberry.field(
        resolver=get_person_by_id_resolver,
        description="Retrieves a specific person by their ID from MySQL."
    )
    
    # Event queries
    events: List[Event] = strawberry.field(
        resolver=get_all_events_resolver,
        description="Retrieves a list of all events from MySQL."
    )
    
    event: Optional[Event] = strawberry.field(
        resolver=get_event_by_id_resolver,
        description="Retrieves a specific event by ID from MySQL."
    )
    
    # Small group queries
    smallGroups: List[SmallGroup] = strawberry.field(
        resolver=get_all_small_groups_resolver,
        description="Retrieves a list of all small groups from MySQL."
    )
    
    smallGroup: Optional[SmallGroup] = strawberry.field(
        resolver=get_small_group_by_id_resolver,
        description="Retrieves a specific small group by ID from MySQL."
    )
    
    smallGroupMembers: List[SmallGroupMember] = strawberry.field(
        resolver=get_small_group_members_resolver,
        description="Retrieves members of a small group from MySQL."
    )
    
    smallGroupLeaders: List[SmallGroupLeader] = strawberry.field(
        resolver=get_small_group_leaders_resolver,
        description="Retrieves leaders of a small group from MySQL."
    )
    
    # Registration queries
    eventRegistrations: List[Registration] = strawberry.field(
        resolver=get_event_registrations_resolver,
        description="Retrieves all registrations for an event from MySQL."
    )
    
    # MongoDB queries
    personNotes: List[PersonNote] = strawberry.field(
        resolver=get_person_notes_resolver,
        description="Retrieves all notes for a person from MongoDB."
    )
    
    parentContacts: List[ParentContact] = strawberry.field(
        resolver=get_parent_contacts_resolver,
        description="Retrieves all parent contacts for a person from MongoDB."
    )
    
    eventNotes: List[EventNote] = strawberry.field(
        resolver=get_event_notes_resolver,
        description="Retrieves all notes/highlights for an event from MongoDB."
    )
    
    # Redis queries
    liveCheckIns: Optional[LiveCheckInSummary] = strawberry.field(
        resolver=get_live_checkins_resolver,
        description="Retrieves live check-in data from Redis and MySQL."
    )
    
    # Comprehensive query
    comprehensiveEventSummary: Optional[ComprehensiveEventSummary] = strawberry.field(
        resolver=get_comprehensive_event_summary_resolver,
        description="The Trifecta! Gets event data from MySQL, Redis, and MongoDB."
    )

# --- Mutation Type ---

@strawberry.type
class Mutation:
    """Defines all write operations (mutations) in the GraphQL API."""
    
    createPerson: Person = strawberry.field(
        resolver=create_person_resolver,
        description="Creates a new person."
    )
    
    updatePerson: Person = strawberry.field(
        resolver=update_person_resolver,
        description="Updates an existing person."
    )
    
    deletePerson: bool = strawberry.field(
        resolver=delete_person_resolver,
        description="Deletes a person. Returns true if successful."
    )
    
    createEvent: Event = strawberry.field(
        resolver=create_event_resolver,
        description="Creates a new event."
    )
    
    createSmallGroup: SmallGroup = strawberry.field(
        resolver=create_small_group_resolver,
        description="Creates a new small group."
    )
    
    registerForEvent: Registration = strawberry.field(
        resolver=register_for_event_resolver,
        description="Registers someone for an event."
    )
    
    addMemberToGroup: SmallGroupMember = strawberry.field(
        resolver=add_member_to_group_resolver,
        description="Adds a member to a small group."
    )
    
    addLeaderToGroup: SmallGroupLeader = strawberry.field(
        resolver=add_leader_to_group_resolver,
        description="Adds a leader to a small group."
    )
    
    addPersonNote: PersonNote = strawberry.field(
        resolver=add_person_note_resolver,
        description="Adds a note for a person in MongoDB."
    )

# --- Schema ---
schema = strawberry.Schema(query=Query, mutation=Mutation)

