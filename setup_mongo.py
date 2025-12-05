from database import get_mongo_db, close_connections


def setup_mongo_data():
    """
    Sets up flexible event-types in MongoDB.
    """
    try:
        db = get_mongo_db()
        event_types = db["eventTypes"]

        print("Clearing eventTypes collection...")
        event_types.delete_many({})
        print("Collection cleared.")

        sample_types = [
            {
                "event_type": "Youth_Night",
                "required_items": ["Bible", "Journal", "Pen"],
                "description": "Weekly gathering with teaching, worship, and small groups.",
                "duration_minutes": 120,
                "extra_notes": "Pizza provided. Parents pick up at 8:15."
            },
            {
                "event_type": "Retreat",
                "packing_list": [
                    "Sleeping bag",
                    "Warm clothes",
                    "Flashlight",
                    "Bible",
                    "Journal"
                ],
                "schedule": {
                    "day1": "Arrival, worship, smores",
                    "day2": "Hiking, small groups, evening worship",
                    "day3": "Teaching, communion, worship, send-off"
                },
                "forms_required": True,
                "notes": "Medical release form due by Dec. 4th"
            },
            {
                "event_type": "Service_Day",
                "locations": ["Food Bank", "Alice Keck Park", "Retirement Home"],
                "what_to_wear": "Close-toed shoes and work clothes",
                "bring": ["Water bottle", "Sunscreen"],
                "partner_orgs": ["SB Food Bank"]
            }
        ]

        print("Inserting new event type documents...")
        event_types.insert_many(sample_types)

        print("Event types inserted successfully.")

    except Exception as e:
        print(f"Mongo setup error: {e}")

    finally:
        close_connections()


if __name__ == "__main__":
    print("--- Mongo Setup Start ---")
    setup_mongo_data()
    print("--- Mongo Setup Complete ---")
