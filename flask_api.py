# API Server untuk ESP32 Smart Water Meter
# Versi alternatif menggunakan Flask (lebih cocok untuk REST API)

from flask import Flask, request, jsonify
import json
import datetime
from pathlib import Path

app = Flask(__name__)

DATA_FILE = Path("water_flow_data.json")
DEVICES_FILE = Path("registered_devices.json")

def init_files():
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps([]))
    if not DEVICES_FILE.exists():
        devices = {
            "ESP32_WATER_001": {
                "name": "Water Meter 001",
                "location": "Main Building",
                "registered_at": datetime.datetime.now().isoformat()
            }
        }
        DEVICES_FILE.write_text(json.dumps(devices, indent=2))

init_files()

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def load_devices():
    with open(DEVICES_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Smart Water Meter API",
        "version": "1.0",
        "endpoints": {
            "verify": "/verify?device_id=<device_id>",
            "data": "/data?device_id=<device_id> (POST)"
        }
    })

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    # Try to get device_id from query parameter first
    device_id = request.args.get('device_id')
    
    # If not in query, try to get from JSON body (for POST requests)
    if not device_id and request.is_json:
        data = request.get_json()
        device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({
            "status": "error",
            "message": "device_id parameter required"
        }), 400
    
    devices = load_devices()
    
    if device_id in devices:
        return jsonify({
            "status": "verified",
            "device_id": device_id,
            "device_info": devices[device_id]
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "device not registered"
        }), 404

@app.route('/data', methods=['POST'])
def receive_data():
    # Try to get device_id from query parameter
    device_id = request.args.get('device_id')
    
    try:
        incoming_data = request.get_json()
        
        # Check if it's wrapped format: {"device_id": "...", "data": [...]}
        if isinstance(incoming_data, dict) and 'device_id' in incoming_data and 'data' in incoming_data:
            # New format with wrapper
            device_id = incoming_data['device_id']  # Override from JSON body
            data_array = incoming_data['data']
        elif isinstance(incoming_data, list):
            # Old format: direct array
            data_array = incoming_data
        else:
            return jsonify({
                "status": "error",
                "message": "data must be a JSON array or object with device_id and data fields"
            }), 400
        
        if not device_id:
            return jsonify({
                "status": "error",
                "message": "device_id required (in query param or JSON body)"
            }), 400
        
        devices = load_devices()
        if device_id not in devices:
            return jsonify({
                "status": "error",
                "message": "device not registered"
            }), 404
        
        # Load existing data
        all_data = load_data()
        
        # Add metadata
        for record in data_array:
            record['device_id'] = device_id
            record['received_at'] = datetime.datetime.now().isoformat()
            all_data.append(record)
        
        # Save
        save_data(all_data)
        
        return jsonify({
            "status": "success",
            "message": f"Received {len(data_array)} data points",
            "device_id": device_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    devices = load_devices()
    return jsonify(devices), 200

@app.route('/latest', methods=['GET'])
def get_latest():
    device_id = request.args.get('device_id')
    all_data = load_data()
    
    if device_id:
        device_data = [d for d in all_data if d.get('device_id') == device_id]
        if device_data:
            return jsonify(device_data[-1]), 200
        else:
            return jsonify({"status": "error", "message": "no data found"}), 404
    else:
        if all_data:
            return jsonify(all_data[-1]), 200
        else:
            return jsonify({"status": "error", "message": "no data available"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
