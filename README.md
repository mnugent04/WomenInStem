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
* Should not be able to delete notes that are not theirs
* Update list of youth group members or leaders 
* Head pastor/ select leaders have master privilege and are able to grant other access

**Students/ Parents:**
* Ability to register for events
* Ability to view but not edit small groups
* View a schedule of past and upcoming events and small groups
* Check into event
* Should not be able to edit small groups, registration, or events

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
