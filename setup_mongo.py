"""
setup_mongo.py - MongoDB Data Initialization Script

This script sets up initial event type data in MongoDB.
Event types are stored in MongoDB because they have flexible schemas - 
different event types can have different fields (some have packing_list, 
others have locations, etc.). This flexibility is MongoDB's strength.

Why MongoDB for event types?
- Different event types need different information
- Youth_Night has: required_items, duration_minutes
- Retreat has: packing_list, schedule (nested object), forms_required
- Service_Day has: locations, what_to_wear, partner_orgs
- In MySQL, we'd need many nullable columns or separate tables
- In MongoDB, each document can have different fields - perfect for this!

Run this script to:
1. Clear existing event types (fresh start)
2. Insert sample event type documents with varied structures
"""

from database import get_mongo_db, close_connections


def setup_mongo_data():
    """
    Sets up flexible event-types in MongoDB.
    
    This function:
    1. Connects to MongoDB
    2. Clears existing event types (for fresh setup)
    3. Inserts sample event type documents
    4. Each event type has different fields (demonstrating MongoDB's flexibility)
    """
    try:
        # Get MongoDB database instance
        db = get_mongo_db()
        
        # Access the "eventTypes" collection (like a table in MySQL)
        # Collections don't need to be created - MongoDB creates them automatically
        event_types = db["eventTypes"]

        # Clear all existing documents in the collection
        # delete_many({}) with empty filter deletes everything
        print("Clearing eventTypes collection...")
        event_types.delete_many({})
        print("Collection cleared.")

        # Define sample event types with DIFFERENT structures
        # This demonstrates MongoDB's schema flexibility
        sample_types = [
            {
                # Youth_Night event type - has required_items, duration_minutes
                "event_type": "Youth_Night",
                "required_items": ["Bible", "Journal", "Pen"],  # Array field
                "description": "Weekly gathering with teaching, worship, and small groups.",
                "duration_minutes": 120,  # Number field
                "extra_notes": "Pizza provided. Parents pick up at 8:15."
            },
            {
                # Retreat event type - has packing_list, schedule (nested object), forms_required
                "event_type": "Retreat",
                "packing_list": [  # Array field (different from required_items)
                    "Sleeping bag",
                    "Warm clothes",
                    "Flashlight",
                    "Bible",
                    "Journal"
                ],
                "schedule": {  # Nested object (not possible in flat MySQL table easily)
                    "day1": "Arrival, worship, smores",
                    "day2": "Hiking, small groups, evening worship",
                    "day3": "Teaching, communion, worship, send-off"
                },
                "forms_required": True,  # Boolean field
                "notes": "Medical release form due by Dec. 4th"
            },
            {
                # Service_Day event type - has locations, what_to_wear, partner_orgs
                "event_type": "Service_Day",
                "locations": ["Food Bank", "Alice Keck Park", "Retirement Home"],  # Array
                "what_to_wear": "Close-toed shoes and work clothes",  # String field
                "bring": ["Water bottle", "Sunscreen"],  # Array field
                "partner_orgs": ["SB Food Bank"]  # Array field
            }
        ]

        # Insert all sample event types at once
        # insert_many() is efficient for bulk inserts
        print("Inserting new event type documents...")
        event_types.insert_many(sample_types)

        print("Event types inserted successfully.")

    except Exception as e:
        # Catch any errors during setup and print them
        print(f"Mongo setup error: {e}")

    finally:
        # Always close connections, even if there was an error
        # This ensures clean shutdown
        close_connections()


if __name__ == "__main__":
    # Only run setup if script is executed directly (not imported)
    print("--- Mongo Setup Start ---")
    setup_mongo_data()
    print("--- Mongo Setup Complete ---")
