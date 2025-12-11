"""
youthGroupFastAPI.py - Main FastAPI Application

This is the main REST API server for the Youth Group management system.
It provides endpoints for managing people, events, registrations, small groups,
and integrates with three database systems:

1. MySQL - Structured relational data (people, events, registrations, small groups)
2. MongoDB - Flexible document data (event types, notes, parent contacts)
3. Redis - Real-time in-memory data (live check-ins)

API Design:
- RESTful endpoints (GET, POST, PUT, PATCH, DELETE)
- Pydantic models for request/response validation
- Connection pooling for efficient database access
- Error handling with HTTP status codes
- CORS enabled for frontend integration

Key Patterns:
- Connection Pooling: Reuses database connections (see database.py)
- Try/Finally: Always closes connections even if errors occur
- Dictionary Cursors: Returns results as dicts (easier than tuples)
- Dynamic SQL: Builds UPDATE queries based on provided fields
"""

import mysql.connector
import redis
from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
from datetime import datetime

# --- Database Configuration ---
# Import database credentials from config.py (keeps secrets separate)
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, REDIS_SSL, REDIS_USERNAME, REDIS_PORT, \
    REDIS_PASSWORD, REDIS_HOST, MONGO_URI
from database import get_mysql_pool, get_mongo_client, close_connections, get_mongo_db, get_redis_conn, \
    get_redis_client, get_db_connection

# --- Connection Pooling ---
# Create MySQL connection pool at startup
# Pool maintains 5 connections that are reused for all requests
# This is MUCH more efficient than creating a new connection for each request
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="fastapi_pool",  # Name for this pool
        pool_size=30,  # Maximum connections in pool
        user=DB_USER,  # Database username
        password=DB_PASSWORD,  # Database password
        host=DB_HOST,  # Database server address
        port=DB_PORT,  # Database server port
        database=DB_NAME  # Database name
    )
    print("Database connection pool created successfully.")
except mysql.connector.Error as err:
    # If pool creation fails, exit (can't run without database)
    print(f"Error creating connection pool: {err}")
    exit()


# --- App Lifecycle Management ---
# @asynccontextmanager handles startup and shutdown events
# This ensures databases are initialized when app starts and closed when app stops
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application lifecycle - startup and shutdown.
    
    Startup: Initialize all database connections
    Shutdown: Close all database connections gracefully
    """
    # Startup: Initialize all database connections
    print("Application startup: Initializing database connections...")
    get_mysql_pool()  # Initialize MySQL pool (already done above, but ensures it exists)
    get_mongo_client()  # Initialize MongoDB client
    # get_redis_client()  # Redis can be initialized on-demand if needed
    yield  # App runs here
    # Shutdown: Close all database connections
    print("Application shutdown: Closing database connections...")
    close_connections()  # Clean up all connections


# --- FastAPI App ---
# Create the FastAPI application instance
# This is the main app object that handles all HTTP requests
app = FastAPI(
    title="Youth Group API",
    description="An API for interacting with the YouthGroupDB database.",
    version="1.0.0",
    lifespan=lifespan  # Use our lifespan manager for startup/shutdown
)

# --- CORS Middleware ---
# CORS (Cross-Origin Resource Sharing) allows the frontend to call this API
# Frontend runs on different port (e.g., localhost:3000) than API (localhost:8099)
# Without CORS, browser blocks these requests for security
# This will allow the frontend (running on a different origin) to communicate with the API.
# For demonstration purposes, we allow all origins, methods, and headers.
# In production, restrict this to your frontend's domain for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (in production, use specific domain)
    allow_credentials=True,  # Allow cookies/authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# --- Pydantic Models (for request/response validation) ---
# Pydantic models define the structure of request/response data
# FastAPI automatically validates incoming requests against these models
# If data doesn't match, FastAPI returns 422 error with details

class Person(BaseModel):
    """
    Pydantic model representing a Person.
    Used for API request/response validation.
    Fields must match database columns (with camelCase conversion).
    """
    id: int  # Primary key
    firstName: str  # Required field (not nullable)
    lastName: str  # Required field (not nullable)
    age: int | None = None  # Optional field (can be null)


class PersonCreate(BaseModel):
    firstName: str
    lastName: str
    age: int | None = None


class Volunteer(BaseModel):
    id: int
    personID: int


class Attendee(BaseModel):
    id: int
    personID: int
    guardian: str


class Leader(BaseModel):
    id: int
    personID: int


class SmallGroup(BaseModel):
    id: int
    name: str


class SmallGroupMember(BaseModel):
    id: int
    attendeeID: int
    smallGroupID: int


class SmallGroupLeader(BaseModel):
    id: int
    leaderID: int
    smallGroupID: int


class Event(BaseModel):
    id: int
    name: str
    type: str
    dateTime: datetime
    location: str
    notes: str | None


class Registration(BaseModel):
    id: int
    eventID: int
    attendeeID: int | None
    leaderID: int | None
    emergencyContact: str


class AttendanceRecord(BaseModel):
    id: int
    personID: int
    eventID: int


class EventCreate(BaseModel):
    name: str
    type: str
    dateTime: datetime
    location: str
    notes: str | None = None


class EventUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    dateTime: datetime | None = None
    location: str | None = None
    notes: str | None = None


# --- Pydantic Models for MongoDB Data ---
from typing import List, Optional, Any
from datetime import datetime
from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Return a Pydantic CoreSchema that defines how to validate and serialize ObjectIds.
        """
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        """Validate that the input is a valid ObjectId."""
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


# pydantic model for mongodb
class EventTypeQuery(BaseModel):
    event_type: str


# pydantic models for redis
class CheckedInStudent(BaseModel):
    studentId: int
    firstName: str
    lastName: str
    checkInTime: Optional[str] = None


class LiveCheckInSummary(BaseModel):
    eventId: int
    count: int
    students: List[CheckedInStudent]
    message: str


# --- API Endpoints ---
@app.get("/")
def read_root():
    """
    Root endpoint with a welcome message.
    """
    return {"message": "Welcome to the YouthGroup API!"}


@app.get("/people", response_model=list[Person])
def get_all_people():
    """
    Retrieves a list of all people from the database.
    
    Endpoint: GET /people
    Returns: List of Person objects
    
    Database Pattern:
    1. Get connection from pool
    2. Create cursor (dictionary=True returns dicts instead of tuples)
    3. Execute SELECT query
    4. Fetch all results
    5. Close cursor and connection (returns connection to pool)
    
    Note: Always use try/finally to ensure connections are closed even if errors occur
    """
    try:
        # Get connection from pool (reuses existing connections)
        cnx = db_pool.get_connection()
        # Create cursor that returns results as dictionaries (easier to work with)
        cursor = cnx.cursor(dictionary=True)

        # Execute SQL query
        # AS clauses rename columns to match Pydantic model fields (camelCase)
        cursor.execute("SELECT ID AS id, firstName, lastName, age FROM Person ORDER BY lastName, firstName;")

        # Fetch all rows returned by query
        people = cursor.fetchall()
        return people  # FastAPI automatically converts to JSON
    except mysql.connector.Error as err:
        # If database error, return 500 status with error message
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/people/{person_id}", response_model=Person)
def get_person_by_id(person_id: int):
    """
    Retrieves a specific person by their ID.
    
    Endpoint: GET /people/{person_id}
    Path Parameter: person_id - The ID of the person to retrieve
    Returns: Person object if found
    
    Raises:
        HTTPException 404: If person not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Query with WHERE clause to filter by ID
        query = "SELECT ID AS id, firstName, lastName, age FROM Person WHERE ID = %s;"
        cursor.execute(query, (person_id,))
        person = cursor.fetchone()  # Get single row (or None if not found)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.post("/people", response_model=Person, status_code=201)
def create_person(person: PersonCreate):
    """
    Creates a new person in the database.
    
    Endpoint: POST /people
    Request Body: PersonCreate (firstName, lastName, age)
    Returns: Created Person object with generated ID
    
    Database Pattern:
    1. Execute INSERT query with provided data
    2. Commit transaction (saves to database)
    3. Get generated ID using cursor.lastrowid
    4. Query database to get complete person record
    5. Return the new person
    
    Note: Must commit() after INSERT/UPDATE/DELETE to save changes
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # INSERT query with placeholders (%s) for values
        # This prevents SQL injection attacks
        insert_query = """
            INSERT INTO Person (FirstName, LastName, Age)
            VALUES (%s, %s, %s)
        """
        # Execute with tuple of values (in order matching placeholders)
        cursor.execute(insert_query, (person.firstName, person.lastName, person.age))

        # Commit transaction - saves changes to database
        # Without commit(), changes are rolled back when connection closes
        cnx.commit()

        # Get the auto-generated ID of the newly inserted row
        person_id = cursor.lastrowid

        # Query database to get the complete person record (with generated ID)
        cursor.execute(
            "SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s",
            (person_id,)
        )
        new_person = cursor.fetchone()
        return new_person

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.put("/people/{person_id}", response_model=Person)
def update_person(person_id: int, person: PersonCreate):
    """
    Updates a person (full update - all fields must be provided).
    
    Endpoint: PUT /people/{person_id}
    Path Parameter: person_id - The ID of the person to update
    Request Body: PersonCreate with all fields (firstName, lastName, age)
    Returns: Updated Person object
    
    PUT vs PATCH:
    - PUT: Full update (all fields required, replaces entire record)
    - PATCH: Partial update (only provided fields updated)
    
    Raises:
        HTTPException 404: If person not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Verify person exists before updating
        cursor.execute("SELECT * FROM Person WHERE ID = %s;", (person_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Person not found")

        # UPDATE query - updates all fields
        update_query = """
            UPDATE Person
            SET FirstName = %s, LastName = %s, Age = %s
            WHERE ID = %s;
        """
        cursor.execute(update_query, (person.firstName, person.lastName, person.age, person_id))
        cnx.commit()  # Save changes

        # Query to get updated record
        cursor.execute(
            "SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s;",
            (person_id,))
        updated = cursor.fetchone()
        return updated
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/people/{person_id}")
def delete_person(person_id: int):
    """
    Deletes a person by ID.
    
    Endpoint: DELETE /people/{person_id}
    Path Parameter: person_id - The ID of the person to delete
    Returns: Success message
    
    Deletion Pattern:
    1. Verify person exists before deleting
    2. Execute DELETE query
    3. Commit transaction
    4. Return success message
    
    Raises:
        HTTPException 404: If person not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # Verify person exists before attempting deletion
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Person not found")

        # Delete the person
        cursor.execute("DELETE FROM Person WHERE ID = %s;", (person_id,))
        cnx.commit()  # Save deletion
        return {"message": f"Person {person_id} deleted successfully."}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


