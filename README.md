# WomenInStem
CS125 Final Project: Youth Group Management System 

### Who is using this?
* Students
* Parents
* Church Leaders

### What do they want to do?
* Schedule events
* View calendar of events 
* Manage small groups
* Keep track of attendance
* Registration for events
* Event/ meeting notes

### What should/ shouldn't they be able to do?

**Leaders:**
* Create events
* Update calendar and view calendar
* Manage and view small groups
* Should not be able to delete past events (to keep records clear)
* Keep track of attendance
* Register/ view registration for events
* Take meeting and event notes
* Should not be able to delete notes that are not theirs
* Update contact list of youth group parishioners 
* Head pastor/ select leaders have master privilege and are able to grant other access

**Students/ Parents:**
* Ability to register for events
* Ability to view but not edit small groups
* View a schedule of past and upcoming events and small groups
* Check into event
* Should not be able to edit calendar, small groups, registration, or events

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
DB_HOST = "127.0.0.1"  
DB_NAME = "YouthGroupDB"
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