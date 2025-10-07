import streamlit as st
import json
import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict

# File untuk menyimpan data
DATA_FILE = Path("water_flow_data.json")
DEVICES_FILE = Path("registered_devices.json")

# Inisialisasi file jika belum ada
def init_files():
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps([]))
    if not DEVICES_FILE.exists():
        # Register default device
        devices = {
            "ESP32_WATER_001": {
                "name": "Water Meter 001",
                "location": "Main Building",
                "registered_at": datetime.datetime.now().isoformat()
            }
        }
        DEVICES_FILE.write_text(json.dumps(devices, indent=2))

init_files()

# Load data
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def load_devices():
    try:
        with open(DEVICES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=2)

# API Endpoints (menggunakan Streamlit query params)
def handle_verify():
    """Handle /verify endpoint - accepts both GET and POST with JSON body"""
    params = st.query_params
    device_id = params.get("device_id", None)
    
    # Also try to get from session state (for POST with JSON body)
    if not device_id and 'verify_device_id' in st.session_state:
        device_id = st.session_state.verify_device_id
    
    if not device_id:
        return {"status": "error", "message": "device_id required"}
    
    devices = load_devices()
    if device_id in devices:
        return {
            "status": "verified",
            "device_id": device_id,
            "device_info": devices[device_id]
        }
    else:
        return {"status": "error", "message": "device not registered"}

def handle_data():
    """Handle /data endpoint - accepts JSON with device_id and data array"""
    params = st.query_params
    device_id = params.get("device_id", None)
    
    # Also try to get from incoming data (for JSON body)
    if 'incoming_data' in st.session_state:
        incoming_payload = st.session_state.incoming_data
        
        # Check if it's the new JSON format with device_id wrapper
        if isinstance(incoming_payload, dict) and 'device_id' in incoming_payload:
            device_id = incoming_payload['device_id']
            incoming_data = incoming_payload.get('data', [])
        else:
            # Old format: direct array
            incoming_data = incoming_payload if isinstance(incoming_payload, list) else []
    else:
        return {"status": "error", "message": "no data received"}
    
    if not device_id:
        return {"status": "error", "message": "device_id required"}
    
    # Cek apakah device terdaftar
    devices = load_devices()
    if device_id not in devices:
        return {"status": "error", "message": "device not registered"}
    
    # Load existing data
    all_data = load_data()
    
    # Tambahkan metadata
    for record in incoming_data:
        record['device_id'] = device_id
        record['received_at'] = datetime.datetime.now().isoformat()
        all_data.append(record)
    
    # Save
    save_data(all_data)
    
    return {
        "status": "success",
        "message": f"Received {len(incoming_data)} data points",
        "device_id": device_id
    }

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Smart Water Meter Monitor",
        page_icon="💧",
        layout="wide"
    )
    
    st.title("💧 Smart Water Meter Monitoring System")
    
    # Sidebar untuk navigasi
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "API Testing", "Device Management", "Raw Data"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "API Testing":
        show_api_testing()
    elif page == "Device Management":
        show_device_management()
    elif page == "Raw Data":
        show_raw_data()
    
    # Footer dengan API info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔗 API Endpoints")
    base_url = "https://your-app.streamlit.app"
    st.sidebar.code(f"{base_url}/verify?device_id=ESP32_WATER_001", language="text")
    st.sidebar.code(f"{base_url}/data?device_id=ESP32_WATER_001", language="text")

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Load data
    all_data = load_data()
    devices = load_devices()
    
    if not all_data:
        st.info("📭 No data received yet. Waiting for ESP32 to send data...")
        st.markdown("""
        ### Setup Instructions:
        1. Update your ESP32 code with:
           - `SERVER_URL = "https://your-streamlit-app.streamlit.app"`
           - Your WiFi credentials
        2. Upload code to ESP32
        3. Device will automatically start sending data
        """)
        return
    
    # Statistik
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(all_data))
    
    with col2:
        unique_devices = len(set([d.get('device_id', 'unknown') for d in all_data]))
        st.metric("Active Devices", unique_devices)
    
    with col3:
        if all_data:
            latest_record = all_data[-1]
            st.metric("Latest Flow Rate", f"{latest_record.get('flow_rate', 0):.2f} L/min")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    if 'received_at' in df.columns:
        df['received_at'] = pd.to_datetime(df['received_at'])
        df = df.sort_values('received_at', ascending=False)
    
    # Filter by device
    if 'device_id' in df.columns:
        selected_device = st.selectbox(
            "Select Device",
            options=['All'] + list(df['device_id'].unique())
        )
        
        if selected_device != 'All':
            df_filtered = df[df['device_id'] == selected_device]
        else:
            df_filtered = df
    else:
        df_filtered = df
    
    # Chart
    st.subheader("📈 Flow Rate Over Time")
    if 'flow_rate' in df_filtered.columns and len(df_filtered) > 0:
        chart_data = df_filtered[['received_at', 'flow_rate']].set_index('received_at')
        st.line_chart(chart_data)
    else:
        st.info("No flow rate data available")
    
    # Recent data table
    st.subheader("📋 Recent Data (Last 20 records)")
    display_cols = ['device_id', 'flow_rate', 'volume', 'timestamp', 'received_at']
    available_cols = [col for col in display_cols if col in df_filtered.columns]
    st.dataframe(df_filtered[available_cols].head(20), use_container_width=True)

