
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
        # Use parameterized query to prevent SQL injection

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
