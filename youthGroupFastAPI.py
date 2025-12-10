import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict

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
    dateTime: str
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
    dateTime: str
    location: str
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
    Creates a person.
    """
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        insert_query = """
            INSERT INTO Person (ID, FirstName, LastName, Age)
            VALUES ((SELECT IFNULL(MAX(ID), 0) + 1 FROM Person), %s, %s, %s);
        """
        cursor.execute(insert_query, (person.firstName, person.lastName, person.age))
        cnx.commit()
        cursor.execute("SELECT ID AS id, FirstName, LastName, Age FROM Person ORDER BY ID DESC LIMIT 1;")
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
        cursor.execute("SELECT ID AS id, FirstName, LastName, Age FROM Person WHERE ID = %s;", (person_id,))
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

        query = """
            SELECT R.ID AS id,
                   R.EventID AS eventId,
                   R.AttendeeID AS attendeeId,
                   R.LeaderID AS leaderId,
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
    Registers either an attendee or leader for an event.
    """
    attendee_id = body.get("attendeeID")
    leader_id = body.get("leaderID")
    emergency_contact = body.get("emergencyContact")

    if not attendee_id and not leader_id:
        raise HTTPException(400, "Must include attendeeID or leaderID")

    if not emergency_contact:
        raise HTTPException(400, "Missing emergencyContact")

    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        # 1. Get next ID first
        cursor.execute("SELECT IFNULL(MAX(ID),0) + 1 AS nextId FROM Registration;")
        next_id = cursor.fetchone()[0]

        # 2. Now insert using that ID
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
def add_member_to_group(group_id: int, body: dict):
    """
      Adds a member to a small group by ID
      """
    attendee_id = body.get("attendeeID")
    if not attendee_id:
        raise HTTPException(400, "Missing attendeeID")

    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        cursor.execute("""
            INSERT INTO SmallGroupMember (ID, AttendeeID, SmallGroupID)
            VALUES ((SELECT IFNULL(MAX(ID), 0) + 1 FROM SmallGroupMember), %s, %s);
        """, (attendee_id, group_id))
        cnx.commit()

        return {"message": "Member added successfully"}
    finally:
        cursor.close()
        cnx.close()


@app.post("/smallgroups/{group_id}/leaders")
def add_leader_to_group(group_id: int, body: dict):
    """
      Adds a leader to a small group
      """
    leader_id = body.get("leaderID")
    if not leader_id:
        raise HTTPException(400, "Missing leaderID")

    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor()

        cursor.execute("""
            INSERT INTO SmallGroupLeader (ID, LeaderID, SmallGroupID)
            VALUES ((SELECT IFNULL(MAX(ID), 0) + 1 FROM SmallGroupLeader), %s, %s);
        """, (leader_id, group_id))
        cnx.commit()

        return {"message": "Leader added successfully"}
    finally:
        cursor.close()
        cnx.close()


@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    try:
        cnx = db_pool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        insert_query = """
            INSERT INTO Event (ID, Name, Type, DateTime, Location, Notes)
            VALUES ((SELECT IFNULL(MAX(ID), 0) + 1 FROM Event), %s, %s, %s, %s, %s);
        """

        cursor.execute(insert_query, (
            event.name,
            event.type,
            event.dateTime,
            event.location,
            event.notes
        ))

        cnx.commit()

        # Retrieve last inserted event
        cursor.execute("""
            SELECT
                ID AS id,
                Name AS name,
                Type AS type,
                DateTime AS dateTime,
                Location AS location,
                Notes AS notes
            FROM Event
            ORDER BY ID DESC LIMIT 1;
        """)

        new_event = cursor.fetchone()
        return new_event

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

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


@app.get("/demo", response_class=FileResponse)
async def read_demo():
    """
    Serves the demo HTML page.
    """
    return os.path.join(os.path.dirname(__file__), "index.html")


if __name__ == "__main__":
    print("\nTo run this FastAPI application:")
    print("1. Make sure you have installed the required packages: pip install -r requirements.txt")
    print("2. Run the server: uvicorn demo3_fastapi_app:app --reload --port 8000")
    print("3. Open your browser and go to http://127.0.0.1:8000/docs for the API documentation.")
    print("4. Open your browser and go to http://127.0.0.1:8000/demo for a UI demo.")

    # This part is for demonstration purposes and will not be executed when running with uvicorn
    # uvicorn.run("demo3_fastapi_app:app", host="127.0.0.1", port=8000, reload=True)
