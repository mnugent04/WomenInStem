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
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, REDIS_SSL, REDIS_USERNAME, REDIS_PORT, REDIS_PASSWORD, REDIS_HOST, MONGO_URI
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
