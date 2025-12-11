DROP DATABASE YouthGroupDB;
CREATE DATABASE YouthGroupDB;
USE YouthGroupDB;

CREATE TABLE Person
(
    ID        INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName  VARCHAR(50) NOT NULL,
    Age       INT         NOT NULL
);

CREATE TABLE Volunteer
(
    ID       INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT NOT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person (ID)
);

CREATE TABLE Attendee
(
    ID       INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT          NOT NULL,
    Guardian VARCHAR(100) NOT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person (ID)
);

CREATE TABLE Leader
(
    ID       INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT NOT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person (ID)
);

CREATE TABLE SmallGroup
(
    ID   INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL
);

CREATE TABLE SmallGroupMember
(
    ID           INT AUTO_INCREMENT PRIMARY KEY,
    AttendeeID   INT NOT NULL,
    SmallGroupID INT NOT NULL,
    FOREIGN KEY (AttendeeID) REFERENCES Person (ID),
    FOREIGN KEY (SmallGroupID) REFERENCES SmallGroup (ID)
);

CREATE TABLE SmallGroupLeader
(
    ID           INT AUTO_INCREMENT PRIMARY KEY,
    LeaderID     INT NOT NULL,
    SmallGroupID INT NOT NULL,
    FOREIGN KEY (LeaderID) REFERENCES Person (ID),
    FOREIGN KEY (SmallGroupID) REFERENCES SmallGroup (ID)
);

CREATE TABLE Event
(
    ID       INT AUTO_INCREMENT PRIMARY KEY,
    Name     VARCHAR(50)  NOT NULL,
    Type     VARCHAR(100) NOT NULL,
    DateTime DATETIME     NOT NULL,
    Location VARCHAR(100) NOT NULL,
    Notes    VARCHAR(255)
);

CREATE TABLE Registration
(
    ID               INT AUTO_INCREMENT PRIMARY KEY,
    EventID          INT         NOT NULL,
    AttendeeID       INT,
    LeaderID         INT,
    VolunteerID      INT         NULL,
    EmergencyContact VARCHAR(50) NOT NULL,
    FOREIGN KEY (EventID) REFERENCES Event (ID),
    FOREIGN KEY (AttendeeID) REFERENCES Attendee (ID),
    FOREIGN KEY (LeaderID) REFERENCES Leader (ID),
    FOREIGN KEY (VolunteerID) REFERENCES Volunteer (ID),
    CONSTRAINT ValidRegister CHECK (
        (AttendeeID IS NOT NULL) OR
        (LeaderID IS NOT NULL) OR
        (VolunteerID IS NOT NULL))
);

CREATE TABLE AttendanceRecord
(
    ID       INT AUTO_INCREMENT PRIMARY KEY,
    PersonID INT NOT NULL,
    EventID  INT NOT NULL,
    FOREIGN KEY (PersonID) REFERENCES Person (ID),
    FOREIGN KEY (EventID) REFERENCES Event (ID)
);




