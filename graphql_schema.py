"""
graphql_schema.py - GraphQL Schema Definition

This file defines the complete GraphQL schema for the Youth Group API.
GraphQL provides an alternative to REST APIs where clients can request exactly 
the data they need in a single query.

Key Concepts:
1. Schema: Defines the types of data that can be queried - the contract between client and server
2. Types (@strawberry.type): Building blocks representing our data models (Person, Event, etc.)
3. Query: Read operations - fetching data from MySQL, MongoDB, and Redis
4. Mutation: Write operations - creating, updating, and deleting data
5. Resolver: Functions that fetch/process data for each field (the actual database queries)
6. Input Types (@strawberry.input): Define what data clients send for mutations

How GraphQL Works:
- Client sends a query describing what data they want
- GraphQL validates the query against the schema
- Resolvers execute database queries to fetch the data
- Results are returned in the exact format requested

Example Query:
{
  people {
    id
    firstName
    lastName
  }
  events {
    id
    name
    type
  }
}

This schema integrates with three databases:
- MySQL: Structured data (people, events, registrations)
- MongoDB: Flexible documents (notes, event types)
- Redis: Real-time data (live check-ins)
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
# @strawberry.type decorator tells Strawberry this is a GraphQL type
# These types define what fields clients can request

@strawberry.type
class Person:
    """
    GraphQL type representing a person.
    
    This type maps to the Person table in MySQL.
    Fields correspond to database columns.
    Optional fields can be None (nullable in database).
    """
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
# Resolvers are called by GraphQL when a field is requested
# Each resolver executes the actual database query

def get_all_people_resolver() -> List[Person]:
    """
    Resolver to fetch all people from MySQL.
    
    How it works:
    1. Get a connection from the MySQL pool
    2. Execute SELECT query to get all people
    3. Convert database rows to Person objects
    4. Return list of Person objects
    5. GraphQL automatically serializes these to JSON
    
    Returns:
        List[Person]: All people from the database
    """
    try:
        # Get connection from pool (reuses existing connections efficiently)
        cnx = db_pool.get_connection()
        # Create cursor that returns results as dictionaries (easier to work with)
        cursor = cnx.cursor(dictionary=True)
        
        # Execute SQL query
        # AS clauses rename columns to match GraphQL field names (camelCase)
        cursor.execute("SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person ORDER BY lastName, firstName;")
        
        # Fetch all rows returned by the query
        people_data = cursor.fetchall()
        
        # Close cursor and return connection to pool
        cursor.close()
        cnx.close()
        
        # Convert database rows to Person objects
        # **p unpacks dictionary into keyword arguments for Person constructor
        # Example: Person(id=1, firstName="John", lastName="Doe", age=20)
        return [Person(**p) for p in people_data]
    except Exception as e:
        # If database error occurs, raise HTTP exception
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_person_by_id_resolver(person_id: int) -> Optional[Person]:
    """
    Resolver to fetch a specific person by their ID from MySQL.
    
    Args:
        person_id: The ID of the person to fetch
        
    Returns:
        Person object if found, None if person doesn't exist
        
    Database Pattern:
    1. Execute SELECT query with WHERE clause filtering by ID
    2. Use fetchone() since we expect at most one result
    3. Return None if person not found (GraphQL handles this gracefully)
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Query with WHERE clause to filter by ID
        # %s placeholder prevents SQL injection
        cursor.execute("SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s;", (person_id,))
        person_data = cursor.fetchone()  # Get single row (or None if not found)
        cursor.close()
        cnx.close()
        if not person_data:
            return None  # Person doesn't exist
        return Person(**person_data)  # Convert dict to Person object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_all_events_resolver() -> List[Event]:
    """
    Resolver to fetch all events from MySQL, ordered by most recent first.
    
    Returns:
        List[Event]: All events from the database, newest first
        
    Database Pattern:
    1. Execute SELECT query for all events
    2. ORDER BY DateTime DESC sorts newest events first
    3. Convert all rows to Event objects
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Query all events, ordered by date/time (newest first)
        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event
            ORDER BY DateTime DESC;
        """)
        events_data = cursor.fetchall()  # Get all rows
        cursor.close()
        cnx.close()
        return [Event(**e) for e in events_data]  # Convert each row to Event object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_event_by_id_resolver(event_id: int) -> Optional[Event]:
    """
    Resolver to fetch a specific event by its ID from MySQL.
    
    Args:
        event_id: The ID of the event to fetch
        
    Returns:
        Event object if found, None if event doesn't exist
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Query event by ID
        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event
            WHERE ID = %s;
        """, (event_id,))
        event_data = cursor.fetchone()  # Get single row
        cursor.close()
        cnx.close()
        if not event_data:
            return None  # Event doesn't exist
        return Event(**event_data)  # Convert dict to Event object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_all_small_groups_resolver() -> List[SmallGroup]:
    """
    Resolver to fetch all small groups from MySQL, ordered alphabetically by name.
    
    Returns:
        List[SmallGroup]: All small groups, sorted by name
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Query all groups, ordered alphabetically
        cursor.execute("SELECT ID AS id, Name AS name FROM SmallGroup ORDER BY name;")
        groups_data = cursor.fetchall()
        cursor.close()
        cnx.close()
        return [SmallGroup(**g) for g in groups_data]  # Convert to SmallGroup objects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_small_group_by_id_resolver(group_id: int) -> Optional[SmallGroup]:
    """
    Resolver to fetch a specific small group by its ID from MySQL.
    
    Args:
        group_id: The ID of the small group to fetch
        
    Returns:
        SmallGroup object if found, None if group doesn't exist
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Query group by ID
        cursor.execute("SELECT ID AS id, Name AS name FROM SmallGroup WHERE ID = %s;", (group_id,))
        group_data = cursor.fetchone()
        cursor.close()
        cnx.close()
        if not group_data:
            return None  # Group doesn't exist
        return SmallGroup(**group_data)  # Convert dict to SmallGroup object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_small_group_members_resolver(group_id: int) -> List[SmallGroupMember]:
    """
    Resolver to fetch all members of a small group using JOINs.
    
    This demonstrates complex SQL JOINs:
    - SmallGroupMember links attendees to groups
    - Attendee links to Person
    - JOINs combine data from multiple tables
    
    Args:
        group_id: The ID of the small group
        
    Returns:
        List[SmallGroupMember]: All members with their names included
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Complex JOIN query:
        # 1. Start with SmallGroupMember table
        # 2. JOIN Attendee to get PersonID
        # 3. JOIN Person to get FirstName/LastName
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
        return [SmallGroupMember(**m) for m in members_data]  # Convert to objects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def get_small_group_leaders_resolver(group_id: int) -> List[SmallGroupLeader]:
    """
    Resolver to fetch all leaders of a small group using JOINs.
    
    Similar to members resolver but for leaders:
    - SmallGroupLeader links leaders to groups
    - JOIN Person to get leader names
    
    Args:
        group_id: The ID of the small group
        
    Returns:
        List[SmallGroupLeader]: All leaders with their names included
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # JOIN query to get leader names:
        # SmallGroupLeader -> Person (LeaderID is Person.ID)
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
        return [SmallGroupLeader(**l) for l in leaders_data]  # Convert to objects
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
    """
    Resolver to fetch notes for a person from MongoDB.
    
    This demonstrates MongoDB integration:
    - MongoDB stores flexible documents (can have different fields)
    - Uses .get() with defaults for optional fields
    - Converts MongoDB ObjectId to string for GraphQL
    
    Args:
        person_id: The ID of the person to get notes for
        
    Returns:
        List[PersonNote]: All notes for the person
    """
    try:
        # Get MongoDB database instance
        db = get_mongo_db()
        
        # Query MongoDB collection
        # find() with filter returns cursor, convert to list
        # {"personId": person_id} is the query filter (like WHERE clause)
        notes = list(db["personNotes"].find({"personId": person_id}))
        
        # Convert MongoDB documents to PersonNote objects
        result = []
        for note in notes:
            result.append(PersonNote(
                id=str(note["_id"]),              # Convert ObjectId to string
                personId=note["personId"],        # Required field
                text=note.get("text", ""),        # .get() with default for optional fields
                category=note.get("category"),    # Returns None if field doesn't exist
                createdBy=note.get("createdBy"),
                created=note.get("created"),
                updated=note.get("updated")
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

def get_parent_contacts_resolver(person_id: int) -> List[ParentContact]:
    """
    Resolver to fetch parent contacts for a person from MongoDB.
    
    Parent contacts are stored in MongoDB because they have flexible fields:
    - method (phone, email, in-person, etc.)
    - summary (free-form text)
    - date (optional contact date)
    - Metadata (createdBy, created, updated)
    
    Args:
        person_id: The ID of the person to get contacts for
        
    Returns:
        List[ParentContact]: All parent contact records for the person
    """
    try:
        db = get_mongo_db()
        # Query MongoDB collection with filter
        contacts = list(db["parentContacts"].find({"personId": person_id}))
        result = []
        # Convert MongoDB documents to ParentContact objects
        for contact in contacts:
            result.append(ParentContact(
                id=str(contact["_id"]),              # Convert ObjectId to string
                personId=contact["personId"],        # Required field
                method=contact.get("method"),        # Optional field
                summary=contact.get("summary", ""),  # Required with default
                date=contact.get("date"),            # Optional field
                createdBy=contact.get("createdBy"),  # Optional metadata
                created=contact.get("created"),      # Optional timestamp
                updated=contact.get("updated")        # Optional timestamp
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

def get_event_notes_resolver(event_id: int) -> List[EventNote]:
    """
    Resolver to fetch notes/highlights for an event from MongoDB.
    
    Event notes are stored in MongoDB with flexible fields:
    - notes: General event notes
    - concerns: Any concerns from the event
    - studentWins: Positive highlights/achievements
    - Metadata: createdBy, created, updated timestamps
    
    Args:
        event_id: The ID of the event to get notes for
        
    Returns:
        List[EventNote]: All notes/highlights for the event
    """
    try:
        db = get_mongo_db()
        # Query MongoDB collection
        notes = list(db["eventNotes"].find({"eventId": event_id}))
        result = []
        # Convert MongoDB documents to EventNote objects
        for note in notes:
            result.append(EventNote(
                id=str(note["_id"]),                    # Convert ObjectId to string
                eventId=note["eventId"],                # Required field
                notes=note.get("notes"),                # Optional field
                concerns=note.get("concerns"),          # Optional field
                studentWins=note.get("studentWins"),     # Optional field
                createdBy=note.get("createdBy"),       # Optional metadata
                created=note.get("created"),            # Optional timestamp
                updated=note.get("updated")              # Optional timestamp
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

def get_live_checkins_resolver(event_id: int) -> Optional[LiveCheckInSummary]:
    """
    Resolver to fetch live check-ins from Redis (combines Redis + MySQL).
    
    This demonstrates multi-database integration:
    1. Get checked-in student IDs from Redis SET
    2. Get check-in timestamps from Redis HASH
    3. Query MySQL to get student details (name, etc.)
    4. Combine Redis and MySQL data into response
    
    Why Redis for check-ins?
    - Very fast (in-memory)
    - Perfect for real-time data
    - SET stores unique student IDs
    - HASH stores timestamps
    
    Args:
        event_id: The event ID to get check-ins for
        
    Returns:
        LiveCheckInSummary or None if no check-ins or Redis unavailable
    """
    try:
        # Get Redis client
        r = get_redis_conn()
        
        # Define Redis keys using naming convention
        checked_in_key = f"event:{event_id}:checkedIn"      # SET: student IDs
        times_key = f"event:{event_id}:checkInTimes"         # HASH: ID -> timestamp
        
        # SMEMBERS: Get all members of the SET (all checked-in student IDs)
        student_ids = r.smembers(checked_in_key)
        if not student_ids:
            return None  # No one checked in
        
        # HGETALL: Get all key-value pairs from HASH (all timestamps)
        timestamps = r.hgetall(times_key)
        
        # Convert Redis strings to integers for MySQL query
        student_ids_int = [int(sid) for sid in student_ids]
        
        # Query MySQL to get student details (names, etc.)
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        
        # Build dynamic IN clause for SQL query
        # Format: "SELECT ... WHERE ID IN (%s, %s, %s)"
        format_strings = ",".join(["%s"] * len(student_ids_int))
        query = f"SELECT ID, FirstName, LastName FROM Person WHERE ID IN ({format_strings});"
        cursor.execute(query, tuple(student_ids_int))
        people = cursor.fetchall()
        cursor.close()
        cnx.close()
        
        # Combine Redis timestamps with MySQL student data
        students = [
            CheckedInStudent(
                studentId=p["ID"],
                firstName=p["FirstName"],
                lastName=p["LastName"],
                checkInTime=timestamps.get(str(p["ID"]))  # Get timestamp from Redis hash
            )
            for p in people
        ]
        
        # Return combined summary
        return LiveCheckInSummary(
            eventId=event_id,
            count=len(students),
            students=students,
            message=f"{len(students)} students are currently checked in."
        )
    except redis.RedisError as e:
        # Redis might not be available - return None instead of crashing
        return None
    except Exception as e:
        # Any other error - return None
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
    """
    Resolver to create a new person in MySQL.
    
    Mutation Pattern:
    1. Execute INSERT query with provided data
    2. Commit transaction (saves to database)
    3. Get generated ID using cursor.lastrowid
    4. Query database to get complete person record
    5. Return the new person object
    
    Args:
        person: PersonCreateInput with firstName, lastName, and optional age
        
    Returns:
        Person: The newly created person with generated ID
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # INSERT query with placeholders (%s) to prevent SQL injection
        cursor.execute("""
            INSERT INTO Person (FirstName, LastName, Age)
            VALUES (%s, %s, %s)
        """, (person.firstName, person.lastName, person.age))
        cnx.commit()  # Save changes to database
        
        # Get the auto-generated ID of the newly inserted row
        person_id = cursor.lastrowid
        
        # Query database to get complete person record (with generated ID)
        cursor.execute(
            "SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s",
            (person_id,)
        )
        new_person = cursor.fetchone()
        cursor.close()
        cnx.close()
        return Person(**new_person)  # Convert dict to Person object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def update_person_resolver(person_id: int, person: PersonUpdateInput) -> Person:
    """
    Resolver to update a person partially (only provided fields are updated).
    
    This demonstrates dynamic SQL building:
    - Only updates fields that are provided (not None)
    - Builds UPDATE query dynamically based on provided fields
    - Allows partial updates (PATCH semantics)
    
    Args:
        person_id: The ID of the person to update
        person: PersonUpdateInput with optional fields to update
        
    Returns:
        Person: The updated person object
        
    Raises:
        HTTPException 404: If person not found
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        
        # Verify person exists before updating
        cursor.execute("SELECT * FROM Person WHERE ID = %s;", (person_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Build update query dynamically - only include fields that are provided
        fields = []  # List of "ColumnName = %s" strings
        values = []  # List of values to update
        
        if person.firstName is not None:
            fields.append("FirstName = %s")
            values.append(person.firstName)
        if person.lastName is not None:
            fields.append("LastName = %s")
            values.append(person.lastName)
        if person.age is not None:
            fields.append("Age = %s")
            values.append(person.age)
        
        # Only execute UPDATE if there are fields to update
        if fields:
            # Build SQL: "UPDATE Person SET Field1 = %s, Field2 = %s WHERE ID = %s"
            sql = f"UPDATE Person SET {', '.join(fields)} WHERE ID = %s"
            values.append(person_id)  # Add ID for WHERE clause
            cursor.execute(sql, values)
            cnx.commit()  # Save changes
        
        # Query database to get updated record
        cursor.execute("SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s;", (person_id,))
        updated = cursor.fetchone()
        cursor.close()
        cnx.close()
        return Person(**updated)  # Convert dict to Person object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def delete_person_resolver(person_id: int) -> bool:
    """
    Resolver to delete a person from MySQL.
    
    Deletion Pattern:
    1. Verify person exists before deleting
    2. Execute DELETE query
    3. Commit transaction
    4. Return True if successful
    
    Args:
        person_id: The ID of the person to delete
        
    Returns:
        bool: True if deletion successful
        
    Raises:
        HTTPException 404: If person not found
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        # Verify person exists before attempting deletion
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Delete the person
        cursor.execute("DELETE FROM Person WHERE ID = %s;", (person_id,))
        cnx.commit()  # Save deletion to database
        cursor.close()
        cnx.close()
        return True  # Success
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def create_event_resolver(event: EventCreateInput) -> Event:
    """
    Resolver to create a new event in MySQL.
    
    Args:
        event: EventCreateInput with name, type, dateTime, location, and optional notes
        
    Returns:
        Event: The newly created event with generated ID
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # INSERT event with all required fields
        cursor.execute("""
            INSERT INTO Event (Name, Type, DateTime, Location, Notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (event.name, event.type, event.dateTime, event.location, event.notes))
        cnx.commit()  # Save changes
        
        # Get generated ID
        event_id = cursor.lastrowid
        
        # Query to get complete event record
        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event WHERE ID = %s
        """, (event_id,))
        new_event = cursor.fetchone()
        cursor.close()
        cnx.close()
        return Event(**new_event)  # Convert dict to Event object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def create_small_group_resolver(group: SmallGroupCreateInput) -> SmallGroup:
    """
    Resolver to create a new small group in MySQL.
    
    This demonstrates manual ID generation:
    - SmallGroup table doesn't use AUTO_INCREMENT
    - We manually calculate next ID: MAX(ID) + 1
    - IFNULL handles case where table is empty (returns 0 + 1 = 1)
    
    Args:
        group: SmallGroupCreateInput with name
        
    Returns:
        SmallGroup: The newly created group with generated ID
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        # Manually calculate next ID (since no AUTO_INCREMENT)
        # IFNULL handles empty table case (returns 0 if MAX returns NULL)
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroup;")
        next_id = cursor.fetchone()[0]  # Get first column of first row
        
        # Insert new group with calculated ID
        cursor.execute("INSERT INTO SmallGroup (ID, Name) VALUES (%s, %s);", (next_id, group.name.strip()))
        cnx.commit()  # Save changes
        cursor.close()
        cnx.close()
        return SmallGroup(id=next_id, name=group.name.strip())  # Return new group
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
    """
    Resolver to add a member (attendee) to a small group.
    
    Creates a relationship between an Attendee and a SmallGroup.
    Note: attendeeId should be an Attendee ID (not Person ID).
    
    Args:
        group_id: The ID of the small group
        input: AddMemberToGroupInput with attendeeId
        
    Returns:
        SmallGroupMember: The newly created membership record
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        # Calculate next ID manually
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroupMember;")
        next_id = cursor.fetchone()[0]
        
        # Insert membership record linking attendee to group
        cursor.execute("""
            INSERT INTO SmallGroupMember (ID, AttendeeID, SmallGroupID)
            VALUES (%s, %s, %s);
        """, (next_id, input.attendeeId, group_id))
        cnx.commit()  # Save membership
        cursor.close()
        cnx.close()
        return SmallGroupMember(id=next_id, attendeeId=input.attendeeId, smallGroupId=group_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def add_leader_to_group_resolver(group_id: int, input: AddLeaderToGroupInput) -> SmallGroupLeader:
    """
    Resolver to add a leader to a small group.
    
    Creates a relationship between a Leader and a SmallGroup.
    Note: leaderId should be a Leader ID (not Person ID).
    
    Args:
        group_id: The ID of the small group
        input: AddLeaderToGroupInput with leaderId
        
    Returns:
        SmallGroupLeader: The newly created leadership record
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        # Calculate next ID manually
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroupLeader;")
        next_id = cursor.fetchone()[0]
        
        # Insert leadership record linking leader to group
        cursor.execute("""
            INSERT INTO SmallGroupLeader (ID, LeaderID, SmallGroupID)
            VALUES (%s, %s, %s);
        """, (next_id, input.leaderId, group_id))
        cnx.commit()  # Save leadership assignment
        cursor.close()
        cnx.close()
        return SmallGroupLeader(id=next_id, leaderId=input.leaderId, smallGroupId=group_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

def add_person_note_resolver(person_id: int, note: PersonNoteInput) -> PersonNote:
    """
    Resolver to add a note for a person in MongoDB.
    
    Notes are stored in MongoDB because they have flexible fields:
    - text: The note content
    - category: Optional categorization
    - createdBy: Who created the note
    - created: Timestamp (automatically set)
    
    Args:
        person_id: The ID of the person to add a note for
        note: PersonNoteInput with note content and metadata
        
    Returns:
        PersonNote: The newly created note with generated MongoDB _id
    """
    try:
        db = get_mongo_db()
        from datetime import datetime
        
        # Build MongoDB document
        note_doc = {
            "personId": person_id,
            "text": note.text,
            "category": note.category,           # Optional field
            "createdBy": note.createdBy,         # Optional field
            "created": datetime.utcnow(),         # Auto-set timestamp
        }
        
        # Insert document into MongoDB collection
        # insert_one() returns result with inserted_id
        result = db["personNotes"].insert_one(note_doc)
        
        # Return PersonNote object with MongoDB _id converted to string
        return PersonNote(
            id=str(result.inserted_id),  # Convert ObjectId to string
            personId=person_id,
            text=note.text,
            category=note.category,
            createdBy=note.createdBy,
            created=note_doc["created"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")

# --- Query Type ---
# The Query type defines all read operations (GET requests in REST terms)
# Each field in Query corresponds to a resolver function

@strawberry.type
class Query:
    """
    Defines all read operations (queries) in the GraphQL API.
    
    Query fields are read-only - they fetch data but don't modify it.
    Each field maps to a resolver function that executes the database query.
    
    Example query:
    {
      people {
        id
        firstName
        lastName
      }
    }
    """
    
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
# The Mutation type defines all write operations (POST/PUT/DELETE in REST terms)
# Mutations modify data - create, update, or delete records

@strawberry.type
class Mutation:
    """
    Defines all write operations (mutations) in the GraphQL API.
    
    Mutation fields modify data - they create, update, or delete records.
    Each field maps to a resolver function that executes the database operation.
    
    Example mutation:
    mutation {
      createPerson(firstName: "John", lastName: "Doe", age: 20) {
        id
        firstName
      }
    }
    """
    
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
# The schema combines Query and Mutation types
# This is what GraphQL uses to validate queries and route them to resolvers
schema = strawberry.Schema(query=Query, mutation=Mutation)

