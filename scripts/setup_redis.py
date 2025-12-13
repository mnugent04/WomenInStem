"""
setup_redis.py - Redis Data Initialization Script

This script sets up sample check-in data in Redis for testing.
Redis is used for live check-ins because:
- Very fast (in-memory storage)
- Perfect for real-time data that changes frequently
- Supports sets (for list of checked-in students) and hashes (for timestamps)
- Data can be lost on restart (acceptable for temporary check-in data)

Redis Data Structures Used:
- SET: Stores unique student IDs who are checked in (no duplicates)
- HASH: Stores check-in timestamps for each student (key-value pairs)

Key Naming Convention:
- event:{event_id}:checkedIn - SET containing student IDs
- event:{event_id}:checkInTimes - HASH mapping student ID -> timestamp

Run this script to populate Redis with sample check-in data.
"""

from datetime import datetime

from backend.database import get_redis_conn, close_connections


def setup_redis_data():
    """
    Connects to Redis and sets up sample event check-in data for testing.
    
    This function demonstrates Redis data structures:
    1. SET: Used to store which students are checked in (unique IDs)
    2. HASH: Used to store check-in timestamps for each student
    
    Why Redis for check-ins?
    - Check-ins happen frequently and need to be fast
    - Data is temporary (only needed during event)
    - Real-time queries need to be instant
    - Can handle many concurrent check-ins
    """
    try:
        # Get Redis client connection
        r = get_redis_conn()

        # Define event and sample student IDs
        event_id = 1  # youth night event
        sample_students = [3, 4, 6]  # student IDs that should already exist in MySQL

        # Define Redis keys using a naming convention
        # Convention: event:{event_id}:{data_type}
        set_key = f"event:{event_id}:checkedIn"      # SET: list of checked-in student IDs
        times_key = f"event:{event_id}:checkInTimes"  # HASH: student ID -> timestamp mapping

        # Clear any existing data for this event (fresh start)
        print(f"Clearing existing Redis keys for event {event_id}...")
        r.delete(set_key)    # Delete the SET if it exists
        r.delete(times_key)  # Delete the HASH if it exists

        print("Adding sample students to Redis...")

        # Add each student to Redis
        for sid in sample_students:
            # SADD: Add student ID to the SET (Set Add)
            # If student already in set, Redis ignores it (sets are unique)
            r.sadd(set_key, sid)
            
            # HSET: Set timestamp in HASH (Hash Set)
            # Stores student ID as key, ISO timestamp as value
            # Format: {student_id: "2024-01-15T10:30:00"}
            r.hset(times_key, sid, datetime.utcnow().isoformat())

        print("Redis setup complete.")

        # Verify results by reading back the data
        print("\n--- Verification ---")
        # SMEMBERS: Get all members of the SET (all checked-in student IDs)
        print("Checked-in students:", r.smembers(set_key))
        # HGETALL: Get all key-value pairs from the HASH (all student ID -> timestamp mappings)
        print("Timestamps:", r.hgetall(times_key))

    except Exception as e:
        # Catch any errors during setup
        print(f"An error occurred during Redis setup: {e}")

    finally:
        # Always close connections, even if there was an error
        close_connections()


if __name__ == "__main__":
    # Only run setup if script is executed directly (not imported)
    print("--- Starting Redis Data Setup ---")
    setup_redis_data()
    print("--- Redis Data Setup Finished ---")
