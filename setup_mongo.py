from database import get_mongo_db, close_connections
from datetime import datetime

def setup_mongo_data():
    """
    Connects to MongoDB, clears the 'event_types' collection,
    and populates it with semantically meaningful, fake bakery review data.
    """
    try:
        db = get_mongo_db()
        event_types_collection = db["eventTypes"]

        # Clear existing data to ensure a clean slate for the demo
        print("Clearing existing data from 'event_types' collection...")
        event_types_collection.delete_many({})
        print("Collection cleared.")

        # Sample review data linked to product IDs from the MySQL database
        event_types_data = [
            {
                "event_id": 1,
                "fields": [
                    {"required_items": "Bible, Pen, Journal"},
                    {"description": "Weekly youth group Bible study"}
                ]
            },
            {
                "event_id": 2,
                "fields": [
                    {"required_items": "Sleeping bag, Chlothes for 3 days, Toiletries, Pillow, Bible, Flashlight"},
                    {"description": "A once a year retreat for all youth group members"}
                ]
            }
        ]

        # Insert the new data
        print("Inserting new sample review data...")
        event_types_collection.insert_many(event_types_data)
        print(f"{len(event_types_data)} event type documents inserted successfully.")

    except Exception as e:
        print(f"An error occurred during MongoDB setup: {e}")
    finally:
        # Close the connection
        close_connections()

if __name__ == "__main__":
    print("--- Starting MongoDB Data Setup ---")
    setup_mongo_data()
    print("--- MongoDB Data Setup Finished ---")
