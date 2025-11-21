
USE YouthGroupDB;
-- === Person ===
INSERT INTO Person VALUES
(1, 'Sarah', 'Lopez', 28),
(2, 'James', 'Kim', 32),
(3, 'Ella', 'Brown', 14),
(4, 'Noah', 'Brown', 12),
(5, 'Megan', 'Sharp', 26),
(6, 'David', 'Nguyen', 15);

-- === Volunteer ===
INSERT INTO Volunteer VALUES
(1, 1),  -- Sarah
(2, 2);  -- James

-- === Attendee ===
INSERT INTO Attendee VALUES
(1, 3, 'Laura Brown'),
(2, 4, 'Laura Brown'),
(3, 6, 'Peter Nguyen');

-- === Leader ===
INSERT INTO Leader VALUES
(1, 5),   -- Megan
(2, 1);   -- Sarah (can be both Volunteer + Leader)

-- === Small Groups ===
INSERT INTO SmallGroup VALUES
(1, 'Middle Schoolers'),
(2, 'High School Girls');

-- === SmallGroupMember ===
-- NOTE: AttendeeID references Person.ID (not Attendee.ID) in your schema
INSERT INTO SmallGroupMember VALUES
(1, 3, 1),  -- Ella in Middle School
(2, 4, 1),  -- Noah in Middle School
(3, 6, 2);  -- David in High School group

-- === SmallGroupLeader ===
-- LeaderID references Person.ID (not Leader.ID)
INSERT INTO SmallGroupLeader VALUES
(1, 5, 1),  -- Megan leads Middle School
(2, 1, 2);  -- Sarah leads High School

-- === Events ===
INSERT INTO Event VALUES
(1, 'Youth Night', 'Weekly Gathering', '2025-02-10 18:00:00', 'Main Hall', 'Games + message'),
(2, 'Retreat', 'Overnight Trip', '2025-03-01 09:00:00', 'Camp Ridgeview', 'Bring sleeping bags');

-- === Registration ===
INSERT INTO Registration VALUES
(1, 1, 1, NULL, 'Laura Brown'),   -- Ella registered for Youth Night
(2, 1, 2, NULL, 'Laura Brown'),   -- Noah registered
(3, 1, NULL, 1, 'N/A'),           -- Sarah (leader) registered
(4, 2, 3, NULL, 'Peter Nguyen');  -- David registered for retreat

-- === AttendanceRecord ===
INSERT INTO AttendanceRecord VALUES
(1, 3, 1),   -- Ella attended Youth Night
(2, 4, 1),   -- Noah attended
(3, 5, 1),   -- Megan attended as leader
(4, 6, 2);   -- David attended retreat