def show_api_testing():
    st.header("🧪 API Testing")
    
    st.markdown("""
    Test your API endpoints here before deploying to ESP32.
    """)
    
    # Test Verify Endpoint
    st.subheader("1. Test /verify Endpoint")
    device_id_verify = st.text_input("Device ID (verify)", value="ESP32_WATER_001")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test Verify (GET with Query Param)"):
            devices = load_devices()
            if device_id_verify in devices:
                st.success(f"✅ Device verified: {device_id_verify}")
                st.json({
                    "status": "verified",
                    "device_id": device_id_verify,
                    "device_info": devices[device_id_verify]
                })
            else:
                st.error(f"❌ Device not registered: {device_id_verify}")
    
    with col2:
        if st.button("Test Verify (POST with JSON Body)"):
            # Simulate POST with JSON body
            st.session_state.verify_device_id = device_id_verify
            devices = load_devices()
            if device_id_verify in devices:
                st.success(f"✅ Device verified: {device_id_verify}")
                st.json({
                    "status": "verified",
                    "device_id": device_id_verify,
                    "device_info": devices[device_id_verify]
                })
            else:
                st.error(f"❌ Device not registered: {device_id_verify}")
            
            if 'verify_device_id' in st.session_state:
                del st.session_state.verify_device_id
    
    st.markdown("---")
    
    # Test Data Endpoint
    st.subheader("2. Test /data Endpoint")
    device_id_data = st.text_input("Device ID (data)", value="ESP32_WATER_001")
    
    st.markdown("**Sample Data (JSON format with device_id wrapper):**")
    sample_data_wrapped = {
        "device_id": "ESP32_WATER_001",
        "data": [
            {"timestamp": 123456789, "flow_rate": 2.5, "volume": 150.2},
            {"timestamp": 123456849, "flow_rate": 2.3, "volume": 152.5},
        ]
    }
    
    data_input = st.text_area(
        "Data (JSON with device_id and data array)",
        value=json.dumps(sample_data_wrapped, indent=2),
        height=250
    )
    
    if st.button("Test Send Data"):
        try:
            data = json.loads(data_input)
            
            # Check format: could be wrapped (with device_id) or direct array
            if isinstance(data, dict) and 'device_id' in data and 'data' in data:
                # New format: {"device_id": "...", "data": [...]}
                device_id_from_json = data['device_id']
                data_array = data['data']
                st.info(f"📦 Detected JSON format with device_id wrapper")
            elif isinstance(data, list):
                # Old format: direct array
                device_id_from_json = device_id_data
                data_array = data
                st.info(f"📦 Detected direct array format")
            else:
                st.error("Data must be either a JSON array or an object with 'device_id' and 'data' fields")
                return
            
            # Simpan ke session state
            st.session_state.incoming_data = data
            
            # Process
            devices = load_devices()
            if device_id_from_json not in devices:
                st.error(f"❌ Device not registered: {device_id_from_json}")
            else:
                # Save data
                all_data = load_data()
                for record in data_array:
                    record['device_id'] = device_id_from_json
                    record['received_at'] = datetime.datetime.now().isoformat()
                    all_data.append(record)
                save_data(all_data)
                
                st.success(f"✅ Successfully received {len(data_array)} data points!")
                st.json({
                    "status": "success",
                    "message": f"Received {len(data_array)} data points",
                    "device_id": device_id_from_json
                })
                
                # Clear session state
                if 'incoming_data' in st.session_state:
                    del st.session_state.incoming_data
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {str(e)}")

def show_device_management():
    st.header("🔧 Device Management")
    
    devices = load_devices()
    
    # Show registered devices
    st.subheader("Registered Devices")
    if devices:
        for device_id, info in devices.items():
            with st.expander(f"📱 {device_id}"):
                st.write(f"**Name:** {info.get('name', 'N/A')}")
                st.write(f"**Location:** {info.get('location', 'N/A')}")
                st.write(f"**Registered:** {info.get('registered_at', 'N/A')}")
                
                if st.button(f"Remove {device_id}", key=f"remove_{device_id}"):
                    del devices[device_id]
                    save_devices(devices)
                    st.success(f"Device {device_id} removed")
                    st.rerun()
    else:
        st.info("No devices registered")
    
    # Add new device
    st.markdown("---")
    st.subheader("Add New Device")
    
    with st.form("add_device"):
        new_device_id = st.text_input("Device ID", placeholder="ESP32_WATER_002")
        new_device_name = st.text_input("Device Name", placeholder="Water Meter 002")
        new_device_location = st.text_input("Location", placeholder="Secondary Building")
        
        submitted = st.form_submit_button("Add Device")
        if submitted:
            if new_device_id and new_device_name:
                devices[new_device_id] = {
                    "name": new_device_name,
                    "location": new_device_location,
                    "registered_at": datetime.datetime.now().isoformat()
                }
                save_devices(devices)
                st.success(f"Device {new_device_id} added successfully!")
                st.rerun()
            else:
                st.error("Device ID and Name are required")

def show_raw_data():
    st.header("📄 Raw Data")
    
    all_data = load_data()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"Total Records: {len(all_data)}")
    
    with col2:
        if st.button("🗑️ Clear All Data"):
            save_data([])
            st.success("All data cleared!")
            st.rerun()
    
    if all_data:
        st.json(all_data[-10:])  # Show last 10 records
        
        # Download button
        df = pd.DataFrame(all_data)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"water_flow_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available")

if __name__ == "__main__":
    main()
