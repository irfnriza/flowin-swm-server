"""
ALUR KERJA SISTEM SMART WATER METER V2
========================================

┌─────────────────────────────────────────────────────────────────┐
│                        ESP32 BOOT SEQUENCE                       │
└─────────────────────────────────────────────────────────────────┘

    1. Power On
         ↓
    2. Init Hardware (Sensor, Relay, OLED)
         ↓
    3. Load Hard-coded Config
         ↓
    4. Turn ON Relay (WiFi Module Power)
         ↓
    5. Connect to WiFi
         ↓
    6. Verify Device with Server
         ├─ Success → Continue
         └─ Failed → Restart ESP32
         ↓
    7. Turn OFF WiFi (Save Power)
         ↓
    8. Start Monitoring Loop


┌─────────────────────────────────────────────────────────────────┐
│                      MONITORING LOOP (Main)                      │
└─────────────────────────────────────────────────────────────────┘

    Loop forever:
    
    ┌──────────────────────────────────────┐
    │  Every 1 Second                      │
    │  ├─ Count pulses from flow sensor    │
    │  ├─ Calculate flow rate              │
    │  ├─ Calculate total volume           │
    │  └─ Update OLED display              │
    └──────────────────────────────────────┘
              ↓
    ┌──────────────────────────────────────┐
    │  Every 60 Seconds                    │
    │  ├─ Store data to buffer             │
    │  │   • Timestamp                     │
    │  │   • Flow rate                     │
    │  │   • Total volume                  │
    │  └─ Check buffer size                │
    └──────────────────────────────────────┘
              ↓
    ┌──────────────────────────────────────┐
    │  When Buffer >= 10 samples           │
    │  ├─ Turn ON WiFi                     │
    │  ├─ Connect to WiFi                  │
    │  ├─ Send data to server              │
    │  ├─ Turn OFF WiFi                    │
    │  └─ Clear buffer                     │
    └──────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      DATA TRANSMISSION                           │
└─────────────────────────────────────────────────────────────────┘

    ESP32                                    Streamlit Server
      │                                             │
      │  POST /data?device_id=ESP32_WATER_001      │
      │ ─────────────────────────────────────────> │
      │                                             │
      │  Body:                                      │
      │  [                                          │
      │    {"timestamp": 123, "flow": 2.5, ...}    │
      │    {"timestamp": 183, "flow": 2.3, ...}    │
      │    ... (10 records)                         │
      │  ]                                          │
      │                                             │
      │                                      ┌──────┴──────┐
      │                                      │ 1. Validate │
      │                                      │ 2. Add meta │
      │                                      │ 3. Save     │
      │                                      └──────┬──────┘
      │                                             │
      │  <───────────────────────────────────────── │
      │  Response:                                  │
      │  {                                          │
      │    "status": "success",                     │
      │    "message": "Received 10 data points"     │
      │  }                                          │
      │                                             │


┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD                           │
└─────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────────────────────────────┐
    │                    NAVIGATION                       │
    │  • Dashboard      → View data & charts             │
    │  • API Testing    → Test endpoints                 │
    │  • Device Mgmt    → Manage devices                 │
    │  • Raw Data       → View/download JSON             │
    └────────────────────────────────────────────────────┘
                           ↓
    ┌────────────────────────────────────────────────────┐
    │                    DASHBOARD                        │
    │  ┌──────────────────────────────────────────────┐ │
    │  │  Statistics                                   │ │
    │  │  • Total Records                              │ │
    │  │  • Active Devices                             │ │
    │  │  • Latest Flow Rate                           │ │
    │  └──────────────────────────────────────────────┘ │
    │  ┌──────────────────────────────────────────────┐ │
    │  │  Flow Rate Chart                              │ │
    │  │  [Line chart showing flow over time]          │ │
    │  └──────────────────────────────────────────────┘ │
    │  ┌──────────────────────────────────────────────┐ │
    │  │  Recent Data Table                            │ │
    │  │  Device | Flow | Volume | Time                │ │
    │  └──────────────────────────────────────────────┘ │
    └────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      POWER MANAGEMENT                            │
└─────────────────────────────────────────────────────────────────┘

    WiFi Module controlled by Relay (Pin 23):
    
    Normal Operation (95% of time):
    ┌──────────────────────────────────┐
    │  Relay OFF → WiFi Module OFF     │
    │  • Monitoring flow sensor        │
    │  • Updating OLED display         │
    │  • Buffering data                │
    │  • Power consumption: LOW        │
    └──────────────────────────────────┘
    
    Data Transmission (5% of time):
    ┌──────────────────────────────────┐
    │  Relay ON → WiFi Module ON       │
    │  • Connect to WiFi               │
    │  • Send buffered data            │
    │  • Receive confirmation          │
    │  • Power consumption: HIGH       │
    └──────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      FLOW CALCULATION                            │
└─────────────────────────────────────────────────────────────────┘

    Sensor generates pulses when water flows:
    
    1. Interrupt Handler
       └─ Each pulse → increment counter
    
    2. Every 1 second:
       ├─ flowRate = pulses / CALIBRATION_FACTOR
       │             (pulses per second / 5.5 = L/min)
       │
       ├─ totalVolume += flowRate / 60
       │                 (convert L/min to L)
       │
       └─ pulses = 0  (reset counter)
    
    Example:
    • 55 pulses in 1 second
    • flowRate = 55 / 5.5 = 10 L/min
    • totalVolume += 10 / 60 = 0.167 L added


┌─────────────────────────────────────────────────────────────────┐
│                    DATA BUFFER MANAGEMENT                        │
└─────────────────────────────────────────────────────────────────┘

    Buffer Array (50 slots):
    
    struct Data {
        unsigned long timestamp;  // millis() when recorded
        float flow_rate;          // L/min
        float volume;             // Total L
    }
    
    Data buf[50];
    int idx = 0;  // Current position
    
    Timeline:
    00:00 → Record sample #1  (idx=1)
    01:00 → Record sample #2  (idx=2)
    02:00 → Record sample #3  (idx=3)
    ...
    09:00 → Record sample #10 (idx=10) → SEND TO SERVER
    10:00 → Record sample #1  (idx=1)  → Buffer reset
    
    Safety: Buffer max 50 samples
            If transmission fails, can store up to 50 minutes


┌─────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING                              │
└─────────────────────────────────────────────────────────────────┘

    WiFi Connection Failed:
    • Retry 20 times (10 seconds)
    • Show "WiFi FAIL" on OLED
    • Keep data in buffer
    • Try again next transmission cycle
    
    Verification Failed:
    • Show "Failed!" on OLED
    • Wait 2 seconds
    • Restart ESP32
    
    Data Send Failed:
    • Data remains in buffer
    • Will retry next cycle
    • Buffer can hold 50 samples (50 minutes)


┌─────────────────────────────────────────────────────────────────┐
│                    TYPICAL OPERATION DAY                         │
└─────────────────────────────────────────────────────────────────┘

    00:00 - Boot & Verify
    00:01 - Start monitoring
    00:01-00:59 - Collect 1 sample (WiFi OFF)
    01:00 - Collect 2 samples
    ...
    10:00 - Collect 10 samples → SEND (WiFi ON for ~30 sec)
    10:01 - Continue monitoring (WiFi OFF)
    11:00 - Collect 1 sample
    ...
    20:00 - Collect 10 samples → SEND
    
    Daily stats:
    • Measurements: 1440 (every minute)
    • Transmissions: 144 (every 10 minutes)
    • WiFi ON time: ~72 minutes (5% of day)
    • WiFi OFF time: ~1368 minutes (95% of day)


┌─────────────────────────────────────────────────────────────────┐
│                      CONFIGURATION                               │
└─────────────────────────────────────────────────────────────────┘

    Hard-coded in ESP32 code:
    
    const String DEVICE_ID = "ESP32_WATER_001";
    └─ Unique identifier untuk device
       Harus match dengan yang terdaftar di server
    
    const char* WIFI_SSID = "YourWiFi";
    └─ Nama WiFi network
       Harus WiFi 2.4GHz (ESP32 tidak support 5GHz)
    
    const char* WIFI_PASS = "password";
    └─ Password WiFi
    
    const String SERVER_URL = "https://your-app.streamlit.app";
    └─ URL server Streamlit
       Tanpa trailing slash
       Bisa http (local) atau https (production)


┌─────────────────────────────────────────────────────────────────┐
│                    CALIBRATION FACTOR                            │
└─────────────────────────────────────────────────────────────────┘

    const float CAL_FACTOR = 5.5;
    
    Artinya: 5.5 pulsa per detik = 1 L/min
    
    Untuk kalibrasi ulang:
    1. Ukur air dengan volume terukur (contoh: 10L)
    2. Hitung total pulsa saat mengalir
    3. CAL_FACTOR = total_pulsa / (volume_liter * 60)
    
    Contoh kalibrasi:
    • 10 L air mengalir dalam 60 detik
    • Total pulsa = 3300
    • CAL_FACTOR = 3300 / (10 * 60) = 5.5


┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT CHECKLIST                          │
└─────────────────────────────────────────────────────────────────┘

    ☐ Hardware Setup
      ├─ ESP32 connected
      ├─ Flow sensor wired to pin 34
      ├─ Relay wired to pin 23
      ├─ OLED display I2C connected
      └─ Power supply adequate
    
    ☐ ESP32 Code
      ├─ Update DEVICE_ID
      ├─ Update WIFI_SSID
      ├─ Update WIFI_PASS
      ├─ Update SERVER_URL
      ├─ Verify CAL_FACTOR
      └─ Upload to ESP32
    
    ☐ Server Setup
      ├─ Deploy to Streamlit Cloud
      ├─ Register device ID
      ├─ Test /verify endpoint
      ├─ Test /data endpoint
      └─ Monitor dashboard
    
    ☐ Testing
      ├─ WiFi connection works
      ├─ Device verification successful
      ├─ Flow sensor reading correctly
      ├─ OLED displaying data
      ├─ Data transmitting to server
      └─ Dashboard updating
    
    ☐ Monitoring
      ├─ Check Serial Monitor regularly
      ├─ Monitor dashboard for gaps
      ├─ Verify data accuracy
      └─ Check battery/power consumption

═══════════════════════════════════════════════════════════════════

                    SISTEM SIAP BEROPERASI! ✅

═══════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
