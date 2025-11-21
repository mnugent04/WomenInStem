CREATE DATABASE YouthGroupDB;

USE YouthGroupDB;

CREATE TABLE Person
(
    ID        INT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName  VARCHAR(50) NOT NULL,
    Age       INT         NOT NULL
);

CREATE TABLE Volunteer
(
    ID       INT PRIMARY KEY,
    PersonID INT NOT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person (ID)
);

CREATE TABLE Attendee
(
    ID       INT PRIMARY KEY,
    PersonID INT          NOT NULL,
    Guardian VARCHAR(100) NOT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person (ID)
);

CREATE TABLE Leader
(
    ID       INT PRIMARY KEY,
    PersonID INT NOT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person (ID)
);

CREATE TABLE SmallGroup
(
    ID   INT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE SmallGroupMember
(
    ID           INT PRIMARY KEY,
    AttendeeID   INT NOT NULL,
    SmallGroupID INT NOT NULL,
    FOREIGN KEY (AttendeeID) REFERENCES Person (ID),
    FOREIGN KEY (SmallGroupID) REFERENCES SmallGroup (ID)
);

CREATE TABLE SmallGroupLeader
(
    ID           INT PRIMARY KEY,
    LeaderID     INT NOT NULL,
    SmallGroupID INT NOT NULL,
    FOREIGN KEY (LeaderID) REFERENCES Person (ID),
    FOREIGN KEY (SmallGroupID) REFERENCES SmallGroup (ID)
);

CREATE TABLE Event
(
    ID       INT PRIMARY KEY,
    Name     VARCHAR(50)  NOT NULL,
    Type     VARCHAR(100) NOT NULL,
    DateTime DATETIME     NOT NULL,
    Location VARCHAR(100) NOT NULL,
    Notes    VARCHAR(255)
);

CREATE TABLE Registration
(
    ID               INT PRIMARY KEY,
    EventID          INT         NOT NULL,
    AttendeeID       INT,
    LeaderID         INT,
    EmergencyContact VARCHAR(50) NOT NULL,
    FOREIGN KEY (EventID) REFERENCES Event (ID),
    FOREIGN KEY (AttendeeID) REFERENCES Attendee (ID),
    FOREIGN KEY (LeaderID) REFERENCES Leader (ID),
    CONSTRAINT ValidRegister CHECK ((AttendeeID IS NOT NULL) OR (LeaderID IS NOT NULL))
);

CREATE TABLE AttendanceRecord
(
    ID       INT PRIMARY KEY,
    PersonID INT NOT NULL,
    EventID  INT NOT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person (ID),
    FOREIGN KEY (EventID) REFERENCES Event (ID)
);



