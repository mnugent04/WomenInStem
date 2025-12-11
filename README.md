# WomenInStem
CS125 Final Project: Youth Group Management System 

### Who is using this?
* Students
* Parents
* Church Leaders

### What do they want to do?
* Schedule events
* View events 
* Manage small groups
* Keep track of attendance
* Registration for events
* Event/ meeting notes

### What should/ shouldn't they be able to do?

**Leaders:**
* Create events
* Update and view events
* Manage and view small groups
* Should not be able to delete past events (to keep records clear)
* Keep track of attendance
* Register/ view registration for events
* Take event notes
* Update list of youth group members or leaders 

**Students/ Parents:**
* Ability to register for events
* Ability to view and edit small groups
* View a schedule of past and upcoming events and small groups
* Check into event

## Team Name:
**Woman In Stem**

## How to get Server Up and Running

This project uses: 
* FastAPI
* Uvicorn
* MySQL
* mysql-connector-python

**To run the API locally:**
## 1. Install Dependencies
```pip install -r requirements.txt```

## 2. Make sure MySQL is Running
```mysql -u root -p -h 127.0.0.1```

## 3. Load the Database!
Hit ctrl^d to exit out of mysql, then type this to load in the data:  
```mysql -u root -p -h 127.0.0.1 < youthGroupData.sql```

**Check that the database exists and is loaded correctly:**  
Reconnect: ```mysql -u root -p -h 127.0.0.1``` 

if you have something running on port 3306, use this instead:
```mysql -u root -p -h 127.0.0.1 -P (your port number)```

Then run:  
```
SHOW DATABASES;  
USE YouthGroupDB;  
SELECT * FROM Person;
```

## 4. Add DB Credentials
Create a file named config.py  
**Put this in config.py:**  
```
DB_USER = "root"  
DB_PASSWORD = "your_password"   
DB_HOST = "host.docker.internal"  
DB_NAME = "YouthGroupDB"
MONGO_URI = "your mongo uri"
MONGO_DB_NAME="youthgroup_db"
```
**Don't forget to add the password!**

This file is ignored by .gitignore.

# 5. Run the FastAPI Server
Quit the sql application and run:  
```uvicorn youthGroupFastAPI:app --reload --port 8000 ```

## 6. View the Data

The base URL only shows the welcome message:  
http://127.0.0.1:8000/  
To see data from the database, go to:  
http://127.0.0.1:8000/people

## 7. Test in Insomnia  
* Open Insomnia  
* Create a GET request  
* Use this URL:  
* http://127.0.0.1:8000/people  
* Click Send  
* You should see a list of people returned as JSON.

## To Dockerize your file:
1.  **Build the Docker Image:**
    From the project root directory, run the `docker build` command:
    ```bash
    docker build -t youthgroup-api .
    ```
2.  **Run the Docker Container (Secure Method):**
    Execute this command from your project root:
    ```bash
    docker run --rm -it \
      -p 8099:8099 \
      youthgroup-api
    ```

## To 'run as normal' as stated below:
* run the required setup for either mongo or redis, named "setup_mongo.py" or "setup_redis.py"
* then recreate the image using 
    ```bash
    docker build -t youthgroup-api .
    ```
* then run the image using 
    ```bash
    docker run --rm -it \
      -p 8099:8099 \
      youthgroup-api
    ```
(just like above!)

* then you can click the link it gives, OR instead you can follow the instructions below for mongo and redis endpoints. 
* NOTE**: if you are running windows, you must manually change the 0.0.0.0 in the link to be localhost, otherwise it will not work!
* Then you can add the link paths below. 

## To run the Mongo endpoints:
* Make sure your config and requirements are up to date
* Make sure your IP address is connected in MongoDB
* Run as normal and go to
* http://127.0.0.1:8000/event-type/{event_type}

## To run the Redis endpoints:
* Make sure your config and requirements are up to date
* Run as normal and go to
* http://127.0.0.1:8000/event/{eventId}/live-checkins

