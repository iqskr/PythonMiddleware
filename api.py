# from flask import Flask, send_file

# app = Flask(__name__)

# @app.route("/vehicle_positions")
# def get_vehicle_positions():
#     return send_file("vehicle_positions.pb", mimetype="application/x-protobuf")

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)


from flask import Flask, send_file

app = Flask(__name__)

@app.route('/gtfs-rt/vehicle_positions.pb', methods=['GET'])
def get_vehicle_positions():
    """Serve the GTFS-RT vehicle positions feed."""
    return send_file("vehicle_positions.pb", mimetype="application/octet-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
