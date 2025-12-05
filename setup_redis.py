from datetime import datetime

from database import get_redis_conn, close_connections


def setup_redis_data():
    """
    Connects to Redis and sets up an event check-in data for youth night.
    """
    try:
        r = get_redis_conn()

        event_id = 1  # youth night
        sample_students = [3, 4, 6]  # student IDs already in MySQL

        set_key = f"event:{event_id}:checkedIn"
        times_key = f"event:{event_id}:checkInTimes"

        print(f"Clearing existing Redis keys for event {event_id}...")
        r.delete(set_key)
        r.delete(times_key)

        print("Adding sample students to Redis...")

        for sid in sample_students:
            r.sadd(set_key, sid)
            r.hset(times_key, sid, datetime.utcnow().isoformat())

        print("Redis setup complete.")

        # Verify results
        print("\n--- Verification ---")
        print("Checked-in students:", r.smembers(set_key))
        print("Timestamps:", r.hgetall(times_key))

    except Exception as e:
        print(f"An error occurred during Redis setup: {e}")

    finally:
        close_connections()

if __name__ == "__main__":
    print("--- Starting Redis Data Setup ---")
    setup_redis_data()
    print("--- Redis Data Setup Finished ---")
