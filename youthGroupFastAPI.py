
import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os

# --- Database Configuration ---
# NOTE: Update with your database credential
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

# --- Connection Pooling ---
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="fastapi_pool",
        pool_size=5,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DB_NAME
    )
    print("Database connection pool created successfully.")
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    exit()

# --- FastAPI App ---
app = FastAPI(
    title="Youth Group API",
    description="An API for interacting with the YouthGroupDB database.",
    version="1.0.0"
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
