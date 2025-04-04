from flask import Flask, request, jsonify, send_file  # Import send_file
from flask_cors import CORS  # Import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="gps_data",
    user="postgres",
    password="mypass",
    host="localhost"
) 
cur = conn.cursor() 

@app.route('/gps', methods=['POST', 'GET'])
def receive_gps():
    if request.method == 'GET':
        # Fetch the latest GPS data from the database
        cur.execute("SELECT latitude, longitude, timestamp, device_id, trip_id, route_id FROM locations ORDER BY timestamp DESC LIMIT 1;")
        result = cur.fetchone()
        
        if result:
            return jsonify({
                "latitude": result[0],
                "longitude": result[1],
                "timestamp": result[2],
                "device_id": result[3],
                "trip_id": result[4],
                "route_id": result[5],
                #"bearing": result[6]
            })
        else:
            return jsonify({"error": "No GPS data found"}), 404
    
    # Ensure JSON is received only for POST requests
    if request.method == 'POST' and request.content_type != "application/json":
        return jsonify({"error": "Unsupported Media Type. Use application/json"}), 415

    # Handle POST request
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debug: See what GPSLogger sends

        latitude = data.get("latitude")
        longitude = data.get("longitude")
        timestamp = data.get("timestamp")
        device_id = data.get("device_id")
        trip_id = data.get("trip_id")
        route_id = data.get("route_id")
        #bearing = data.get("bearing")

        if latitude is None or longitude is None: 
            return jsonify({"error": "Missing latitude or longitude"}), 400

        # Store in database
        cur.execute("INSERT INTO locations (latitude, longitude, timestamp, device_id, trip_id, route_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                    (latitude, longitude, timestamp, device_id, trip_id, route_id))
        conn.commit()

        return jsonify({"status": "success", "received": data})

    except Exception as e:
        print("Error:", str(e)) 
        return jsonify({"error": "Invalid JSON format"}), 400


# Hosting GTFS-RT file
@app.route('/gtfs-rt/vehicle_positions.pb', methods=['GET'])
def get_vehicle_positions():
    """Serve the GTFS-RT vehicle positions feed."""
    file_path = "vehicle_positions.pb"
    
    if not os.path.exists(file_path):
        return "File not found", 404  # Ensure file exists
    
    return send_file(file_path, mimetype="application/octet-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
