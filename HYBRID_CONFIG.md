# 📝 UPDATE: Hybrid Configuration Mode

## 🔄 Perubahan Terbaru

Sistem sekarang menggunakan **Hybrid Configuration**:

### ✅ Yang Hard-coded (di ESP32 Code):
- **WiFi SSID** - Nama WiFi
- **WiFi Password** - Password WiFi
- **Server URL** - URL server Streamlit/Flask

### 📱 Yang Dikonfigurasi via Bluetooth:
- **Device ID** - ID unik untuk setiap device

### 📦 Format Data yang Dikirim:
- **Device ID di Query Parameter**: `?device_id=XXX`
- **Data di JSON Body** dengan wrapper: 
```json
{
  "device_id": "ESP32_WATER_001",
  "data": [
    {"timestamp": 123, "flow_rate": 2.5, "volume": 150.2}
  ]
}
```

---

## 🚀 Cara Setup

### 1️⃣ Edit Kode ESP32

Buka `esp32-kode/smartwatermeterv2.cpp`, ubah baris 22-24:

```cpp
// Hard-coded Configuration (WiFi & Server)
const char* WIFI_SSID = "NamaWiFiAnda";           // GANTI INI
const char* WIFI_PASS = "PasswordWiFiAnda";        // GANTI INI
const String SERVER_URL = "http://192.168.1.100:8501"; // GANTI INI
```

### 2️⃣ Upload ke ESP32

```
Arduino IDE → Upload
```

### 3️⃣ Konfigurasi Device ID via Bluetooth

#### Pertama kali boot:
```
Serial Monitor akan show:
"Entering Bluetooth config mode"
"Bluetooth started: ESP32_WaterMeter"
"Send: ID:your_device_id"
```

#### Pair dengan Smartphone:
1. Buka Bluetooth di smartphone
2. Scan dan pair dengan "ESP32_WaterMeter"
3. Gunakan app Bluetooth Terminal (contoh: Serial Bluetooth Terminal)
4. Kirim: `ID:ESP32_WATER_001` (ganti dengan ID Anda)
5. Device akan respond: "Device ID set: ESP32_WATER_001"
6. Device ID tersimpan permanent di ESP32

#### Next boot:
- Device ID otomatis loaded dari memory
- Tidak perlu konfigurasi Bluetooth lagi
- Langsung connect WiFi dan verify

---

## 📡 API Endpoints

### Verify Device

**Request 1: GET with Query Parameter**
```http
GET /verify?device_id=ESP32_WATER_001
```

**Request 2: POST with JSON Body**
```http
POST /verify?device_id=ESP32_WATER_001
Content-Type: application/json

{
  "device_id": "ESP32_WATER_001"
}
```

**Response:**
```json
{
  "status": "verified",
  "device_id": "ESP32_WATER_001",
  "device_info": {
    "name": "Water Meter 001",
    "location": "Main Building"
  }
}
```

### Send Data

**Request:**
```http
POST /data?device_id=ESP32_WATER_001
Content-Type: application/json

{
  "device_id": "ESP32_WATER_001",
  "data": [
    {
      "timestamp": 123456789,
      "flow_rate": 2.5,
      "volume": 150.2
    },
    {
      "timestamp": 123456849,
      "flow_rate": 2.3,
      "volume": 152.5
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Received 2 data points",
  "device_id": "ESP32_WATER_001"
}
```

---

## 🔧 Mengganti Device ID

### Via Bluetooth:
1. Connect via Bluetooth Terminal
2. Kirim: `ID:NEW_DEVICE_ID`
3. Device akan save dan restart

### Via Code (jika mau reset):
```cpp
// Tambahkan di setup() sebelum loadDeviceID()
prefs.begin("config", false);
prefs.clear();  // Clear all saved config
prefs.end();
// Upload ulang, akan masuk config mode lagi
```

---

## 📱 Multiple Devices Setup

### Device 1:
```
1. Upload code (sama untuk semua device)
2. Bluetooth config: ID:ESP32_WATER_001
3. Register di server dengan ID: ESP32_WATER_001
```

### Device 2:
```
1. Upload code (sama dengan Device 1)
2. Bluetooth config: ID:ESP32_WATER_002
3. Register di server dengan ID: ESP32_WATER_002
```

### Device 3:
```
1. Upload code (sama dengan Device 1 & 2)
2. Bluetooth config: ID:ESP32_WATER_003
3. Register di server dengan ID: ESP32_WATER_003
```

Semua device menggunakan:
- WiFi yang sama
- Server URL yang sama
- Code yang sama
- Hanya Device ID yang berbeda

---

## 🎯 Keuntungan Hybrid Mode