# registrations:
@app.get("/events/{event_id}/registrations")
def get_registrations_for_event(event_id: int):
    """
    Gets all registrations for an event, including person names.
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Try to include VolunteerID, fallback if column doesn't exist
        try:
            query = """
                SELECT R.ID AS id,
                       R.EventID AS eventId,
                       R.AttendeeID AS attendeeId,
                       R.LeaderID AS leaderId,
                       R.VolunteerID AS volunteerId,
                       R.EmergencyContact AS emergencyContact,
                       P.FirstName AS firstName,
                       P.LastName AS lastName
                FROM Registration R
                LEFT JOIN Attendee A ON R.AttendeeID = A.ID
                LEFT JOIN Leader L ON R.LeaderID = L.ID
                LEFT JOIN Volunteer V ON R.VolunteerID = V.ID
                LEFT JOIN Person P ON (A.PersonID = P.ID OR L.PersonID = P.ID OR V.PersonID = P.ID)
                WHERE R.EventID = %s;
            """
            cursor.execute(query, (event_id,))
        except mysql.connector.Error:
            # Fallback if VolunteerID column doesn't exist
            query = """
                SELECT R.ID AS id,
                       R.EventID AS eventId,
                       R.AttendeeID AS attendeeId,
                       R.LeaderID AS leaderId,
                       NULL AS volunteerId,
                       R.EmergencyContact AS emergencyContact,
                       P.FirstName AS firstName,
                       P.LastName AS lastName
                FROM Registration R
                LEFT JOIN Attendee A ON R.AttendeeID = A.ID
                LEFT JOIN Leader L ON R.LeaderID = L.ID
                LEFT JOIN Person P ON (A.PersonID = P.ID OR L.PersonID = P.ID)
                WHERE R.EventID = %s;
            """
            cursor.execute(query, (event_id,))

        return cursor.fetchall()

    except mysql.connector.Error as err:
        raise HTTPException(500, f"DB error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


# register for an event:
@app.post("/events/{event_id}/registrations")
def register_for_event(event_id: int, body: dict):
    """
    Registers either an attendee, leader, or volunteer for an event.
    
    Endpoint: POST /events/{event_id}/registrations
    Path Parameter: event_id - The ID of the event to register for
    Request Body: dict with:
        - attendeeID (optional): ID of attendee registering
        - leaderID (optional): ID of leader registering
        - volunteerID (optional): ID of volunteer registering
        - emergencyContact (required): Emergency contact information
    
    Registration Rules:
    - Must provide at least one role ID (attendeeID, leaderID, or volunteerID)
    - emergencyContact is required
    - Manually calculates next ID (no AUTO_INCREMENT)
    
    Schema Evolution:
    - Tries to include VolunteerID if provided (newer schema)
    - Falls back to basic registration if VolunteerID column doesn't exist
    
    Returns: Success message with registration ID
    
    Raises:
        HTTPException 400: If validation fails or VolunteerID column missing
        HTTPException 500: If database error occurs
    """
    attendee_id = body.get("attendeeID")
    leader_id = body.get("leaderID")
    volunteer_id = body.get("volunteerID")
    emergency_contact = body.get("emergencyContact")

    # Validation: must have at least one role
    if not attendee_id and not leader_id and not volunteer_id:
        raise HTTPException(400, "Must include attendeeID, leaderID, or volunteerID")

    # Validation: emergency contact required
    if not emergency_contact:
        raise HTTPException(400, "Missing emergencyContact")

    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # 1. Manually calculate next ID (no AUTO_INCREMENT)
        cursor.execute("SELECT IFNULL(MAX(ID),0) + 1 AS nextId FROM Registration;")
        next_id = cursor.fetchone()[0]

        # 2. Try to insert with VolunteerID if volunteer_id is provided
        if volunteer_id:
            try:
                insert_query = """
                    INSERT INTO Registration (ID, EventID, AttendeeID, LeaderID, VolunteerID, EmergencyContact)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query,
                               (next_id, event_id, attendee_id, leader_id, volunteer_id, emergency_contact))
            except mysql.connector.Error as err:
                # If VolunteerID column doesn't exist, raise a helpful error
                if "Unknown column 'VolunteerID'" in str(err) or "1054" in str(err):
                    raise HTTPException(400,
                                        "Volunteer registration requires VolunteerID column in Registration table. Please run the migration script.")
                raise
        else:
            # Regular attendee/leader registration (without VolunteerID)
            insert_query = """
                INSERT INTO Registration (ID, EventID, AttendeeID, LeaderID, EmergencyContact)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (next_id, event_id, attendee_id, leader_id, emergency_contact))

        cnx.commit()  # Save registration

        return {"message": "Registration created successfully", "id": next_id}

    except mysql.connector.Error as err:
        raise HTTPException(500, f"DB error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


# delete registration:
@app.delete("/registrations/{registration_id}")
def delete_registration(registration_id: int):
    """
    Deletes a registration record by ID.
    
    Endpoint: DELETE /registrations/{registration_id}
    Path Parameter: registration_id - The ID of the registration to delete
    Returns: Success message
    
    Raises:
        HTTPException 404: If registration not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Verify registration exists before deleting
        cursor.execute("SELECT ID FROM Registration WHERE ID = %s;", (registration_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Registration not found")

        # Delete the registration
        cursor.execute("DELETE FROM Registration WHERE ID = %s;", (registration_id,))
        cnx.commit()  # Save deletion

        return {"message": "Registration deleted successfully"}

    except mysql.connector.Error as err:
        raise HTTPException(500, f"DB error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/volunteers")
def get_all_volunteers():
    """
    Gets all volunteers
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT V.ID AS id,
                   V.PersonID AS personId,
                   P.FirstName AS firstName,
                   P.LastName AS lastName
            FROM Volunteer V
            JOIN Person P ON V.PersonID = P.ID;
        """)
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/volunteers/{volunteer_id}")
def get_volunteer_by_id(volunteer_id: int):
    """
    Gets a specific volunteer by ID with their person information.
    
    Endpoint: GET /volunteers/{volunteer_id}
    Path Parameter: volunteer_id - The ID of the volunteer
    Returns: Volunteer object with name included
    
    Raises:
        HTTPException 404: If volunteer not found
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # JOIN query with WHERE clause to filter by volunteer ID
        cursor.execute("""
            SELECT V.ID AS id,
                   V.PersonID AS personId,
                   P.FirstName AS firstName,
                   P.LastName AS lastName
            FROM Volunteer V
            JOIN Person P ON V.PersonID = P.ID
            WHERE V.ID = %s;
        """, (volunteer_id,))
        volunteer = cursor.fetchone()
        if not volunteer:
            raise HTTPException(status_code=404, detail="Volunteer not found")
        return volunteer
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/attendees")
def get_all_attendees():
    """
    Gets all attendees with their person information, ordered alphabetically.
    
    Endpoint: GET /attendees
    Returns: List of attendees with names and guardian information
    
    JOIN Pattern:
    - Attendee table links to Person via PersonID
    - Includes guardian field (unique to attendees)
    - Ordered by last name, then first name
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # JOIN query with ORDER BY for alphabetical sorting
        cursor.execute("""
            SELECT A.ID AS id,
                   A.PersonID AS personId,
                   P.FirstName AS firstName,
                   P.LastName AS lastName,
                   A.Guardian AS guardian
            FROM Attendee A
            JOIN Person P ON A.PersonID = P.ID
            ORDER BY P.LastName, P.FirstName;
        """)
        attendees = cursor.fetchall()
        return attendees
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/leaders")
def get_all_leaders():
    """
    Gets all leaders with their person information, ordered alphabetically.
    
    Endpoint: GET /leaders
    Returns: List of leaders with names included
    
    JOIN Pattern:
    - Leader table links to Person via PersonID
    - Ordered by last name, then first name
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        # JOIN query with ORDER BY for alphabetical sorting
        cursor.execute("""
            SELECT L.ID AS id,
                   L.PersonID AS personId,
                   P.FirstName AS firstName,
                   P.LastName AS lastName
            FROM Leader L
            JOIN Person P ON L.PersonID = P.ID
            ORDER BY P.LastName, P.FirstName;
        """)
        leaders = cursor.fetchall()
        return leaders
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


# Role Management Endpoints
@app.post("/people/{person_id}/attendee")
def create_attendee(person_id: int, body: dict):
    """
    Creates an Attendee record for a person. Requires guardian information.
    """
    guardian = body.get("guardian")
    if not guardian:
        raise HTTPException(400, "guardian is required")

    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Check if person exists
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Person not found")

        # Check if already an attendee
        cursor.execute("SELECT ID FROM Attendee WHERE PersonID = %s;", (person_id,))
        if cursor.fetchone():
            raise HTTPException(400, "Person is already an attendee")

        # Get next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM Attendee;")
        next_id = cursor.fetchone()[0]

        # Insert
        cursor.execute("""
            INSERT INTO Attendee (ID, PersonID, Guardian)
            VALUES (%s, %s, %s);
        """, (next_id, person_id, guardian))
        cnx.commit()

        return {"message": "Attendee created successfully", "id": next_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.post("/people/{person_id}/leader")
def create_leader(person_id: int):
    """
    Creates a Leader record for a person.
    
    Endpoint: POST /people/{person_id}/leader
    Path Parameter: person_id - The ID of the person to make a leader
    Returns: Success message with leader ID
    
    Similar to create_attendee but:
    - No guardian field required (leaders don't have guardians)
    - Only requires person_id
    
    Raises:
        HTTPException 400: If person already a leader
        HTTPException 404: If person not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Check if person exists
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Person not found")

        # Check if already a leader (prevent duplicate roles)
        cursor.execute("SELECT ID FROM Leader WHERE PersonID = %s;", (person_id,))
        if cursor.fetchone():
            raise HTTPException(400, "Person is already a leader")

        # Manually calculate next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM Leader;")
        next_id = cursor.fetchone()[0]

        # Insert leader record (no guardian field)
        cursor.execute("""
            INSERT INTO Leader (ID, PersonID)
            VALUES (%s, %s);
        """, (next_id, person_id))
        cnx.commit()  # Save role assignment

        return {"message": "Leader created successfully", "id": next_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.post("/people/{person_id}/volunteer")
def create_volunteer(person_id: int):
    """
    Creates a Volunteer record for a person.
    
    Endpoint: POST /people/{person_id}/volunteer
    Path Parameter: person_id - The ID of the person to make a volunteer
    Returns: Success message with volunteer ID
    
    Similar to create_leader - no additional fields required.
    
    Raises:
        HTTPException 400: If person already a volunteer
        HTTPException 404: If person not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Check if person exists
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Person not found")

        # Check if already a volunteer (prevent duplicate roles)
        cursor.execute("SELECT ID FROM Volunteer WHERE PersonID = %s;", (person_id,))
        if cursor.fetchone():
            raise HTTPException(400, "Person is already a volunteer")

        # Manually calculate next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM Volunteer;")
        next_id = cursor.fetchone()[0]

        # Insert volunteer record
        cursor.execute("""
            INSERT INTO Volunteer (ID, PersonID)
            VALUES (%s, %s);
        """, (next_id, person_id))
        cnx.commit()  # Save role assignment

        return {"message": "Volunteer created successfully", "id": next_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/attendees/{attendee_id}")
def delete_attendee(attendee_id: int):
    """
    Deletes an Attendee record by ID.
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        cursor.execute("SELECT ID FROM Attendee WHERE ID = %s;", (attendee_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Attendee not found")

        cursor.execute("DELETE FROM Attendee WHERE ID = %s;", (attendee_id,))
        cnx.commit()

        return {"message": "Attendee deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/leaders/{leader_id}")
def delete_leader(leader_id: int):
    """
    Deletes a Leader record by ID.
    
    Endpoint: DELETE /leaders/{leader_id}
    Path Parameter: leader_id - The ID of the leader to delete
    Returns: Success message
    
    Note: This removes the leader role, not the person.
    Similar to delete_attendee pattern.
    
    Raises:
        HTTPException 404: If leader not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Verify leader exists before deleting
        cursor.execute("SELECT ID FROM Leader WHERE ID = %s;", (leader_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Leader not found")

        # Delete the leader record
        cursor.execute("DELETE FROM Leader WHERE ID = %s;", (leader_id,))
        cnx.commit()  # Save deletion

        return {"message": "Leader deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/volunteers/{volunteer_id}")
def delete_volunteer(volunteer_id: int):
    """
    Deletes a Volunteer record by ID.
    
    Endpoint: DELETE /volunteers/{volunteer_id}
    Path Parameter: volunteer_id - The ID of the volunteer to delete
    Returns: Success message
    
    Note: This removes the volunteer role, not the person.
    Similar to delete_attendee and delete_leader patterns.
    
    Raises:
        HTTPException 404: If volunteer not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Verify volunteer exists before deleting
        cursor.execute("SELECT ID FROM Volunteer WHERE ID = %s;", (volunteer_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Volunteer not found")

        # Delete the volunteer record
        cursor.execute("DELETE FROM Volunteer WHERE ID = %s;", (volunteer_id,))
        cnx.commit()  # Save deletion

        return {"message": "Volunteer deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/people/{person_id}/roles")
def get_person_roles(person_id: int):
    """
    Gets all roles (Attendee, Leader, Volunteer) for a person.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Get attendee
        cursor.execute("""
            SELECT A.ID AS id, A.Guardian AS guardian
            FROM Attendee A
            WHERE A.PersonID = %s;
        """, (person_id,))
        attendee = cursor.fetchone()

        # Get leader
        cursor.execute("""
            SELECT L.ID AS id
            FROM Leader L
            WHERE L.PersonID = %s;
        """, (person_id,))
        leader = cursor.fetchone()

        # Get volunteer
        cursor.execute("""
            SELECT V.ID AS id
            FROM Volunteer V
            WHERE V.PersonID = %s;
        """, (person_id,))
        volunteer = cursor.fetchone()

        return {
            "personId": person_id,
            "attendee": attendee,
            "leader": leader,
            "volunteer": volunteer
        }
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/people/{person_id}/profile")
def get_person_comprehensive_profile(person_id: int):
    """
    Gets a comprehensive profile of a person using complex joins.
    Returns:
    - Person details
    - All roles (Attendee, Leader, Volunteer)
    - Small groups they're a member of (with group details)
    - Small groups they lead (with group details)
    - Events they're registered for (with event details and registration info)
    - Events they've attended (from AttendanceRecord with event details)

    This endpoint demonstrates complex JOINs across multiple tables.
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # 1. Get person basic info
        cursor.execute("""
            SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age
            FROM Person
            WHERE ID = %s;
        """, (person_id,))
        person = cursor.fetchone()

        if not person:
            raise HTTPException(404, "Person not found")

        # 2. Get roles with details (complex LEFT JOINs)
        cursor.execute("""
            SELECT 
                A.ID AS attendeeId,
                A.Guardian AS guardian,
                L.ID AS leaderId,
                V.ID AS volunteerId
            FROM Person P
            LEFT JOIN Attendee A ON P.ID = A.PersonID
            LEFT JOIN Leader L ON P.ID = L.PersonID
            LEFT JOIN Volunteer V ON P.ID = V.PersonID
            WHERE P.ID = %s;
        """, (person_id,))
        roles = cursor.fetchone()

        # 3. Get small groups they're a member of (JOIN through SmallGroupMember)
        cursor.execute("""
            SELECT 
                SG.ID AS groupId,
                SG.Name AS groupName,
                SGM.ID AS membershipId
            FROM SmallGroupMember SGM
            INNER JOIN SmallGroup SG ON SGM.SmallGroupID = SG.ID
            WHERE SGM.AttendeeID = %s
            ORDER BY SG.Name;
        """, (person_id,))
        member_groups = cursor.fetchall()

        # 4. Get small groups they lead (JOIN through SmallGroupLeader)
        cursor.execute("""
            SELECT 
                SG.ID AS groupId,
                SG.Name AS groupName,
                SGL.ID AS leadershipId
            FROM SmallGroupLeader SGL
            INNER JOIN SmallGroup SG ON SGL.SmallGroupID = SG.ID
            WHERE SGL.LeaderID = %s
            ORDER BY SG.Name;
        """, (person_id,))
        leading_groups = cursor.fetchall()

        # 5. Get event registrations with event details (complex JOINs with role resolution)
        # Try with VolunteerID first
        try:
            cursor.execute("""
                SELECT 
                    R.ID AS registrationId,
                    R.EventID AS eventId,
                    R.AttendeeID AS attendeeId,
                    R.LeaderID AS leaderId,
                    R.VolunteerID AS volunteerId,
                    R.EmergencyContact AS emergencyContact,
                    E.Name AS eventName,
                    E.Type AS eventType,
                    E.DateTime AS eventDateTime,
                    E.Location AS eventLocation,
                    E.Notes AS eventNotes,
                    CASE 
                        WHEN R.AttendeeID IS NOT NULL THEN 'Attendee'
                        WHEN R.LeaderID IS NOT NULL THEN 'Leader'
                        WHEN R.VolunteerID IS NOT NULL THEN 'Volunteer'
                        ELSE 'Unknown'
                    END AS registrationRole
                FROM Registration R
                INNER JOIN Event E ON R.EventID = E.ID
                LEFT JOIN Attendee A ON R.AttendeeID = A.ID
                LEFT JOIN Leader L ON R.LeaderID = L.ID
                LEFT JOIN Volunteer V ON R.VolunteerID = V.ID
                WHERE (A.PersonID = %s OR L.PersonID = %s OR V.PersonID = %s)
                ORDER BY E.DateTime DESC;
            """, (person_id, person_id, person_id))
        except mysql.connector.Error:
            # Fallback if VolunteerID column doesn't exist
            cursor.execute("""
                SELECT 
                    R.ID AS registrationId,
                    R.EventID AS eventId,
                    R.AttendeeID AS attendeeId,
                    R.LeaderID AS leaderId,
                    NULL AS volunteerId,
                    R.EmergencyContact AS emergencyContact,
                    E.Name AS eventName,
                    E.Type AS eventType,
                    E.DateTime AS eventDateTime,
                    E.Location AS eventLocation,
                    E.Notes AS eventNotes,
                    CASE 
                        WHEN R.AttendeeID IS NOT NULL THEN 'Attendee'
                        WHEN R.LeaderID IS NOT NULL THEN 'Leader'
                        ELSE 'Unknown'
                    END AS registrationRole
                FROM Registration R
                INNER JOIN Event E ON R.EventID = E.ID
                LEFT JOIN Attendee A ON R.AttendeeID = A.ID
                LEFT JOIN Leader L ON R.LeaderID = L.ID
                WHERE (A.PersonID = %s OR L.PersonID = %s)
                ORDER BY E.DateTime DESC;
            """, (person_id, person_id))
        registrations = cursor.fetchall()

        # 6. Get attendance records with event details (JOIN Event table)
        cursor.execute("""
            SELECT 
                AR.ID AS attendanceId,
                AR.EventID AS eventId,
                E.Name AS eventName,
                E.Type AS eventType,
                E.DateTime AS eventDateTime,
                E.Location AS eventLocation,
                E.Notes AS eventNotes
            FROM AttendanceRecord AR
            INNER JOIN Event E ON AR.EventID = E.ID
            WHERE AR.PersonID = %s
            ORDER BY E.DateTime DESC;
        """, (person_id,))
        attendance_records = cursor.fetchall()

        # 7. Calculate statistics
        total_registrations = len(registrations)
        total_attended = len(attendance_records)
        attendance_rate = round((total_attended / total_registrations * 100) if total_registrations > 0 else 0, 2)

        # Build comprehensive response
        result = {
            "person": person,
            "roles": {
                "isAttendee": roles["attendeeId"] is not None,
                "isLeader": roles["leaderId"] is not None,
                "isVolunteer": roles["volunteerId"] is not None,
                "attendeeId": roles["attendeeId"],
                "leaderId": roles["leaderId"],
                "volunteerId": roles["volunteerId"],
                "guardian": roles.get("guardian")
            },
            "smallGroups": {
                "asMember": member_groups,
                "asLeader": leading_groups,
                "totalGroups": len(member_groups) + len(leading_groups)
            },
            "events": {
                "registrations": registrations,
                "attendance": attendance_records,
                "statistics": {
                    "totalRegistrations": total_registrations,
                    "totalAttended": total_attended,
                    "attendanceRate": attendance_rate
                }
            }
        }

        return result

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/smallgroups")
def get_all_small_groups():
    """
    Gets all small groups, ordered alphabetically by name.
    
    Endpoint: GET /smallgroups
    Returns: List of all small groups
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID AS id, Name AS name FROM SmallGroup ORDER BY name;")
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.post("/smallgroups")
def create_small_group(body: dict = Body(...)):
    """
    Creates a new small group.
    
    Endpoint: POST /smallgroups
    Request Body: dict with "name" field (required)
    Returns: Success message with group ID and name
    
    Manual ID Generation:
    - SmallGroup table doesn't use AUTO_INCREMENT
    - Manually calculates next ID: MAX(ID) + 1
    - IFNULL handles empty table case
    
    Raises:
        HTTPException 400: If name is missing
        HTTPException 500: If database error occurs
    """
    name = body.get("name")
    if not name:
        raise HTTPException(400, "name is required")

    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Manually calculate next ID (no AUTO_INCREMENT)
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroup;")
        next_id = cursor.fetchone()[0]

        # Insert new group with calculated ID
        cursor.execute("""
            INSERT INTO SmallGroup (ID, Name)
            VALUES (%s, %s);
        """, (next_id, name.strip()))  # strip() removes whitespace
        cnx.commit()  # Save group

        return {"message": "Small group created successfully", "id": next_id, "name": name.strip()}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/smallgroups/{group_id}")
def delete_small_group(group_id: int):
    """
    Deletes a small group by ID.
    
    Endpoint: DELETE /smallgroups/{group_id}
    Path Parameter: group_id - The ID of the group to delete
    Returns: Success message
    
    Note: If foreign keys with CASCADE are set up, deleting a group
    will automatically delete related members and leaders.
    Otherwise, you may need to delete them manually first.
    
    Raises:
        HTTPException 404: If group not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Verify group exists before deleting
        cursor.execute("SELECT ID FROM SmallGroup WHERE ID = %s;", (group_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Small group not found")

        # Delete the group
        # CASCADE should handle members/leaders if foreign keys are configured
        cursor.execute("DELETE FROM SmallGroup WHERE ID = %s;", (group_id,))
        cnx.commit()  # Save deletion

        return {"message": "Small group deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/smallgroups/{group_id}")
def get_small_group(group_id: int):
    """
    Gets small group by ID with member count and leaders.
    
    Endpoint: GET /smallgroups/{group_id}
    Path Parameter: group_id - The ID of the group
    Returns: Group object with member count and leader list
    
    Multiple Query Pattern:
    1. Get basic group info
    2. Count members (aggregate query)
    3. Get leaders with names (JOIN query)
    4. Combine into single response
    
    Raises:
        HTTPException 404: If group not found
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Get basic group information
        cursor.execute("SELECT ID AS id, Name AS name FROM SmallGroup WHERE ID = %s;", (group_id,))
        group = cursor.fetchone()
        if not group:
            raise HTTPException(404, "Small group not found")

        # Count members using aggregate function
        cursor.execute("SELECT COUNT(*) AS memberCount FROM SmallGroupMember WHERE SmallGroupID = %s;", (group_id,))
        group["memberCount"] = cursor.fetchone()["memberCount"]

        # Get leaders with names using JOIN
        cursor.execute("""
            SELECT L.ID, P.FirstName, P.LastName 
            FROM SmallGroupLeader L
            JOIN Person P ON L.LeaderID = P.ID
            WHERE SmallGroupID = %s;
        """, (group_id,))
        group["leaders"] = cursor.fetchall()

        return group

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/smallgroups/{group_id}/members")
def get_small_group_members(group_id: int):
    """
      Gets members of a small group by ID
      """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT SGM.ID, P.FirstName, P.LastName 
            FROM SmallGroupMember SGM
            JOIN Attendee A ON SGM.AttendeeID = A.PersonID
            JOIN Person P ON A.PersonID = P.ID
            WHERE SGM.SmallGroupID = %s;
        """, (group_id,))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/smallgroups/{group_id}/leaders")
def get_small_group_leaders(group_id: int):
    """
    Gets leaders of a small group by ID with their names.
    
    Endpoint: GET /smallgroups/{group_id}/leaders
    Path Parameter: group_id - The ID of the group
    Returns: List of leaders with names included
    
    JOIN Pattern:
    - SmallGroupLeader -> Person
    - LeaderID directly references Person.ID (simpler than members)
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # JOIN: SmallGroupLeader -> Person
        cursor.execute("""
            SELECT L.ID, P.FirstName, P.LastName
            FROM SmallGroupLeader L
            JOIN Person P ON L.LeaderID = P.ID
            WHERE L.SmallGroupID = %s;
        """, (group_id,))
        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.post("/smallgroups/{group_id}/members")
def add_member_to_group(group_id: int, body: dict = Body(...)):
    """
    Adds a member (attendee) to a small group by ID.
    Note: attendeeID should be a Person ID of someone who is an Attendee.
    """
    attendee_id = body.get("attendeeID")
    if not attendee_id:
        raise HTTPException(400, "Missing attendeeID")
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Check if group exists
        cursor.execute("SELECT ID FROM SmallGroup WHERE ID = %s;", (group_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Small group not found")

        # Check if person is already a member
        cursor.execute("""
            SELECT ID FROM SmallGroupMember 
            WHERE AttendeeID = %s AND SmallGroupID = %s;
        """, (attendee_id, group_id))
        if cursor.fetchone():
            raise HTTPException(400, "Person is already a member of this group")

        # Get next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroupMember;")
        next_id = cursor.fetchone()[0]

        # Insert
        cursor.execute("""
            INSERT INTO SmallGroupMember (ID, AttendeeID, SmallGroupID)
            VALUES (%s, %s, %s);
        """, (next_id, attendee_id, group_id))
        cnx.commit()

        return {"message": "Member added successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/smallgroups/{group_id}/members/{member_id}")
def remove_member_from_group(group_id: int, member_id: int):
    """
    Removes a member from a small group.
    
    Endpoint: DELETE /smallgroups/{group_id}/members/{member_id}
    Path Parameters:
        - group_id: The ID of the group
        - member_id: The ID of the membership record to delete
    Returns: Success message
    
    Safety Check:
    - Verifies membership exists AND belongs to specified group
    - Prevents deleting memberships from wrong groups
    
    Raises:
        HTTPException 404: If membership not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Verify membership exists and belongs to this group
        cursor.execute("""
            SELECT ID FROM SmallGroupMember 
            WHERE ID = %s AND SmallGroupID = %s;
        """, (member_id, group_id))
        if not cursor.fetchone():
            raise HTTPException(404, "Member not found in this group")

        # Delete the membership record
        cursor.execute("""
            DELETE FROM SmallGroupMember 
            WHERE ID = %s AND SmallGroupID = %s;
        """, (member_id, group_id))
        cnx.commit()  # Save deletion

        return {"message": "Member removed successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.post("/smallgroups/{group_id}/leaders")
def add_leader_to_group(group_id: int, body: dict = Body(...)):
    """
    Adds a leader to a small group.
    
    Endpoint: POST /smallgroups/{group_id}/leaders
    Path Parameter: group_id - The ID of the group
    Request Body: dict with "leaderID" field (required)
    Returns: Success message
    
    Note: leaderID should be a Leader ID (not Person ID).
    The person must already be a Leader before they can lead a group.
    
    Similar to add_member_to_group but for leaders.
    
    Raises:
        HTTPException 400: If leaderID missing or already a leader
        HTTPException 404: If group not found
        HTTPException 500: If database error occurs
    """
    leader_id = body.get("leaderID")
    if not leader_id:
        raise HTTPException(400, "Missing leaderID")

    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Verify group exists
        cursor.execute("SELECT ID FROM SmallGroup WHERE ID = %s;", (group_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Small group not found")

        # Check if person is already a leader (prevent duplicate leadership)
        cursor.execute("""
            SELECT ID FROM SmallGroupLeader 
            WHERE LeaderID = %s AND SmallGroupID = %s;
        """, (leader_id, group_id))
        if cursor.fetchone():
            raise HTTPException(400, "Person is already a leader of this group")

        # Manually calculate next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroupLeader;")
        next_id = cursor.fetchone()[0]

        # Insert leadership record
        cursor.execute("""
            INSERT INTO SmallGroupLeader (ID, LeaderID, SmallGroupID)
            VALUES (%s, %s, %s);
        """, (next_id, leader_id, group_id))
        cnx.commit()  # Save leadership assignment

        return {"message": "Leader added successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/smallgroups/{group_id}/leaders/{leader_id}")
def remove_leader_from_group(group_id: int, leader_id: int):
    """
    Removes a leader from a small group.
    
    Endpoint: DELETE /smallgroups/{group_id}/leaders/{leader_id}
    Path Parameters:
        - group_id: The ID of the group
        - leader_id: The ID of the leadership record to delete
    Returns: Success message
    
    Similar to remove_member_from_group but for leaders.
    
    Raises:
        HTTPException 404: If leadership record not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Verify leadership exists and belongs to this group
        cursor.execute("""
            SELECT ID FROM SmallGroupLeader 
            WHERE ID = %s AND SmallGroupID = %s;
        """, (leader_id, group_id))
        if not cursor.fetchone():
            raise HTTPException(404, "Leader not found in this group")

        # Delete the leadership record
        cursor.execute("""
            DELETE FROM SmallGroupLeader 
            WHERE ID = %s AND SmallGroupID = %s;
        """, (leader_id, group_id))
        cnx.commit()  # Save deletion

        return {"message": "Leader removed successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


from datetime import datetime


@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        insert_query = """
            INSERT INTO Event (Name, Type, DateTime, Location, Notes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_query,
            (event.name, event.type, event.dateTime, event.location, event.notes)
        )
        cnx.commit()

        event_id = cursor.lastrowid

        cursor.execute(
            """
            SELECT
                ID AS id,
                Name AS name,
                Type AS type,
                DateTime AS dateTime,
                Location AS location,
                Notes AS notes
            FROM Event
            WHERE ID = %s
            """,
            (event_id,),
        )

        new_event = cursor.fetchone()

        return new_event

    except mysql.connector.Error as err:
        # This is what becomes the 500 you see in the frontend
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.patch("/events/{event_id}", response_model=Event)
def update_event(event_id: int, event: EventUpdate):
    """
    Updates an event partially (only provided fields are updated).
    
    Endpoint: PATCH /events/{event_id}
    Request Body: EventUpdate (all fields optional - only provided fields are updated)
    Returns: Updated Event object
    
    Dynamic SQL Pattern:
    - Build UPDATE query dynamically based on which fields are provided
    - Only updates fields that are not None
    - This allows partial updates (PATCH semantics)
    
    Example: If only name is provided, only Name column is updated
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Build dynamic update list
        # Only include fields that are provided (not None)
        fields = []  # List of "ColumnName = %s" strings
        values = []  # List of values to update

        if event.name is not None:
            fields.append("Name = %s")
            values.append(event.name)

        if event.type is not None:
            fields.append("Type = %s")
            values.append(event.type)

        if event.dateTime is not None:
            fields.append("DateTime = %s")
            values.append(event.dateTime)

        if event.location is not None:
            fields.append("Location = %s")
            values.append(event.location)

        if event.notes is not None:
            fields.append("Notes = %s")
            values.append(event.notes)

        # If nothing to update, return error
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Build SQL query dynamically
        # Example: "UPDATE Event SET Name = %s, Type = %s WHERE ID = %s"
        sql = f"UPDATE Event SET {', '.join(fields)} WHERE ID = %s"
        values.append(event_id)  # Add event_id as last parameter (for WHERE clause)
        cursor.execute(sql, values)
        cnx.commit()  # Save changes

        # Query database to get updated record
        cursor.execute(
            """
            SELECT
                ID AS id,
                Name AS name,
                Type AS type,
                DateTime AS dateTime,
                Location AS location,
                Notes AS notes
            FROM Event
            WHERE ID = %s
            """,
            (event_id,),
        )
        updated = cursor.fetchone()

        if not updated:
            raise HTTPException(status_code=404, detail="Event not found")

        return updated

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    """
    Deletes an event by ID.
    
    Endpoint: DELETE /events/{event_id}
    Path Parameter: event_id - The ID of the event to delete
    Returns: Success message
    
    Deletion Pattern:
    1. Verify event exists before deleting
    2. Delete related data (registrations, attendance records, etc.)
    3. Delete event notes from MongoDB
    4. Delete Redis check-in data
    5. Delete the event itself
    6. Commit transaction
    
    Note: This performs cascading deletes manually since foreign key
    constraints may not be set up with CASCADE.
    
    Raises:
        HTTPException 404: If event not found
        HTTPException 500: If database error occurs
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # Verify event exists before deleting
        cursor.execute("SELECT ID FROM Event WHERE ID = %s;", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Event not found")

        # Delete related registrations (if foreign keys don't cascade)
        cursor.execute("DELETE FROM Registration WHERE EventID = %s;", (event_id,))

        # Delete related attendance records (if they exist)
        try:
            cursor.execute("DELETE FROM AttendanceRecord WHERE EventID = %s;", (event_id,))
        except mysql.connector.Error:
            # Table might not exist, ignore error
            pass

        # Delete event notes from MongoDB
        try:
            db = get_mongo_db()
            notes_collection = db["eventNotes"]
            notes_collection.delete_many({"eventId": event_id})
        except Exception as e:
            # MongoDB might not be available, log but don't fail
            print(f"MongoDB error deleting event notes (non-fatal): {e}")

        # Delete Redis check-in data
        try:
            r = get_redis_conn()
            checked_in_key = f"event:{event_id}:checkedIn"
            times_key = f"event:{event_id}:checkInTimes"
            r.delete(checked_in_key)  # Delete SET
            r.delete(times_key)  # Delete HASH
        except Exception as e:
            # Redis might not be available, log but don't fail
            print(f"Redis error deleting check-in data (non-fatal): {e}")

        # Delete the event itself
        cursor.execute("DELETE FROM Event WHERE ID = %s;", (event_id,))
        cnx.commit()  # Save all deletions

        return {"message": f"Event {event_id} deleted successfully"}

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/events/upcoming")
def get_upcoming_events():
    # --- FIX 2: Initialize outside try block ---
    cnx = None
    cursor = None
    try:
        # 1. Get Connection (Can fail with PoolError)
        cnx = db_pool.get_connection()
        # 2. Get Cursor (Can fail if cnx failed)
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                    DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event
            WHERE DateTime >= NOW()
            ORDER BY DateTime;
        """)

        return cursor.fetchall()

    except mysql.connector.Error as err:
        # Your existing error handling
        raise HTTPException(500, f"DB error: {err}")

    except Exception:
        # Catch the UnboundLocalError that occurs when the original exception is
        # re-raised and the finally block is executed.
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/events/{event_id}/comprehensive")
def get_comprehensive_event_summary(event_id: int):
    """
    Comprehensive event summary combining MySQL, Redis, and MongoDB.
    
    This endpoint demonstrates multi-database integration - the "Trifecta"!
    It combines data from all three database systems:
    
    1. MySQL: Event details and registrations (structured relational data)
    2. Redis: Live check-ins (real-time in-memory data)
    3. MongoDB: Event notes/highlights (flexible document data)
    
    Endpoint: GET /events/{event_id}/comprehensive
    Returns: Combined summary with data from all three databases
    
    Why use different databases?
    - MySQL: Best for structured queries, joins, transactions
    - Redis: Best for fast, real-time data that changes frequently
    - MongoDB: Best for flexible schemas and document storage
    
    Error Handling:
    - If Redis unavailable, continues without check-in data
    - If MongoDB unavailable, continues without notes
    - MySQL errors cause full failure (core data)
    """
    cnx = None
    cursor = None
    cnx2 = None
    cursor2 = None
    try:
        # ===== MySQL: Get event details and registrations =====
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Get event basic info
        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event
            WHERE ID = %s;
        """, (event_id,))
        event = cursor.fetchone()

        if not event:
            raise HTTPException(404, "Event not found")

        # Get registrations with person details
        # Try with VolunteerID first, fallback if column doesn't exist
        try:
            cursor.execute("""
                SELECT R.ID AS id,
                       R.EventID AS eventId,
                       R.AttendeeID AS attendeeId,
                       R.LeaderID AS leaderId,
                       R.VolunteerID AS volunteerId,
                       R.EmergencyContact AS emergencyContact,
                       P.FirstName AS firstName,
                       P.LastName AS lastName,
                       P.ID AS personId
                FROM Registration R
                LEFT JOIN Attendee A ON R.AttendeeID = A.ID
                LEFT JOIN Leader L ON R.LeaderID = L.ID
                LEFT JOIN Volunteer V ON R.VolunteerID = V.ID
                LEFT JOIN Person P ON (A.PersonID = P.ID OR L.PersonID = P.ID OR V.PersonID = P.ID)
                WHERE R.EventID = %s;
            """, (event_id,))
        except mysql.connector.Error:
            # Fallback if VolunteerID column doesn't exist
            cursor.execute("""
                SELECT R.ID AS id,
                       R.EventID AS eventId,
                       R.AttendeeID AS attendeeId,
                       R.LeaderID AS leaderId,
                       NULL AS volunteerId,
                       R.EmergencyContact AS emergencyContact,
                       P.FirstName AS firstName,
                       P.LastName AS lastName,
                       P.ID AS personId
                FROM Registration R
                LEFT JOIN Attendee A ON R.AttendeeID = A.ID
                LEFT JOIN Leader L ON R.LeaderID = L.ID
                LEFT JOIN Person P ON (A.PersonID = P.ID OR L.PersonID = P.ID)
                WHERE R.EventID = %s;
            """, (event_id,))
        registrations = cursor.fetchall()

        # Get registration statistics
        attendee_count = sum(1 for r in registrations if r.get('attendeeId'))
        leader_count = sum(1 for r in registrations if r.get('leaderId'))
        volunteer_count = sum(1 for r in registrations if r.get('volunteerId'))

        # ===== Redis: Get live check-in data =====
        # Redis stores real-time check-in data (very fast, in-memory)
        check_in_data = {
            "checkedInCount": 0,
            "checkedInStudents": [],
            "checkInTimes": {}
        }

        try:
            r = get_redis_conn()
            # Redis key naming convention: event:{event_id}:{data_type}
            checked_in_key = f"event:{event_id}:checkedIn"  # SET: student IDs
            times_key = f"event:{event_id}:checkInTimes"  # HASH: ID -> timestamp

            # SMEMBERS: Get all checked-in student IDs from Redis SET
            student_ids = r.smembers(checked_in_key)

            if student_ids:
                # HGETALL: Get all check-in timestamps from Redis HASH
                timestamps = r.hgetall(times_key)

                # Convert Redis strings to integers for MySQL query
                student_ids_int = [int(sid) for sid in student_ids]

                # Query MySQL to get student details (names, etc.)
                # Need second connection because first one is still in use
                cnx2 = db_pool.get_connection()
                cursor2 = cnx2.cursor(dictionary=True)

                if student_ids_int:
                    # Build dynamic IN clause: "WHERE ID IN (%s, %s, %s)"
                    format_strings = ",".join(["%s"] * len(student_ids_int))
                    query = f"SELECT ID, FirstName, LastName FROM Person WHERE ID IN ({format_strings});"
                    cursor2.execute(query, tuple(student_ids_int))
                    checked_in_people = cursor2.fetchall()

                    # Combine Redis timestamps with MySQL student data
                    check_in_data["checkedInCount"] = len(checked_in_people)
                    check_in_data["checkedInStudents"] = [
                        {
                            "personId": p["ID"],
                            "firstName": p["FirstName"],
                            "lastName": p["LastName"],
                            "checkInTime": timestamps.get(str(p["ID"]))  # Get timestamp from Redis
                        }
                        for p in checked_in_people
                    ]
                    check_in_data["checkInTimes"] = timestamps
        except redis.RedisError as e:
            # Redis might not be available - continue without check-in data
            # This is non-fatal - we can still return event and registration data
            print(f"Redis error (non-fatal): {e}")
        except Exception as e:
            # Any other error - continue without Redis data
            print(f"Error fetching Redis data (non-fatal): {e}")

        # ===== MongoDB: Get event notes/highlights =====
        # MongoDB stores flexible event notes/highlights (can have different fields)
        event_notes = []
        try:
            db = get_mongo_db()
            notes_collection = db["eventNotes"]  # Access collection (like a table)

            # Query MongoDB: find all notes for this event
            # {"eventId": event_id} is the filter (like WHERE clause)
            notes = list(notes_collection.find({"eventId": event_id}))

            # Convert MongoDB ObjectId to string for JSON serialization
            for note in notes:
                note["_id"] = str(note["_id"])  # ObjectId can't be JSON serialized directly
                event_notes.append(note)
        except Exception as e:
            # MongoDB might not be available - continue without notes
            # This is non-fatal - we can still return other data
            print(f"MongoDB error (non-fatal): {e}")

        # ===== Combine all data =====
        result = {
            "event": event,
            "registrations": {
                "total": len(registrations),
                "attendees": attendee_count,
                "leaders": leader_count,
                "volunteers": volunteer_count,
                "list": registrations
            },
            "liveCheckIns": {
                "count": check_in_data["checkedInCount"],
                "students": check_in_data["checkedInStudents"],
                "source": "Redis"
            },
            "notes": {
                "count": len(event_notes),
                "list": event_notes,
                "source": "MongoDB"
            },
            "summary": {
                "totalRegistered": len(registrations),
                "totalCheckedIn": check_in_data["checkedInCount"],
                "attendanceRate": round(
                    (check_in_data["checkedInCount"] / len(registrations) * 100) if registrations else 0, 2),
                "notesCount": len(event_notes)
            },
            "dataSources": {
                "eventInfo": "MySQL",
                "registrations": "MySQL",
                "liveCheckIns": "Redis",
                "notes": "MongoDB"
            }
        }

        return result

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Close cursors safely (must close before connections)
        if cursor2 is not None:
            try:
                cursor2.close()
            except:
                pass
        if cursor is not None:
            try:
                cursor.close()
            except:
                pass

        # Close connections safely (returns them to pool)
        if cnx2 is not None and cnx2.is_connected():
            try:
                cnx2.close()
            except:
                pass
        if cnx is not None and cnx.is_connected():
            try:
                cnx.close()
            except:
                pass


@app.get("/events/{event_id}")
def get_event_by_id(event_id: int):
    """
    Returns a single event by ID.
    """
    cnx = None
    cursor = None
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event
            WHERE ID = %s;
        """, (event_id,))

        event = cursor.fetchone()
        if not event:
            raise HTTPException(404, "Event not found")

        return event

    except mysql.connector.Error as err:
        raise HTTPException(500, f"DB error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.get("/events", response_model=list[Event])
def get_all_events():
    """
    Gets all events, ordered by most recent first.
    """
    cnx = None  # Initialize cnx outside try block
    cursor = None  # Initialize cursor outside try block
    try:
        # Fetch connection from the pool
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Query all events with formatted datetime
        cursor.execute("""
            SELECT 
                ID AS id,
                Name AS name,
                Type AS type,
                DATE_FORMAT(DateTime, '%Y-%m-%d %H:%i:%s') AS dateTime, 
                Location AS location,
                Notes AS notes
            FROM Event
            ORDER BY DateTime DESC;
        """)

        return cursor.fetchall()

    except mysql.connector.Error as err:
        # If an error occurs, re-raise as an HTTPException
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


# mongodb!
@app.get("/event-types")
def get_all_event_types():
    """
    Gets all event types from MongoDB.
    
    Endpoint: GET /event-types
    Returns: List of all event type documents
    
    MongoDB Pattern:
    - find({}) with empty filter returns all documents
    - Converts ObjectId to string for JSON serialization
    - Event types have flexible schemas (different fields per type)
    """
    try:
        db = get_mongo_db()
        collection = db["eventTypes"]  # Access collection
        # Query all documents (empty filter = no filter)
        event_types = list(collection.find({}))
        # Convert MongoDB ObjectId to string for each document
        for et in event_types:
            et["_id"] = str(et["_id"])  # ObjectId can't be JSON serialized
        return event_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


@app.get("/event-type/{event_type}")
def get_event_type(event_type: str):
    """
    Fetches a flexible event type definition from MongoDB.
    
    Endpoint: GET /event-type/{event_type}
    Path Parameter: event_type - The name of the event type
    Returns: Event type document (flexible schema)
    
    MongoDB Pattern:
    - find_one() returns single document or None
    - Query by event_type field (not _id)
    - Returns raw document so schema can vary per type
    
    Raises:
        HTTPException 404: If event type not found
        HTTPException 500: If MongoDB error occurs
    """
    try:
        db = get_mongo_db()
        collection = db["eventTypes"]

        # Query by event_type field (not _id)
        doc = collection.find_one({"event_type": event_type})

        if not doc:
            raise HTTPException(
                status_code=404,
                detail=f"No event type found with name '{event_type}'."
            )

        # Convert ObjectId to string for JSON serialization
        doc["_id"] = str(doc["_id"])

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


@app.post("/event-types")
def create_event_type(body: dict):
    """
    Creates a new event type in MongoDB.
    
    Endpoint: POST /event-types
    Request Body: dict with flexible fields (must include "event_type")
    Returns: Created event type document
    
    MongoDB Pattern:
    - Validates required field (event_type)
    - Checks for duplicates before inserting
    - Adds metadata (created timestamp)
    - insert_one() returns result with inserted_id
    - Queries back to get complete document
    
    Raises:
        HTTPException 400: If event_type missing or already exists
        HTTPException 500: If MongoDB error occurs
    """
    try:
        db = get_mongo_db()
        collection = db["eventTypes"]

        # Validate required field
        if "event_type" not in body:
            raise HTTPException(400, "event_type field is required")

        # Check if already exists (prevent duplicates)
        existing = collection.find_one({"event_type": body["event_type"]})
        if existing:
            raise HTTPException(400, f"Event type '{body['event_type']}' already exists")

        # Add metadata: created timestamp
        body["created"] = datetime.utcnow()

        # Insert document into collection
        result = collection.insert_one(body)
        # Query back to get complete document with generated _id
        new_doc = collection.find_one({"_id": result.inserted_id})
        new_doc["_id"] = str(new_doc["_id"])  # Convert ObjectId to string
        return new_doc
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


@app.patch("/event-types/{event_type}")
def update_event_type(event_type: str, body: dict):
    """
    Updates an event type in MongoDB.
    
    Endpoint: PATCH /event-types/{event_type}
    Path Parameter: event_type - The name of the event type to update
    Request Body: dict with fields to update
    Returns: Updated event type document
    
    MongoDB Update Pattern:
    - update_one() updates first matching document
    - $set operator sets/updates fields (partial update)
    - matched_count tells us if document was found
    - Adds updated timestamp automatically
    
    Raises:
        HTTPException 404: If event type not found
        HTTPException 500: If MongoDB error occurs
    """
    try:
        db = get_mongo_db()
        collection = db["eventTypes"]

        # Add updated timestamp
        body["updated"] = datetime.utcnow()

        # Update document using $set operator (partial update)
        # {"event_type": event_type} is the filter (which document to update)
        # {"$set": body} sets/updates fields in body
        updated = collection.update_one(
            {"event_type": event_type},  # Filter: which document
            {"$set": body}  # Update: what to change
        )

        # Check if document was found (matched_count = 0 means not found)
        if updated.matched_count == 0:
            raise HTTPException(404, "Event type not found")

        # Query back to get updated document
        updated_doc = collection.find_one({"event_type": event_type})
        updated_doc["_id"] = str(updated_doc["_id"])  # Convert ObjectId to string
        return updated_doc
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


@app.delete("/event-types/{event_type}")
def delete_event_type(event_type: str):
    """
    Deletes an event type from MongoDB.
    
    Endpoint: DELETE /event-types/{event_type}
    Path Parameter: event_type - The name of the event type to delete
    Returns: Success message
    
    MongoDB Delete Pattern:
    - delete_one() deletes first matching document
    - deleted_count tells us if document was deleted
    - Query by event_type field (not _id)
    
    Raises:
        HTTPException 404: If event type not found
        HTTPException 500: If MongoDB error occurs
    """
    try:
        db = get_mongo_db()
        collection = db["eventTypes"]

        # Delete document matching event_type
        deleted = collection.delete_one({"event_type": event_type})

        # Check if document was deleted (deleted_count = 0 means not found)
        if deleted.deleted_count == 0:
            raise HTTPException(404, "Event type not found")

        return {"message": f"Event type '{event_type}' deleted successfully"}
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


@app.get("/search")
def search_all(query: str):
    """
    Comprehensive search across events, people, and roles.
    Searches:
    - Events by name, type, location
    - People by name
    - People by role (leader, attendee, volunteer)
    - Event types from MongoDB
    
    Returns results grouped by category.
    """
    try:
        results = {
            "query": query,
            "events": [],
            "people": [],
            "roles": {
                "leaders": [],
                "attendees": [],
                "volunteers": []
            },
            "eventTypes": []
        }

        query_lower = query.lower().strip()

        # Search events (MySQL)
        try:
            cnx = db_pool.get_connection()
            cursor = cnx.cursor(dictionary=True)

            # Search events by name, type, or location
            cursor.execute("""
                SELECT ID AS id, Name AS name, Type AS type,
                       DateTime AS dateTime, Location AS location, Notes AS notes
                FROM Event
                WHERE LOWER(Name) LIKE %s 
                   OR LOWER(Type) LIKE %s 
                   OR LOWER(Location) LIKE %s
                ORDER BY DateTime DESC
                LIMIT 20;
            """, (f"%{query_lower}%", f"%{query_lower}%", f"%{query_lower}%"))
            results["events"] = cursor.fetchall()

            # Search people by name
            cursor.execute("""
                SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age
                FROM Person
                WHERE LOWER(FirstName) LIKE %s 
                   OR LOWER(LastName) LIKE %s
                   OR LOWER(CONCAT(FirstName, ' ', LastName)) LIKE %s
                ORDER BY LastName, FirstName
                LIMIT 20;
            """, (f"%{query_lower}%", f"%{query_lower}%", f"%{query_lower}%"))
            results["people"] = cursor.fetchall()

            # Search by role keywords
            if "leader" in query_lower or "lead" in query_lower:
                cursor.execute("""
                    SELECT L.ID AS id, P.ID AS personId, P.FirstName AS firstName, P.LastName AS lastName
                    FROM Leader L
                    JOIN Person P ON L.PersonID = P.ID
                    ORDER BY P.LastName, P.FirstName;
                """)
                results["roles"]["leaders"] = cursor.fetchall()

            if "attendee" in query_lower or "student" in query_lower or "youth" in query_lower:
                cursor.execute("""
                    SELECT A.ID AS id, A.PersonID AS personId, P.FirstName AS firstName, 
                           P.LastName AS lastName, A.Guardian AS guardian
                    FROM Attendee A
                    JOIN Person P ON A.PersonID = P.ID
                    ORDER BY P.LastName, P.FirstName;
                """)
                results["roles"]["attendees"] = cursor.fetchall()

            if "volunteer" in query_lower:
                cursor.execute("""
                    SELECT V.ID AS id, V.PersonID AS personId, P.FirstName AS firstName, P.LastName AS lastName
                    FROM Volunteer V
                    JOIN Person P ON V.PersonID = P.ID
                    ORDER BY P.LastName, P.FirstName;
                """)
                results["roles"]["volunteers"] = cursor.fetchall()

        except mysql.connector.Error as err:
            print(f"MySQL search error: {err}")
        finally:
            if cursor is not None:
                cursor.close()
            if cnx is not None and cnx.is_connected():
                cnx.close()

        # Search event types (MongoDB)
        try:
            db = get_mongo_db()
            collection = db["eventTypes"]

            # Use regex for case-insensitive search
            event_types = list(collection.find({
                "$or": [
                    {"event_type": {"$regex": query_lower, "$options": "i"}},
                    {"description": {"$regex": query_lower, "$options": "i"}}
                ]
            }))

            for et in event_types:
                et["_id"] = str(et["_id"])
            results["eventTypes"] = event_types
        except Exception as e:
            print(f"MongoDB search error: {e}")

        # Calculate totals
        results["totals"] = {
            "events": len(results["events"]),
            "people": len(results["people"]),
            "leaders": len(results["roles"]["leaders"]),
            "attendees": len(results["roles"]["attendees"]),
            "volunteers": len(results["roles"]["volunteers"]),
            "eventTypes": len(results["eventTypes"])
        }

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {e}")


@app.get("/events/by-type/{event_type}")
def get_events_by_type(event_type: str):
    """
    Gets all events of a specific type, including MongoDB event type details.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Get events from MySQL
        cursor.execute("""
            SELECT ID AS id, Name AS name, Type AS type,
                   DateTime AS dateTime, Location AS location, Notes AS notes
            FROM Event
            WHERE Type = %s
            ORDER BY DateTime DESC;
        """, (event_type,))
        events = cursor.fetchall()

        cursor.close()
        cnx.close()

        # Get event type details from MongoDB
        event_type_details = None
        try:
            db = get_mongo_db()
            collection = db["eventTypes"]
            event_type_details = collection.find_one({"event_type": event_type})
            if event_type_details:
                event_type_details["_id"] = str(event_type_details["_id"])
        except Exception as e:
            print(f"MongoDB error (non-fatal): {e}")

        return {
            "eventType": event_type,
            "eventTypeDetails": event_type_details,
            "events": events,
            "count": len(events)
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")


# mongo db notes for person
@app.get("/persons/{person_id}/notes")
def get_notes_for_person(person_id: int):
    """
    Gets all notes for a specific person from MongoDB. Includes timestamp and category.
    """
    db = get_mongo_db()
    notes = list(db["personNotes"].find({"personId": person_id}))
    for note in notes:
        note["_id"] = str(note["_id"])
    return notes


@app.post("/persons/{person_id}/notes")
def add_note_to_person(person_id: int, body: dict):
    """
    Adds a new note for a specific person. Stores flexible fields in MongoDB.
    
    Endpoint: POST /persons/{person_id}/notes
    Path Parameter: person_id - The ID of the person
    Request Body: dict with "text" (required) and optional fields
    Returns: Created note ID
    
    MongoDB Pattern:
    - Validates required field (text)
    - Builds document with flexible fields
    - Adds metadata (created timestamp)
    - insert_one() returns result with inserted_id
    
    Raises:
        HTTPException 400: If text is missing
    """
    db = get_mongo_db()

    # Validate required field
    if "text" not in body:
        raise HTTPException(400, "text is required")

    # Build MongoDB document with flexible fields
    note = {
        "personId": person_id,
        "text": body["text"],  # Required field
        "category": body.get("category"),  # Optional field
        "createdBy": body.get("createdBy"),  # Optional field
        "created": datetime.utcnow(),  # Auto-set timestamp
    }

    # Insert document and return generated ID
    result = db["personNotes"].insert_one(note)
    return {"id": str(result.inserted_id)}  # Convert ObjectId to string


@app.patch("/notes/{note_id}")
def update_note_by_id(note_id: str, body: dict):
    """
    Updates an existing note by its MongoDB _id. Adds an updated timestamp.
    
    Endpoint: PATCH /notes/{note_id}
    Path Parameter: note_id - MongoDB ObjectId as string
    Request Body: dict with fields to update
    Returns: Success message
    
    MongoDB Update Pattern:
    - Converts string ID back to ObjectId for query
    - Uses $set operator for partial update
    - Adds updated timestamp automatically
    - matched_count tells us if document was found
    
    Raises:
        HTTPException 404: If note not found
    """
    db = get_mongo_db()

    # Add updated timestamp
    body["updated"] = datetime.utcnow()

    # Update document using ObjectId
    # Convert string ID back to ObjectId for MongoDB query
    updated = db["personNotes"].update_one(
        {"_id": ObjectId(note_id)},  # Filter: convert string to ObjectId
        {"$set": body}  # Update: set fields in body
    )

    # Check if document was found
    if updated.matched_count == 0:
        raise HTTPException(404, "Note not found")

    return {"message": "Note updated"}


@app.delete("/notes/{note_id}")
def delete_note_by_id(note_id: str):
    """
    Deletes a note by its MongoDB _id.
    
    Endpoint: DELETE /notes/{note_id}
    Path Parameter: note_id - MongoDB ObjectId as string
    Returns: Success message
    
    MongoDB Delete Pattern:
    - Converts string ID to ObjectId for query
    - delete_one() deletes matching document
    - deleted_count tells us if document was deleted
    
    Raises:
        HTTPException 404: If note not found
    """
    db = get_mongo_db()

    # Delete document by ObjectId (convert string to ObjectId)
    deleted = db["personNotes"].delete_one({"_id": ObjectId(note_id)})

    # Check if document was deleted
    if deleted.deleted_count == 0:
        raise HTTPException(404, "Note not found")

    return {"message": "Note deleted"}


# parent contacts mongo_db
@app.get("/persons/{person_id}/parent-contacts")
def get_parent_contacts(person_id: int):
    """
    Gets all parent contacts for a specific person from MongoDB.
    
    Endpoint: GET /persons/{person_id}/parent-contacts
    Path Parameter: person_id - The ID of the person
    Returns: List of parent contact documents
    
    MongoDB Pattern:
    - Query by personId field
    - Contacts have flexible fields (method, summary, date, etc.)
    - Converts ObjectId to string for JSON serialization
    """
    db = get_mongo_db()
    # Query MongoDB collection filtered by personId
    contacts = list(db["parentContacts"].find({"personId": person_id}))
    # Convert ObjectId to string for each contact
    for c in contacts:
        c["_id"] = str(c["_id"])
    return contacts


@app.post("/persons/{person_id}/parent-contacts")
def add_parent_contact(person_id: int, body: dict):
    """
    Adds a new parent contact entry for a specific person.
    
    Endpoint: POST /persons/{person_id}/parent-contacts
    Path Parameter: person_id - The ID of the person
    Request Body: dict with "summary" (required) and optional fields
    Returns: Created contact ID
    
    MongoDB Pattern:
    - Validates required field (summary)
    - Builds document with flexible fields
    - Adds metadata (created timestamp)
    
    Raises:
        HTTPException 400: If summary is missing
    """
    db = get_mongo_db()

    # Validate required field
    if "summary" not in body:
        raise HTTPException(400, "summary is required")

    # Build MongoDB document
    contact = {
        "personId": person_id,
        "method": body.get("method"),  # Optional: contact method (phone, email, etc.)
        "summary": body["summary"],  # Required: summary of contact
        "date": body.get("date"),  # Optional: date they contacted you
        "createdBy": body.get("createdBy"),  # Optional: who created this record
        "created": datetime.utcnow(),  # Auto-set timestamp
    }

    # Insert document and return generated ID
    result = db["parentContacts"].insert_one(contact)
    return {"id": str(result.inserted_id)}  # Convert ObjectId to string


@app.patch("/parent-contacts/{contact_id}")
def update_parent_contact(contact_id: str, body: dict):
    """
    Updates a parent contact by MongoDB _id. Adds updated timestamp.
    
    Endpoint: PATCH /parent-contacts/{contact_id}
    Path Parameter: contact_id - MongoDB ObjectId as string
    Request Body: dict with fields to update
    Returns: Success message
    
    Similar to update_note_by_id pattern.
    
    Raises:
        HTTPException 404: If contact not found
    """
    db = get_mongo_db()

    # Add updated timestamp
    body["updated"] = datetime.utcnow()

    # Update document using ObjectId
    updated = db["parentContacts"].update_one(
        {"_id": ObjectId(contact_id)},  # Convert string to ObjectId
        {"$set": body}  # Partial update
    )

    # Check if document was found
    if updated.matched_count == 0:
        raise HTTPException(404, "Parent contact not found")

    return {"message": "Parent contact updated"}


@app.delete("/parent-contacts/{contact_id}")
def delete_parent_contact(contact_id: str):
    """
    Deletes a parent contact by MongoDB _id.
    
    Endpoint: DELETE /parent-contacts/{contact_id}
    Path Parameter: contact_id - MongoDB ObjectId as string
    Returns: Success message
    
    Similar to delete_note_by_id pattern.
    
    Raises:
        HTTPException 404: If contact not found
    """
    db = get_mongo_db()

    # Delete document by ObjectId
    deleted = db["parentContacts"].delete_one({"_id": ObjectId(contact_id)})

    # Check if document was deleted
    if deleted.deleted_count == 0:
        raise HTTPException(404, "Parent contact not found")

    return {"message": "Parent contact deleted"}


# event highlights mong_db
@app.get("/events/{event_id}/notes")
def get_event_notes(event_id: int):
    """
    Gets all highlight entries for a specific event from MongoDB.
    
    Endpoint: GET /events/{event_id}/notes
    Path Parameter: event_id - The ID of the event
    Returns: List of event note/highlight documents
    
    MongoDB Pattern:
    - Query by eventId field
    - Notes have flexible fields (notes, concerns, studentWins, etc.)
    - Converts ObjectId to string for JSON serialization
    """
    db = get_mongo_db()
    # Query MongoDB collection filtered by eventId
    notes = list(db["eventNotes"].find({"eventId": event_id}))
    # Convert ObjectId to string for each note
    for n in notes:
        n["_id"] = str(n["_id"])
    return notes


@app.post("/events/{event_id}/notes")
def add_event_notes(event_id: int, body: dict):
    """
    Adds a new highlight entry for a specific event.
    
    Endpoint: POST /events/{event_id}/notes
    Path Parameter: event_id - The ID of the event
    Request Body: dict with flexible fields (notes, concerns, studentWins, etc.)
    Returns: Created note ID
    
    Note: The validation checks for "notes" field, but it's actually optional
    in the document structure. This is a validation requirement.
    
    Raises:
        HTTPException 400: If notes field is missing
    """
    db = get_mongo_db()

    # Validate required field (even though document structure is flexible)
    if "notes" not in body:
        raise HTTPException(400, "notes field is required")

    # Build MongoDB document with flexible fields
    note = {
        "eventId": event_id,
        "notes": body.get("notes"),  # Optional: general notes
        "concerns": body.get("concerns"),  # Optional: concerns
        "studentWins": body.get("studentWins"),  # Optional: positive highlights
        "createdBy": body.get("createdBy"),  # Optional: who created this
        "created": datetime.utcnow(),  # Auto-set timestamp
    }

    # Insert document and return generated ID
    result = db["eventNotes"].insert_one(note)
    return {"id": str(result.inserted_id)}  # Convert ObjectId to string


@app.patch("/event/{note_id}")
def update_event_note(note_id: str, body: dict):
    """
    Updates an event highlight entry. Adds updated timestamp.
    """
    db = get_mongo_db()
    body["updated"] = datetime.utcnow()

    updated = db["eventNotes"].update_one(
        {"_id": ObjectId(note_id)},
        {"$set": body}
    )

    if updated.matched_count == 0:
        raise HTTPException(404, "Event note not found")

    return {"message": "Note updated"}


@app.delete("/notes/{note_id}")
def delete_event_note(note_id: str):
    """
    Deletes an event highlight entry by MongoDB _id.
    
    Endpoint: DELETE /notes/{note_id}
    Path Parameter: note_id - MongoDB ObjectId as string
    Returns: Success message
    
    Note: This endpoint deletes from eventNotes collection.
    Similar to other MongoDB delete patterns.
    
    Raises:
        HTTPException 404: If event note not found
    """
    db = get_mongo_db()

    # Delete document by ObjectId
    deleted = db["eventNotes"].delete_one({"_id": ObjectId(note_id)})

    # Check if document was deleted
    if deleted.deleted_count == 0:
        raise HTTPException(404, "Event note not found")

    return {"message": "Note deleted"}


# redis!
@app.get("/event/{eventId}/live-checkins", response_model=LiveCheckInSummary)
def get_live_checkins(eventId: int):
    """
    Retrieves the real-time list of students currently checked in,
    combining Redis (live check-in state) and MySQL (student details).
    Mimics the caching pattern from the professor's daily deal example.
    """
    cnx = None
    cursor = None
    try:
        # 1. Connect to Redis
        r = get_redis_conn()

        checked_in_key = f"event:{eventId}:checkedIn"
        times_key = f"event:{eventId}:checkInTimes"

        # Fetch all checked-in student IDs
        student_ids = r.smembers(checked_in_key)

        if not student_ids:
            raise HTTPException(status_code=404, detail="No students currently checked in.")

        # Fetch timestamps for each student
        timestamps = r.hgetall(times_key)

        # Convert Redis set of strings → list[int]
        student_ids_int = [int(sid) for sid in student_ids]

        # 2. Query MySQL for details about these students
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)

        format_strings = ",".join(["%s"] * len(student_ids_int))
        query = f"SELECT ID, FirstName, LastName FROM Person WHERE ID IN ({format_strings});"
        cursor.execute(query, tuple(student_ids_int))
        people = cursor.fetchall()

        # 3. Combine MySQL + Redis timestamp info
        students = []
        for p in people:
            sid = p["ID"]
            students.append(
                CheckedInStudent(
                    studentId=sid,
                    firstName=p["FirstName"],
                    lastName=p["LastName"],
                    checkInTime=timestamps.get(str(sid))
                )
            )

        return LiveCheckInSummary(
            eventId=eventId,
            count=len(students),
            students=students,
            message=f"{len(students)} students are currently checked in to event {eventId}."
        )

    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.post("/event/{eventId}/checkin/{personId}")
def checkin_person(eventId: int, personId: int):
    """
    Checks in a person to an event using Redis for real-time tracking
    AND updates the persistent SQL AttendanceRecord table.
    """
    cnx = None
    cursor = None
    try:
        r = get_redis_conn()
        now_utc_iso = datetime.utcnow().isoformat()

        # --- Redis Key Setup ---
        checked_in_key = f"event:{eventId}:checkedIn"
        times_key = f"event:{eventId}:checkInTimes"

        # --- 1. MySQL Connection & Person Verification ---
        cnx = get_db_connection()
        cursor = cnx.cursor()

        # A. Verify person exists in MySQL
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (personId,))
        if not cursor.fetchone():
            raise HTTPException(404, "Person not found")

        # --- 2. SQL Attendance Record Update (The Fix for totalAttended) ---
        # **This is the new critical step.**
        # Ensure your AttendanceRecord table has PersonID and EventID fields.
        try:
            cursor.execute("""
                INSERT INTO AttendanceRecord (PersonID, EventID)
                VALUES (%s, %s);
            """, (personId, eventId))  # Use the same timestamp

            # Commit the SQL transaction immediately
            cnx.commit()

        except mysql.connector.IntegrityError:
            # Handle case where the record already exists
            # (e.g., if you have a UNIQUE constraint on (PersonID, EventID))
            # For check-ins, you usually want to allow multiple entries
            # or have a more complex composite key. We'll proceed if it's a conflict.
            pass

            # --- 3. Redis Real-time Update ---
        # B. SADD: Add person ID to SET (For live count)
        r.sadd(checked_in_key, personId)

        # C. HSET: Store check-in timestamp in HASH (For display time)
        r.hset(times_key, personId, now_utc_iso)

        return {
            "message": f"Person {personId} checked in to event {eventId} (SQL & Redis updated).",
            "eventId": eventId,
            "personId": personId,
            "checkInTime": now_utc_iso
        }

    except redis.RedisError as e:
        # NOTE: If Redis fails here, the SQL transaction is committed,
        # so the 'totalAttended' is accurate, but the live count is wrong.
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")

    except mysql.connector.Error as err:
        # If SQL fails, attempt to rollback
        if cnx and cnx.is_connected():
            cnx.rollback()
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")

    finally:
        if cursor is not None:
            cursor.close()
        if cnx is not None and cnx.is_connected():
            cnx.close()


@app.delete("/event/{eventId}/checkin/{personId}")
def checkout_person(eventId: int, personId: int):
    """
    Checks out a person from an event (removes from Redis).
    """
    try:
        r = get_redis_conn()

        checked_in_key = f"event:{eventId}:checkedIn"
        times_key = f"event:{eventId}:checkInTimes"

        # Remove from checked-in set
        removed = r.srem(checked_in_key, personId)

        # Remove timestamp
        r.hdel(times_key, personId)

        if removed == 0:
            raise HTTPException(404, "Person not checked in to this event")

        return {
            "message": f"Person {personId} checked out from event {eventId}",
            "eventId": eventId,
            "personId": personId
        }
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")


@app.get("/demo", response_class=FileResponse)
async def read_demo():
    """
    Serves the demo HTML page.
    """
    return os.path.join(os.path.dirname(__file__), "index.html")


# --- GraphQL Integration ---
# Uncomment the following lines to enable GraphQL endpoint
# You'll need to install: pip install strawberry-graphql
from graphql_app import graphql_app

app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    print("\nTo run this FastAPI application:")
    print("1. Make sure you have installed the required packages: pip install -r requirements.txt")
    print("2. Run the server: uvicorn demo3_fastapi_app:app --reload --port 8000")
    print("3. Open your browser and go to http://127.0.0.1:8000/docs for the API documentation.")
    print("4. Open your browser and go to http://127.0.0.1:8000/demo for a UI demo.")

    # This part is for demonstration purposes and will not be executed when running with uvicorn
    # uvicorn.run("demo3_fastapi_app:app", host="127.0.0.1", port=8000, reload=True)
