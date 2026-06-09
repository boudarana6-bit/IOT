from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Hadchi li dejà m-gadd l-binôme dyalk (On le garde!)
parking_spots = {
    1: {"status": "available", "name": None, "token": None},
    2: {"status": "available", "name": None, "token": None},
    3: {"status": "available", "name": None, "token": None},
    4: {"status": "available", "name": None, "token": None},
}

active_reservations = {}

# Had la route dejà 3ndkom kat-servi l-index.html direct
@app.route('/')
def home():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur chargement index.html: {str(e)}", 500


# 🌐 HNA L-ZIYADA L-MOUHIMMA: Had la route hiya li ghadi t-connecta m3a l-ESP32
@app.route('/api/parking/status', methods=['POST'])
def update_parking_from_esp32():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
        
    action = data.get('action') # Kat-9ra "entree" wla "sortie"
    print(f"📡 Reçu de l'ESP32 - Action: {action}")
    
    # 🚗 LOGIQUE D'ENTRÉE: Kat-9leb 3la awwel blassa khawia w t-rdha occupied
    if action == 'entree':
        for spot_id, spot_info in parking_spots.items():
            if spot_info["status"] == "available":
                spot_info["status"] = "occupied"
                print(f"🚗 Position {spot_id} est maintenant occupée.")
                return jsonify({"status": "success", "message": f"Spot {spot_id} occupied"}), 200
        return jsonify({"status": "full", "message": "Parking plein!"}), 200
        
    # 🍏 LOGIQUE DE SORTIE: Kat-9leb 3la awwel blassa 3mra w t-khwiha (available)
    elif action == 'sortie':
        # Kat-9lbo b l-3akss bach n-khwio l-places
        for spot_id in sorted(parking_spots.keys(), reverse=True):
            if parking_spots[spot_id]["status"] == "occupied":
                parking_spots[spot_id]["status"] = "available"
                print(f"🍏 Position {spot_id} est maintenant libre (available).")
                return jsonify({"status": "success", "message": f"Spot {spot_id} freed"}), 200
        return jsonify({"status": "already_empty", "message": "Parking déjà vide"}), 200
        
    return jsonify({"status": "error", "message": "Action inconnue"}), 400


# (Ila kano 3ndkom des routes khrrin dejà m-gaddinhom tht f app.py bhal dyal les réservations, khllihom kima huma!)
if __name__ == '__main__':
    # Configuration stable pour Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