# GraphQL Setup Guide

This guide explains how to set up and use the GraphQL API for the Youth Group Management System.

## Installation

First, install the required GraphQL package:

```bash
pip install strawberry-graphql
```

## Integration with FastAPI

The GraphQL schema is defined in `graphql_schema.py` and can be integrated with your FastAPI app.

### Option 1: Add to existing FastAPI app

In `youthGroupFastAPI.py`, uncomment and add these lines at the end (before `if __name__ == "__main__"`):

```python
# --- GraphQL Integration ---
from graphql_app import graphql_app
app.include_router(graphql_app, prefix="/graphql")
```

### Option 2: Run GraphQL separately

You can also run the GraphQL endpoint separately if needed.

## Accessing GraphQL

Once integrated, you can access:

1. **GraphQL Playground (Interactive UI)**: `http://127.0.0.1:8099/graphql`
2. **GraphQL Endpoint**: `http://127.0.0.1:8099/graphql` (POST requests)

## Example Queries

### Get all people
```graphql
query {
  people {
    id
    firstName
    lastName
    age
  }
}
```

### Get a specific person
```graphql
query {
  person(personId: 1) {
    id
    firstName
    lastName
    age
  }
}
```

### Get all events
```graphql
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
```

### Get small group with members and leaders
```graphql
query {
  smallGroup(groupId: 1) {
    id
    name
  }
  smallGroupMembers(groupId: 1) {
    id
    firstName
    lastName
  }
  smallGroupLeaders(groupId: 1) {
    id
    firstName
    lastName
  }
}
```

### Get comprehensive event summary (all DBMS)
```graphql
query {
  comprehensiveEventSummary(eventId: 1) {
    event {
      id
      name
      type
      dateTime
      location
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
```

### Get person notes from MongoDB
```graphql
query {
  personNotes(personId: 1) {
    id
    text
    category
    createdBy
    created
  }
}
```

### Get live check-ins from Redis
```graphql
query {
  liveCheckIns(eventId: 1) {
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
```

## Example Mutations

### Create a person
```graphql
mutation {
  createPerson(person: {
    firstName: "John"
    lastName: "Doe"
    age: 25
  }) {
    id
    firstName
    lastName
    age
  }
}
```

### Create an event
```graphql
mutation {
  createEvent(event: {
    name: "Youth Night"
    type: "Weekly Gathering"
    dateTime: "2025-02-15T18:00:00"
    location: "Main Hall"
    notes: "Games and message"
  }) {
    id
    name
    type
    dateTime
    location
  }
}
```

### Register for an event
```graphql
mutation {
  registerForEvent(
    eventId: 1
    registration: {
      attendeeId: 1
      emergencyContact: "555-1234"
    }
  ) {
    id
    eventId
    attendeeId
    emergencyContact
  }
}
```

### Add member to small group
```graphql
mutation {
  addMemberToGroup(
    groupId: 1
    input: {
      attendeeId: 1
    }
  ) {
    id
    attendeeId
    smallGroupId
  }
}
```

### Add person note
```graphql
mutation {
  addPersonNote(
    personId: 1
    note: {
      text: "Great participation in today's activity"
      category: "Positive"
      createdBy: "Leader Name"
    }
  ) {
    id
    text
    category
    createdBy
    created
  }
}
```

# Running the Frontend  
* make sure the backend is running
* open a new tab in your terminal and cd into frontend
* make sure you have npm installed, and an newer version
* run 
```bash
npm run dev
```

## Key Features

1. **Multi-DBMS Support**: Queries can fetch data from MySQL, MongoDB, and Redis
2. **Flexible Queries**: Request only the fields you need
3. **Type Safety**: Strong typing with Strawberry
4. **Comprehensive Endpoints**: Special queries that combine data from all databases

## Notes

- The GraphQL schema reuses the same database connections as the REST API
- All resolvers handle errors gracefully
- MongoDB and Redis queries will return empty/null if those services aren't available
- The schema follows the same patterns as your professor's example
