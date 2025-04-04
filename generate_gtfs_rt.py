import psycopg2
import time
from google.transit import gtfs_realtime_pb2

# Database connection
DB_CONFIG = {
    "dbname": "gps_data",
    "user": "postgres",
    "password": "mypass",
    "host": "localhost"
}

def fetch_latest_gps():
    """Fetch the latest GPS data from PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT latitude, longitude, timestamp FROM locations ORDER BY timestamp DESC LIMIT 1;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result  # (latitude, longitude, timestamp) or None

def generate_gtfs_rt():
    """Generate GTFS-RT vehicle_positions.pb"""
    gps_data = fetch_latest_gps()
    if not gps_data:
        print("No GPS data available.")
        return

    latitude, longitude, timestamp = gps_data

    # Create GTFS-RT Feed
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = int(time.time())

    # Create a vehicle position entity
    entity = feed.entity.add()
    entity.id = "bus_1"  # Unique vehicle ID

    vehicle = entity.vehicle
    vehicle.trip.trip_id = "test_trip"  # Assign a valid trip_id if available
    vehicle.vehicle.id = "bus_1"
    vehicle.position.latitude = float(latitude)
    vehicle.position.longitude = float(longitude)
    vehicle.timestamp = int(timestamp.timestamp())  # Ensure timestamp is in seconds

    # Save to file
    with open("vehicle_positions.pb", "wb") as f:
        f.write(feed.SerializeToString())

    print("Generated vehicle_positions.pb")

if __name__ == "__main__":
    while True:
        generate_gtfs_rt()
        time.sleep(10)  # Update every 10 seconds