### ✅ Pros:
1. **Easy Deployment**: WiFi credentials hard-coded, tidak perlu config per-device
2. **Flexible Device ID**: Setiap device bisa punya ID unik via Bluetooth
3. **Permanent Storage**: Device ID tersimpan di ESP32 memory
4. **No Reconfiguration**: Setelah setup awal, tidak perlu config lagi
5. **Easy Scaling**: Tambah device baru tinggal pair Bluetooth dan set ID

### 📊 Comparison:

| Feature | Full Hard-coded | Full Bluetooth | Hybrid (Current) |
|---------|----------------|----------------|------------------|
| WiFi Config | ✅ Easy | ⏱️ Slow | ✅ Easy |
| Device ID | ❌ Sama semua | ✅ Unique | ✅ Unique |
| Deployment | ⚡ Fast | 🐌 Slow | ⚡ Fast |
| Flexibility | ❌ Low | ✅ High | ✅ High |
| Scaling | ❌ Hard | ⏱️ Medium | ✅ Easy |

---

## 🧪 Testing

### Test 1: First Boot (No Device ID)
```
Expected:
1. OLED: "Config Mode"
2. OLED: "BT: Pairing..."
3. Serial: "Bluetooth started: ESP32_WaterMeter"
4. Pair dari smartphone
5. Send: ID:TEST_DEVICE_001
6. OLED: "ID Saved!"
7. Device restart dan connect WiFi
```

### Test 2: Next Boot (Device ID Saved)
```
Expected:
1. OLED: "Starting..."
2. Serial: "Device ID: TEST_DEVICE_001"
3. OLED: "Connecting..."
4. OLED: "Verified!"
5. Start monitoring
```

### Test 3: Data Transmission
```
Expected:
Serial Monitor:
Sending to: https://your-app.streamlit.app/data?device_id=TEST_DEVICE_001
Payload: {"device_id":"TEST_DEVICE_001","data":[{...}]}
Response code: 200
Sent OK
```

---

## 🔐 Security Notes

### Current Implementation:
- ⚠️ WiFi credentials in plain text in code
- ⚠️ No encryption on Bluetooth pairing
- ⚠️ No authentication on API endpoints

### For Production (Recommended):
1. **Encrypt WiFi credentials** in code
2. **Add Bluetooth PIN** for pairing
3. **Add API Key authentication** untuk endpoints
4. **Use HTTPS** untuk server
5. **Add device certificate** untuk mutual TLS

---

## 📞 Troubleshooting

### Problem: Bluetooth tidak muncul
```
Solution:
- Pastikan ESP32 masuk config mode (belum ada Device ID)
- Restart ESP32
- Check Serial Monitor untuk "Bluetooth started"
```

### Problem: Device ID tidak tersimpan
```
Solution:
- Kirim command dengan format exact: ID:your_id
- Tanpa spasi sebelum/sesudah
- Pastikan ada newline di akhir (Enter)
```

### Problem: Ingin ganti Device ID
```
Solution 1 (via Bluetooth):
- Connect Bluetooth
- Kirim: ID:NEW_DEVICE_ID
- Device akan save dan bisa langsung pakai

Solution 2 (via code):
- Uncomment code untuk clear preferences
- Upload ulang
- Device akan masuk config mode
```

### Problem: Verify failed
```
Solution:
- Pastikan Device ID sudah registered di server
- Cek tab "Device Management" di dashboard
- Add device dengan ID yang sama
```

---

## 🎓 Best Practices

### 1. Naming Convention
```
Format: ESP32_LOCATION_NUMBER
Examples:
- ESP32_BUILDING_A_001
- ESP32_FLOOR_2_ROOM_301
- ESP32_WAREHOUSE_NORTH_01
```

### 2. Documentation
```
Buat spreadsheet:
| Device ID | Location | Installed Date | MAC Address |
|-----------|----------|----------------|-------------|
| ESP32_... | Room 101 | 2025-10-07     | AA:BB:CC:.. |
```

### 3. Testing Checklist per Device
```
- [ ] WiFi credentials correct
- [ ] Server URL correct
- [ ] Bluetooth pairing successful
- [ ] Device ID set and saved
- [ ] Device registered in server
- [ ] Verify endpoint returns 200
- [ ] Data transmission successful
- [ ] Dashboard showing data
```

---

## 🚀 Next Steps

1. Setup WiFi credentials di code
2. Deploy server ke Streamlit Cloud
3. Update SERVER_URL di code
4. Upload ke semua ESP32
5. Pair Bluetooth dan set Device ID untuk setiap device
6. Register semua device di server
7. Test dan monitor

---

**Updated:** October 7, 2025  
**Version:** 2.1 (Hybrid Configuration Mode)
