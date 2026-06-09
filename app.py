from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Halat l-amakin (4 spots default khawyin)
parking_spots = {
    1: {"status": "available", "name": None, "token": None},
    2: {"status": "available", "name": None, "token": None},
    3: {"status": "available", "name": None, "token": None},
    4: {"status": "available", "name": None, "token": None},
}

active_reservations = {}

# 🔥 HADA HUWA L-7ALL L-WA3ER: Flask db ghadi i-servi l-website direct!
@app.route('/')
def home():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: index.html not found f had l-dossier!", 404

# 1. API bāsh l-Website y-9ra l-7ala
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(parking_spots)

# 2. API dial l-Reservation
@app.route('/api/reserve', methods=['POST'])
def reserve_spot():
    data = request.json
    token = data.get('token')
    spot_id = int(data.get('spot'))
    name = data.get('name')
    
    active_reservations[token] = {"spot": spot_id, "name": name}
    print(f"[RESERVATION] {name} booked Spot {spot_id}")
    return jsonify({"success": True})

# 3. API dial l-GM65 (QR Code)
@app.route('/api/scan-qr', methods=['POST'])
def scan_qr():
    data = request.json
    token = data.get('token')
    
    if token in active_reservations:
        res = active_reservations[token]
        spot_id = res['spot']
        parking_spots[spot_id] = {"status": "occupied", "name": res['name'], "token": token}
        del active_reservations[token]
        return jsonify({"success": True, "message": "Access Granted"}), 200
    return jsonify({"success": False, "message": "Invalide QR"}), 400

# 4. API dial l-RFID
@app.route('/api/scan-rfid', methods=['POST'])
def scan_rfid():
    data = request.json
    uid = data.get('uid')
    for spot_id, info in parking_spots.items():
        if info['status'] == 'available':
            parking_spots[spot_id] = {"status": "occupied", "name": f"RFID ({uid})", "token": "RFID"}
            return jsonify({"success": True, "message": "Access Granted"}), 200
    return jsonify({"success": False, "message": "Parking Full"}), 400

# 5. API dial l-Exit (IR Sensor)
@app.route('/api/exit', methods=['POST'])
def car_exit():
    data = request.json
    spot_id = int(data.get('spot'))
    if spot_id in parking_spots:
        parking_spots[spot_id] = {"status": "available", "name": None, "token": None}
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

if __name__ == '__main__':
    # host='0.0.0.0' khasha t-bqa bāsh l-madrassa wla l-IoT hardware y9dro y-connectaou m3ak
    app.run(host='0.0.0.0', port=5000, debug=True)