# graphql_schema.py

import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional

from youthGroupFastAPI import db_pool


# ==========================================
# PERSON TYPE
# ==========================================

@strawberry.type
class PersonType:
    id: int
    firstName: str
    lastName: str
    age: Optional[int]


# ==========================================
# REGISTRATION TYPE
# ==========================================

@strawberry.type
class RegistrationType:
    id: int
    eventId: int
    person: PersonType
    role: str  # attendee | leader | volunteer


# ==========================================
# EVENT TYPE
# ==========================================

# ✅ THE IMPORTANT FIX: Typed resolver function
def resolve_event_registrations(parent: EventType) -> List[RegistrationType]:
    cnx = db_pool.get_connection()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT R.ID AS registrationId,
               R.EventID AS eventId,
               P.ID AS personId,
               P.FirstName,
               P.LastName,
               P.Age,
               CASE
                 WHEN R.AttendeeID IS NOT NULL THEN 'attendee'
                 WHEN R.LeaderID IS NOT NULL THEN 'leader'
                 WHEN R.VolunteerID IS NOT NULL THEN 'volunteer'
               END AS role
        FROM Registration R
        LEFT JOIN Attendee A ON R.AttendeeID = A.ID
        LEFT JOIN Leader L ON R.LeaderID = L.ID
        LEFT JOIN Volunteer V ON R.VolunteerID = V.ID
        LEFT JOIN Person P ON (A.PersonID = P.ID OR L.PersonID = P.ID OR V.PersonID = P.ID)
        WHERE R.EventID = %s;
        """,
        (parent.id,),
    )

    rows = cursor.fetchall()
    cursor.close()
    cnx.close()

    return [
        RegistrationType(
            id=r["registrationId"],
            eventId=r["eventId"],
            role=r["role"],
            person=PersonType(
                id=r["personId"],
                firstName=r["FirstName"],
                lastName=r["LastName"],
                age=r["Age"],
            ),
        )
        for r in rows
    ]


@strawberry.type
class EventType:
    id: int
    name: str
    type: str
    dateTime: str
    location: str
    notes: Optional[str]

    registrations: List[RegistrationType] = strawberry.field(
        resolver=resolve_event_registrations
    )



# ==========================================
# RESOLVERS
# ==========================================

def resolve_people() -> List[PersonType]:
    cnx = db_pool.get_connection()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Person")
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()

    return [
        PersonType(
            id=r["ID"],
            firstName=r["FirstName"],
            lastName=r["LastName"],
            age=r["Age"],
        )
        for r in rows
    ]



# ==========================================
# ROOT QUERY
# ==========================================

@strawberry.type
class Query:
    people: List[PersonType] = strawberry.field(resolver=resolve_people)
    events: List[EventType] = strawberry.field(resolver=resolve_events)


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
