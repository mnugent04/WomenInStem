from database import get_mongo_db, close_connections
from datetime import datetime

def setup_mongo_data():
    """
    Connects to MongoDB, clears the 'product_reviews' collection,
    and populates it with semantically meaningful, fake bakery review data.
    """
    try:
        db = get_mongo_db()
        event_types_collection = db["eventTypes"]

        # Clear existing data to ensure a clean slate for the demo
        print("Clearing existing data from 'product_reviews' collection...")
        event_types_collection.delete_many({})
        print("Collection cleared.")

        # Sample review data linked to product IDs from the MySQL database
        event_types_data = [
            {
                "eventId": 1,
                "fields": [
                    {"name": "packing_list", "type": "text"},
                    {"name": "bring_a_friend", "type": "boolean"},
                    {"name": "number_of_sessions", "type": "number"}
                ]
            },
            {
                "eventId": 2,
                "fields": [
                    {"name": "location", "type": "text"},
                    {"name": "required_items", "type": "text"},
                    {"name": "signup_deadline", "type": "date"}
                ]
            }
        ]

        # Insert the new data
        print("Inserting new sample review data...")
        event_types_collection.insert_many(event_types_data)
        print(f"{len(event_types_data)} product review documents inserted successfully.")

    except Exception as e:
        print(f"An error occurred during MongoDB setup: {e}")
    finally:
        # Close the connection
        close_connections()

if __name__ == "__main__":
    print("--- Starting MongoDB Data Setup ---")
    setup_mongo_data()
    print("--- MongoDB Data Setup Finished ---")
