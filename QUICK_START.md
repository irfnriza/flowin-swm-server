# 🚀 QUICK START GUIDE - Smart Water Meter

## ⚡ Setup Cepat (6 Langkah)

### 1️⃣ Edit Kode ESP32
Buka `esp32-kode/smartwatermeterv2.cpp` dan ubah baris 22-24:

```cpp
const char* WIFI_SSID = "NamaWiFiAnda";               // Ganti dengan WiFi Anda
const char* WIFI_PASS = "PasswordWiFiAnda";           // Ganti dengan password WiFi
const String SERVER_URL = "http://192.168.1.100:8501"; // IP komputer Anda
```

### 2️⃣ Upload ke ESP32
```
Arduino IDE → Tools → Board → ESP32 Dev Module
Arduino IDE → Tools → Port → [Pilih COM port ESP32]
Arduino IDE → Upload
```

### 3️⃣ Konfigurasi Device ID via Bluetooth
```
1. Buka Serial Monitor (115200 baud)
2. ESP32 akan show: "Bluetooth started: ESP32_WaterMeter"
3. Pair dengan smartphone (scan: ESP32_WaterMeter)
4. Gunakan app Bluetooth Terminal
5. Kirim: ID:ESP32_WATER_001
6. ESP32 respond: "Device ID set: ESP32_WATER_001"
7. Device ID tersimpan permanent
```

### 4️⃣ Jalankan Server
```bash
cd production_server
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### 5️⃣ Test API
Buka browser: `http://localhost:8501`
- Klik tab "API Testing"
- Test verify endpoint
- Test data endpoint dengan sample data

### 6️⃣ Monitor Data
- Buka tab "Dashboard"
- Lihat data real-time dari ESP32
- Flow rate akan update setiap 10 menit

---

## 🔄 Format Komunikasi

### Verify Endpoint
```http
POST /verify?device_id=ESP32_WATER_001
Content-Type: application/json

{
  "device_id": "ESP32_WATER_001"
}
```

### Data Endpoint
```http
POST /data?device_id=ESP32_WATER_001
Content-Type: application/json

{
  "device_id": "ESP32_WATER_001",
  "data": [
    {"timestamp": 123456789, "flow_rate": 2.5, "volume": 150.2},
    {"timestamp": 123456849, "flow_rate": 2.3, "volume": 152.5}
  ]
}
```

---

## 🌐 Deploy ke Production

### A. Deploy Server ke Streamlit Cloud

1. **Push ke GitHub**
```bash
git add production_server/
git commit -m "Add water meter server"
git push origin main
```

2. **Deploy**
- Login: https://streamlit.io/cloud
- Klik: "New app"
- Repository: Pilih repo Anda
- Main file: `production_server/streamlit_app.py`
- Klik: "Deploy"

3. **Copy URL**
URL Anda akan seperti: `https://username-watermeter.streamlit.app`

### B. Update ESP32 untuk Production

1. **Edit kode ESP32**
```cpp
const String SERVER_URL = "https://username-watermeter.streamlit.app";
```

2. **Upload ulang ke ESP32**

3. **Monitor Serial** (115200 baud)
```
Device ID: ESP32_WATER_001
Server: https://username-watermeter.streamlit.app
WiFi connecting...
WiFi OK
IP: 192.168.1.123
Verify response code: 200
Verified!
```

4. **Cek Dashboard**
Buka URL Streamlit Anda, data akan mulai masuk dalam 10 menit

---

## 🔧 Troubleshooting Cepat

### ❌ WiFi tidak connect
```cpp
// Pastikan WiFi 2.4GHz (bukan 5GHz)
// Cek SSID dan password
// Cek serial monitor untuk error
```

### ❌ Verify failed
```bash
# Register device di server
# Buka tab "Device Management"
# Add device dengan ID yang sama
```

### ❌ Data tidak muncul
```cpp
// Tunggu 10 menit (buffer 10 samples)
// Cek Serial Monitor untuk response code
// Harus: "Response code: 200"
// Jika 404: Device tidak terdaftar
```

### ❌ Streamlit tidak bisa deploy
```bash
# Pastikan file ada:
# - streamlit_app.py
# - requirements.txt
# - registered_devices.json
# - water_flow_data.json

# Cek logs di Streamlit Cloud
```

---

## 📱 Cara Kerja Sistem

```
ESP32 Monitoring → Setiap detik hitung flow rate
                ↓
     Simpan ke buffer → Setiap 60 detik
                ↓
     Buffer penuh (10 samples) → Setiap 10 menit
                ↓
     Nyalakan WiFi → Kirim data → Matikan WiFi
                ↓
          Dashboard Update
```

---

## 📊 Yang Akan Anda Lihat

### Di Serial Monitor (ESP32):
```
Device ID: ESP32_WATER_001
WiFi connecting...
WiFi OK
IP: 192.168.1.123
Verify response code: 200
Verified!
...
Sending to: https://your-app.streamlit.app/data?device_id=ESP32_WATER_001
Response code: 200
Sent OK
```

### Di OLED Display:
```
Water Flow
----------
Flow: 2.5 L/m
Vol: 150.2 L
Buf: 3
```

### Di Dashboard:
- Total Records: 30
- Active Devices: 1
- Latest Flow Rate: 2.5 L/min
- Chart showing flow over time
- Table with recent data

---

## 🎯 Tips & Trik

### Hemat Baterai
- WiFi OFF 95% waktu
- Hanya ON saat kirim data (30 detik setiap 10 menit)
- Gunakan deep sleep jika perlu

### Kalibrasi Sensor
```cpp
// Default: CAL_FACTOR = 5.5
// Untuk kalibrasi:
// 1. Ukur 10L air dengan gelas ukur
// 2. Hitung total pulsa dari serial monitor
// 3. CAL_FACTOR = pulsa / (10 * 60)
```

### Multiple Devices
```cpp
// Device 1:
const String DEVICE_ID = "ESP32_WATER_001";

// Device 2:
const String DEVICE_ID = "ESP32_WATER_002";

// Register keduanya di server
```

### Backup Data
```
Dashboard → Raw Data → Download as CSV
```

---

## 📞 Need Help?

1. Cek `testing_guide.py` untuk panduan testing
2. Cek `FLOW_DIAGRAM.py` untuk alur sistem
3. Cek `CHANGES.md` untuk dokumentasi lengkap
4. Cek `README.md` untuk detail API

---

## ✅ Checklist Deployment

Sebelum deploy, pastikan:

**Hardware:**
- [ ] ESP32 connected
- [ ] Flow sensor working
- [ ] OLED display showing data
- [ ] Relay controlling power
- [ ] Power supply stable

**Software:**
- [ ] Code uploaded successfully
- [ ] Serial monitor shows "Verified!"
- [ ] WiFi connecting properly
- [ ] Data transmitting (code 200)

**Server:**
- [ ] Streamlit deployed
- [ ] Device registered
- [ ] Dashboard accessible
- [ ] Data receiving properly

**Testing:**
- [ ] Local test passed
- [ ] Production test passed
- [ ] Data accuracy verified
- [ ] Power consumption acceptable

---

## 🎉 Selamat!

Sistem Smart Water Meter Anda siap beroperasi!

Monitoring air Anda sekarang:
- ✅ Real-time
- ✅ Online
- ✅ Efficient
- ✅ Reliable

**Next:** Tambahkan alert, analytics, dan automation! 🚀

---

Last updated: October 7, 2025
Version: 2.0
