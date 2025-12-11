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
# NOTE: Update with your database credential
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, REDIS_SSL, REDIS_USERNAME, REDIS_PORT, \
    REDIS_PASSWORD, REDIS_HOST, MONGO_URI
from database import get_mysql_pool, get_mongo_client, close_connections, get_mongo_db, get_redis_conn, \
    get_redis_client, get_db_connection

# --- Connection Pooling ---
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="fastapi_pool",
        pool_size=5,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    print("Database connection pool created successfully.")
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    exit()


# --- App Lifecycle Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize all database connections
    print("Application startup: Initializing database connections...")
    get_mysql_pool()
    get_mongo_client()
    # get_redis_client()
    yield
    # Shutdown: Close all database connections
    print("Application shutdown: Closing database connections...")
    close_connections()


# --- FastAPI App ---
app = FastAPI(
    title="Youth Group API",
    description="An API for interacting with the YouthGroupDB database.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This will allow the frontend (running on a different origin) to communicate with the API.
# For demonstration purposes, we allow all origins, methods, and headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models (for request/response validation) ---
class Person(BaseModel):
    id: int
    firstName: str
    lastName: str
    age: int | None = None


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
    Retrieves a list of all customers.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID AS id, firstName, lastName, age FROM Person ORDER BY lastName, firstName;")
        people = cursor.fetchall()
        return people
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.get("/people/{person_id}", response_model=Person)
def get_person_by_id(person_id: int):
    """
    Retrieves a specific customer by their ID.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT ID AS id, firstName, lastName, age FROM Person WHERE ID = %s;"
        cursor.execute(query, (person_id,))
        person = cursor.fetchone()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.post("/people", response_model=Person, status_code=201)
def create_person(person: PersonCreate):
    """
    creates a person
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        insert_query = """
            INSERT INTO Person (FirstName, LastName, Age)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (person.firstName, person.lastName, person.age))
        cnx.commit()

        person_id = cursor.lastrowid

        cursor.execute(
            "SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s",
            (person_id,)
        )
        new_person = cursor.fetchone()
        return new_person

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()



@app.put("/people/{person_id}", response_model=Person)
def update_person(person_id: int, person: PersonCreate):
    """
    Updates a person.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Person WHERE ID = %s;", (person_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Person not found")
        update_query = """
            UPDATE Person
            SET FirstName = %s, LastName = %s, Age = %s
            WHERE ID = %s;
        """
        cursor.execute(update_query, (person.firstName, person.lastName, person.age, person_id))
        cnx.commit()
        cursor.execute("SELECT ID AS id, FirstName AS firstName, LastName AS lastName, Age AS age FROM Person WHERE ID = %s;", (person_id,))
        updated = cursor.fetchone()
        return updated
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.delete("/people/{person_id}")
def delete_person(person_id: int):
    """
    Deletes a person by ID
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Person not found")
        cursor.execute("DELETE FROM Person WHERE ID = %s;", (person_id,))
        cnx.commit()
        return {"message": f"Person {person_id} deleted successfully."}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


# registrations:
@app.get("/events/{event_id}/registrations")
def get_registrations_for_event(event_id: int):
    """
    Gets all registrations for an event, including person names.
    """
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
        cursor.close()
        cnx.close()


# register for an event:
@app.post("/events/{event_id}/registrations")
def register_for_event(event_id: int, body: dict):
    """
    Registers either an attendee, leader, or volunteer for an event.
    """
    attendee_id = body.get("attendeeID")
    leader_id = body.get("leaderID")
    volunteer_id = body.get("volunteerID")
    emergency_contact = body.get("emergencyContact")

    if not attendee_id and not leader_id and not volunteer_id:
        raise HTTPException(400, "Must include attendeeID, leaderID, or volunteerID")

    if not emergency_contact:
        raise HTTPException(400, "Missing emergencyContact")

    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # 1. Get next ID first
        cursor.execute("SELECT IFNULL(MAX(ID),0) + 1 AS nextId FROM Registration;")
        next_id = cursor.fetchone()[0]

        # 2. Try to insert with VolunteerID if volunteer_id is provided
        if volunteer_id:
            try:
                insert_query = """
                    INSERT INTO Registration (ID, EventID, AttendeeID, LeaderID, VolunteerID, EmergencyContact)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (next_id, event_id, attendee_id, leader_id, volunteer_id, emergency_contact))
            except mysql.connector.Error as err:
                # If VolunteerID column doesn't exist, raise a helpful error
                if "Unknown column 'VolunteerID'" in str(err) or "1054" in str(err):
                    raise HTTPException(400, "Volunteer registration requires VolunteerID column in Registration table. Please run the migration script.")
                raise
        else:
            # Regular attendee/leader registration
            insert_query = """
                INSERT INTO Registration (ID, EventID, AttendeeID, LeaderID, EmergencyContact)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (next_id, event_id, attendee_id, leader_id, emergency_contact))
        
        cnx.commit()

        return {"message": "Registration created successfully", "id": next_id}

    except mysql.connector.Error as err:
        raise HTTPException(500, f"DB error: {err}")

    finally:
        cursor.close()
        cnx.close()


# delete registration:
@app.delete("/registrations/{registration_id}")
def delete_registration(registration_id: int):
    """
    Deletes a registration record by ID.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        cursor.execute("SELECT ID FROM Registration WHERE ID = %s;", (registration_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Registration not found")

        cursor.execute("DELETE FROM Registration WHERE ID = %s;", (registration_id,))
        cnx.commit()

        return {"message": "Registration deleted successfully"}

    except mysql.connector.Error as err:
        raise HTTPException(500, f"DB error: {err}")

    finally:
        cursor.close()
        cnx.close()


@app.get("/volunteers")
def get_all_volunteers():
    """
    Gets all volunteers
    """
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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.get("/volunteers/{volunteer_id}")
def get_volunteer_by_id(volunteer_id: int):
    """
    Gets volunteer by ID
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.get("/attendees")
def get_all_attendees():
    """
    Gets all attendees with their person information
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.get("/leaders")
def get_all_leaders():
    """
    Gets all leaders with their person information
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.post("/people/{person_id}/leader")
def create_leader(person_id: int):
    """
    Creates a Leader record for a person.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        # Check if person exists
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Person not found")
        
        # Check if already a leader
        cursor.execute("SELECT ID FROM Leader WHERE PersonID = %s;", (person_id,))
        if cursor.fetchone():
            raise HTTPException(400, "Person is already a leader")
        
        # Get next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM Leader;")
        next_id = cursor.fetchone()[0]
        
        # Insert
        cursor.execute("""
            INSERT INTO Leader (ID, PersonID)
            VALUES (%s, %s);
        """, (next_id, person_id))
        cnx.commit()
        
        return {"message": "Leader created successfully", "id": next_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.post("/people/{person_id}/volunteer")
def create_volunteer(person_id: int):
    """
    Creates a Volunteer record for a person.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        # Check if person exists
        cursor.execute("SELECT ID FROM Person WHERE ID = %s;", (person_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Person not found")
        
        # Check if already a volunteer
        cursor.execute("SELECT ID FROM Volunteer WHERE PersonID = %s;", (person_id,))
        if cursor.fetchone():
            raise HTTPException(400, "Person is already a volunteer")
        
        # Get next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM Volunteer;")
        next_id = cursor.fetchone()[0]
        
        # Insert
        cursor.execute("""
            INSERT INTO Volunteer (ID, PersonID)
            VALUES (%s, %s);
        """, (next_id, person_id))
        cnx.commit()
        
        return {"message": "Volunteer created successfully", "id": next_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.delete("/attendees/{attendee_id}")
def delete_attendee(attendee_id: int):
    """
    Deletes an Attendee record by ID.
    """
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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.delete("/leaders/{leader_id}")
def delete_leader(leader_id: int):
    """
    Deletes a Leader record by ID.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        cursor.execute("SELECT ID FROM Leader WHERE ID = %s;", (leader_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Leader not found")
        
        cursor.execute("DELETE FROM Leader WHERE ID = %s;", (leader_id,))
        cnx.commit()
        
        return {"message": "Leader deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.delete("/volunteers/{volunteer_id}")
def delete_volunteer(volunteer_id: int):
    """
    Deletes a Volunteer record by ID.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        cursor.execute("SELECT ID FROM Volunteer WHERE ID = %s;", (volunteer_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Volunteer not found")
        
        cursor.execute("DELETE FROM Volunteer WHERE ID = %s;", (volunteer_id,))
        cnx.commit()
        
        return {"message": "Volunteer deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.get("/smallgroups")
def get_all_small_groups():
    """
    Gets all small groups
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT ID AS id, Name AS name FROM SmallGroup ORDER BY name;")
        return cursor.fetchall()
    finally:
        cursor.close()
        cnx.close()


@app.post("/smallgroups")
def create_small_group(body: dict = Body(...)):
    """
    Creates a new small group.
    """
    name = body.get("name")
    if not name:
        raise HTTPException(400, "name is required")
    
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        # Get next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroup;")
        next_id = cursor.fetchone()[0]
        
        # Insert
        cursor.execute("""
            INSERT INTO SmallGroup (ID, Name)
            VALUES (%s, %s);
        """, (next_id, name.strip()))
        cnx.commit()
        
        return {"message": "Small group created successfully", "id": next_id, "name": name.strip()}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.delete("/smallgroups/{group_id}")
def delete_small_group(group_id: int):
    """
    Deletes a small group by ID.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        # Check if group exists
        cursor.execute("SELECT ID FROM SmallGroup WHERE ID = %s;", (group_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Small group not found")
        
        # Delete the group (cascade should handle members/leaders if foreign keys are set up)
        cursor.execute("DELETE FROM SmallGroup WHERE ID = %s;", (group_id,))
        cnx.commit()
        
        return {"message": "Small group deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.get("/smallgroups/{group_id}")
def get_small_group(group_id: int):
    """
    Gets small group by ID
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("SELECT ID AS id, Name AS name FROM SmallGroup WHERE ID = %s;", (group_id,))
        group = cursor.fetchone()
        if not group:
            raise HTTPException(404, "Small group not found")

        cursor.execute("SELECT COUNT(*) AS memberCount FROM SmallGroupMember WHERE SmallGroupID = %s;", (group_id,))
        group["memberCount"] = cursor.fetchone()["memberCount"]

        cursor.execute("""
            SELECT L.ID, P.FirstName, P.LastName 
            FROM SmallGroupLeader L
            JOIN Person P ON L.LeaderID = P.ID
            WHERE SmallGroupID = %s;
        """, (group_id,))
        group["leaders"] = cursor.fetchall()

        return group

    finally:
        cursor.close()
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
        cursor.close()
        cnx.close()


@app.get("/smallgroups/{group_id}/leaders")
def get_small_group_leaders(group_id: int):
    """
      Gets leaders of a small group by ID
      """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT L.ID, P.FirstName, P.LastName
            FROM SmallGroupLeader L
            JOIN Person P ON L.LeaderID = P.ID
            WHERE L.SmallGroupID = %s;
        """, (group_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.delete("/smallgroups/{group_id}/members/{member_id}")
def remove_member_from_group(group_id: int, member_id: int):
    """
    Removes a member from a small group.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        cursor.execute("""
            SELECT ID FROM SmallGroupMember 
            WHERE ID = %s AND SmallGroupID = %s;
        """, (member_id, group_id))
        if not cursor.fetchone():
            raise HTTPException(404, "Member not found in this group")
        
        cursor.execute("""
            DELETE FROM SmallGroupMember 
            WHERE ID = %s AND SmallGroupID = %s;
        """, (member_id, group_id))
        cnx.commit()
        
        return {"message": "Member removed successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.post("/smallgroups/{group_id}/leaders")
def add_leader_to_group(group_id: int, body: dict = Body(...)):
    """
    Adds a leader to a small group.
    Note: leaderID should be a Person ID of someone who is a Leader.
    """
    leader_id = body.get("leaderID")
    if not leader_id:
        raise HTTPException(400, "Missing leaderID")

    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        # Check if group exists
        cursor.execute("SELECT ID FROM SmallGroup WHERE ID = %s;", (group_id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Small group not found")
        
        # Check if person is already a leader
        cursor.execute("""
            SELECT ID FROM SmallGroupLeader 
            WHERE LeaderID = %s AND SmallGroupID = %s;
        """, (leader_id, group_id))
        if cursor.fetchone():
            raise HTTPException(400, "Person is already a leader of this group")

        # Get next ID
        cursor.execute("SELECT IFNULL(MAX(ID), 0) + 1 AS nextId FROM SmallGroupLeader;")
        next_id = cursor.fetchone()[0]
        
        # Insert
        cursor.execute("""
            INSERT INTO SmallGroupLeader (ID, LeaderID, SmallGroupID)
            VALUES (%s, %s, %s);
        """, (next_id, leader_id, group_id))
        cnx.commit()

        return {"message": "Leader added successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.delete("/smallgroups/{group_id}/leaders/{leader_id}")
def remove_leader_from_group(group_id: int, leader_id: int):
    """
    Removes a leader from a small group.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()
        
        cursor.execute("""
            SELECT ID FROM SmallGroupLeader 
            WHERE ID = %s AND SmallGroupID = %s;
        """, (leader_id, group_id))
        if not cursor.fetchone():
            raise HTTPException(404, "Leader not found in this group")
        
        cursor.execute("""
            DELETE FROM SmallGroupLeader 
            WHERE ID = %s AND SmallGroupID = %s;
        """, (leader_id, group_id))
        cnx.commit()
        
        return {"message": "Leader removed successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


from datetime import datetime

@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventCreate):
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
        if "cnx" in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.patch("/events/{event_id}", response_model=Event)
def update_event(event_id: int, event: EventUpdate):
    """
    Update an event partially.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Build dynamic update list
        fields = []
        values = []

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

        # If nothing to update
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        sql = f"UPDATE Event SET {', '.join(fields)} WHERE ID = %s"
        values.append(event_id)       # last param is event_id
        cursor.execute(sql, values)
        cnx.commit()

        # Return the updated row
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
        if "cnx" in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()



@app.get("/events/upcoming")
def get_upcoming_events():
    """
    Returns all events whose datetime is in the future.
    """
    try:
        cnx = db_pool.get_connection()
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
        raise HTTPException(500, f"DB error: {err}")

    finally:
        cursor.close()
        cnx.close()


@app.get("/events/{event_id}/comprehensive")
def get_comprehensive_event_summary(event_id: int):
    """
    Comprehensive event summary combining MySQL, Redis, and MongoDB.
    Returns event details, registrations, live check-ins, and notes from all three databases.
    """
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
        
        cursor.close()
        cnx.close()
        
        # ===== Redis: Get live check-in data =====
        check_in_data = {
            "checkedInCount": 0,
            "checkedInStudents": [],
            "checkInTimes": {}
        }
        
        try:
            r = get_redis_conn()
            checked_in_key = f"event:{event_id}:checkedIn"
            times_key = f"event:{event_id}:checkInTimes"
            
            # Get checked-in student IDs
            student_ids = r.smembers(checked_in_key)
            
            if student_ids:
                # Get timestamps
                timestamps = r.hgetall(times_key)
                
                # Convert to list of integers
                student_ids_int = [int(sid) for sid in student_ids]
                
                # Get person details from MySQL for checked-in students
                cnx2 = db_pool.get_connection()
                cursor2 = cnx2.cursor(dictionary=True)
                
                if student_ids_int:
                    format_strings = ",".join(["%s"] * len(student_ids_int))
                    query = f"SELECT ID, FirstName, LastName FROM Person WHERE ID IN ({format_strings});"
                    cursor2.execute(query, tuple(student_ids_int))
                    checked_in_people = cursor2.fetchall()
                    
                    check_in_data["checkedInCount"] = len(checked_in_people)
                    check_in_data["checkedInStudents"] = [
                        {
                            "personId": p["ID"],
                            "firstName": p["FirstName"],
                            "lastName": p["LastName"],
                            "checkInTime": timestamps.get(str(p["ID"]))
                        }
                        for p in checked_in_people
                    ]
                    check_in_data["checkInTimes"] = timestamps
                
                cursor2.close()
                cnx2.close()
        except redis.RedisError as e:
            # Redis might not be available, continue without it
            print(f"Redis error (non-fatal): {e}")
        except Exception as e:
            # Any other error, continue without Redis data
            print(f"Error fetching Redis data (non-fatal): {e}")
        
        # ===== MongoDB: Get event notes/highlights =====
        event_notes = []
        try:
            db = get_mongo_db()
            notes_collection = db["eventNotes"]
            notes = list(notes_collection.find({"eventId": event_id}))
            
            for note in notes:
                note["_id"] = str(note["_id"])
                event_notes.append(note)
        except Exception as e:
            # MongoDB might not be available, continue without it
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
                "attendanceRate": round((check_in_data["checkedInCount"] / len(registrations) * 100) if registrations else 0, 2),
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
    # close cursor safely
        try:
            cursor.close()
        except:
            pass

    # close main DB connection safely
        try:
            cnx.close()
        except:
            pass

    # close 2nd cursor safely (Redis/MySQL join)
        try:
            cursor2.close()
        except:
            pass

        # close 2nd DB connection safely
        try:
            cnx2.close()
        except:
            pass



@app.get("/events/{event_id}")
def get_event_by_id(event_id: int):
    """
    Returns a single event by ID.
    """
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
        cursor.close()
        cnx.close()

@app.get("/events", response_model=list[Event])
def get_all_events():
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

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
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        cursor.close()
        cnx.close()


# mongodb!
@app.get("/event-type/{event_type}")
def get_event_type(event_type: str):
    """
    Fetches a flexible event type definition from MongoDB.
    Returns raw Mongo documents so the schema can vary per event type.
    """
    try:
        db = get_mongo_db()
        collection = db["eventTypes"]

        doc = collection.find_one({"event_type": event_type})

        if not doc:
            raise HTTPException(
                status_code=404,
                detail=f"No event type found with name '{event_type}'."
            )

        # Convert ObjectId → string
        doc["_id"] = str(doc["_id"])

        return doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB error: {e}")


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
    Adds a new note for a specific person. Stores flexible fields in Mongo.
    """

    db = get_mongo_db()

    if "text" not in body:
        raise HTTPException(400, "text is required")

    note = {
        "personId": person_id,
        "text": body["text"],
        "category": body.get("category"),
        "createdBy": body.get("createdBy"),
        "created": datetime.utcnow(),
    }

    result = db["personNotes"].insert_one(note)
    return {"id": str(result.inserted_id)}


@app.patch("/notes/{note_id}")
def update_note_by_id(note_id: str, body: dict):
    """
    Updates an existing note by its id. Adds an updated timestamp.
    """
    db = get_mongo_db()

    body["updated"] = datetime.utcnow()

    updated = db["personNotes"].update_one(
        {"_id": ObjectId(note_id)},
        {"$set": body}
    )

    if updated.matched_count == 0:
        raise HTTPException(404, "Note not found")

    return {"message": "Note updated"}


@app.delete("/notes/{note_id}")
def delete_note_by_id(note_id: str):
    db = get_mongo_db()

    deleted = db["personNotes"].delete_one({"_id": ObjectId(note_id)})

    if deleted.deleted_count == 0:
        raise HTTPException(404, "Note not found")

    return {"message": "Note deleted"}


# parent contacts mongo_db
@app.get("/persons/{person_id}/parent-contacts")
def get_parent_contacts(person_id: int):
    """
    Gets all parent contacts for a specific person from Mongo.
    """
    db = get_mongo_db()
    contacts = list(db["parentContacts"].find({"personId": person_id}))
    for c in contacts:
        c["_id"] = str(c["_id"])
    return contacts


@app.post("/persons/{person_id}/parent-contacts")
def add_parent_contact(person_id: int, body: dict):
    """
    Adds a new parent contact entry for a specific person.
    """
    db = get_mongo_db()

    if "summary" not in body:
        raise HTTPException(400, "summary is required")

    contact = {
        "personId": person_id,
        "method": body.get("method"),
        "summary": body["summary"],
        "date": body.get("date"),  # optional date they contacted you
        "createdBy": body.get("createdBy"),
        "created": datetime.utcnow(),
    }

    result = db["parentContacts"].insert_one(contact)
    return {"id": str(result.inserted_id)}


@app.patch("/parent-contacts/{contact_id}")
def update_parent_contact(contact_id: str, body: dict):
    """
    Updates a parent contact by id. Adds updated timestamp.
    """
    db = get_mongo_db()

    body["updated"] = datetime.utcnow()

    updated = db["parentContacts"].update_one(
        {"_id": ObjectId(contact_id)},
        {"$set": body}
    )

    if updated.matched_count == 0:
        raise HTTPException(404, "Parent contact not found")

    return {"message": "Parent contact updated"}


@app.delete("/parent-contacts/{contact_id}")
def delete_parent_contact(contact_id: str):
    """
    Deletes a parent contact by id.
    """
    db = get_mongo_db()

    deleted = db["parentContacts"].delete_one({"_id": ObjectId(contact_id)})

    if deleted.deleted_count == 0:
        raise HTTPException(404, "Parent contact not found")

    return {"message": "Parent contact deleted"}


# event highlights mong_db
@app.get("/events/{event_id}/notes")
def get_event_notes(event_id: int):
    """
    Gets all highlight entries for a specific event.
    """
    db = get_mongo_db()
    notes = list(db["eventNotes"].find({"eventId": event_id}))
    for n in notes:
        n["_id"] = str(n["_id"])
    return notes


@app.post("/events/{event_id}/notes")
def add_event_notes(event_id: int, body: dict):
    """
    Adds a new highlight entry for a specific event.
    """
    db = get_mongo_db()

    if "notes" not in body:
        raise HTTPException(400, "notes field is required")

    note = {
        "eventId": event_id,
        "notes": body.get("notes"),
        "concerns": body.get("concerns"),
        "studentWins": body.get("studentWins"),
        "createdBy": body.get("createdBy"),
        "created": datetime.utcnow(),
    }

    result = db["eventNotes"].insert_one(note)
    return {"id": str(result.inserted_id)}


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
    Deletes an event highlight entry by id.
    """
    db = get_mongo_db()

    deleted = db["eventNotes"].delete_one({"_id": ObjectId(note_id)})

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
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()


@app.post("/event/{eventId}/checkin/{personId}")
def checkin_person(eventId: int, personId: int):
    """
    Checks in a person to an event using Redis for real-time tracking.
    """
    try:
        r = get_redis_conn()
        
        checked_in_key = f"event:{eventId}:checkedIn"
        times_key = f"event:{eventId}:checkInTimes"
        
        # Check if person exists
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT ID, FirstName, LastName FROM Person WHERE ID = %s;", (personId,))
        person = cursor.fetchone()
        if not person:
            raise HTTPException(404, "Person not found")
        cursor.close()
        cnx.close()
        
        # Add to checked-in set
        r.sadd(checked_in_key, personId)
        
        # Store check-in timestamp
        r.hset(times_key, personId, datetime.utcnow().isoformat())
        
        return {
            "message": f"Person {personId} checked in to event {eventId}",
            "eventId": eventId,
            "personId": personId,
            "checkInTime": datetime.utcnow().isoformat()
        }
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
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
