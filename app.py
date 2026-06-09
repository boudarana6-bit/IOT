from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# 🚗 L-Dictionnaire dyal les places (Khllito perfectly kima m-gaddo l-binôme dyalk)
parking_spots = {
    1: {"status": "available", "name": None, "token": None},
    2: {"status": "available", "name": None, "token": None},
    3: {"status": "available", "name": None, "token": None},
    4: {"status": "available", "name": None, "token": None},
}

active_reservations = {}

# 🌐 La route principal li kat-7ll l-index.html f l-site web
@app.route('/')
def home():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur chargement index.html: {str(e)}", 500


# 📡 LA ROUTE L-JDIDA: Hiya li ghadi t-reçoit l-data mn l-ESP32
@app.route('/api/parking/status', methods=['POST'])
def update_parking_from_esp32():
    data = request.get_json()
    
    # Vérification d l-data
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
        
    action = data.get('action') # Kat-9ra "entree" (RFID) wla "sortie" (IR)
    print(f"📡 Reçu de l'ESP32 - Action de la voiture: {action}")
    
    # 1. ILA KANT L-ACTION = ENTREE (RFID khdam w la barrière tl3at)
    if action == 'entree':
        # Kat-9lebo 3la awwel blassa khawia (available) mn 1 l 4 bach n-3mrouha
        for spot_id, spot_info in parking_spots.items():
            if spot_info["status"] == "available":
                spot_info["status"] = "occupied" # Reddiha 3amra
                print(f"🚗 Position {spot_id} rj3at msdouda / occupied.")
                return jsonify({"status": "success", "message": f"Spot {spot_id} occupied"}), 200
        return jsonify({"status": "full", "message": "Parking plein!"}), 200
        
    # 2. ILA KANT L-ACTION = SORTIE (Capteur IR d l-khroj khdam w la barrière tl3at)
    elif action == 'sortie':
        # Kat-9lebo 3la l-places m-3ksin (mn 4 l 1) bach n-khwio l-places li 3amrin
        for spot_id in sorted(parking_spots.keys(), reverse=True):
            if parking_spots[spot_id]["status"] == "occupied":
                parking_spots[spot_id]["status"] = "available" # Reddiha khawia
                print(f"🍏 Position {spot_id} rj3at khawia / available.")
                return jsonify({"status": "success", "message": f"Spot {spot_id} freed"}), 200
        return jsonify({"status": "already_empty", "message": "Parking déjà vide"}), 200
        
    return jsonify({"status": "error", "message": "Action inconnue"}), 400


# Configuration s7i7a dyal l-Port bach Render y-déployer le code direct bla error
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
