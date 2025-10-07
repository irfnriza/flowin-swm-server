# Smart Water Meter - Streamlit Server

Server monitoring untuk Smart Water Meter berbasis ESP32 yang dapat di-deploy ke Streamlit Cloud.

## 🚀 Fitur

- ✅ API endpoint untuk verifikasi device (`/verify`)
- ✅ API endpoint untuk menerima data (`/data`)
- 📊 Dashboard real-time untuk monitoring
- 🔧 Device management
- 📈 Visualisasi data flow rate
- 💾 Export data ke CSV

## 📦 Deployment ke Streamlit Cloud

### 1. Persiapan

1. Push folder `production_server` ke GitHub repository Anda
2. Pastikan file `requirements.txt` sudah ada
3. Login ke [Streamlit Cloud](https://streamlit.io/cloud)

### 2. Deploy

1. Klik "New app" di Streamlit Cloud
2. Pilih repository GitHub Anda
3. Set main file path: `production_server/streamlit_app.py`
4. Klik "Deploy"
5. Tunggu beberapa menit hingga deployment selesai

### 3. Konfigurasi ESP32

Setelah deployment berhasil, Anda akan mendapatkan URL seperti:
```
https://your-username-water-meter.streamlit.app
```

Update kode ESP32 Anda:

```cpp
const String SERVER_URL = "https://your-username-water-meter.streamlit.app";
const char* WIFI_SSID = "NamaWiFiAnda";
const char* WIFI_PASS = "PasswordWiFiAnda";
```

## 🔌 API Endpoints

### Verify Device
```
GET /verify?device_id=ESP32_WATER_001
```

Response:
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
```
POST /data?device_id=ESP32_WATER_001
Content-Type: application/json

[
  {
    "timestamp": 123456789,
    "flow_rate": 2.5,
    "volume": 150.2
  }
]
```

Response:
```json
{
  "status": "success",
  "message": "Received 1 data points",
  "device_id": "ESP32_WATER_001"
}
```

## 🧪 Testing Lokal

Untuk test di komputer lokal sebelum deploy:

```bash
cd production_server
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Aplikasi akan berjalan di `http://localhost:8501`

## 📱 Menambah Device Baru

1. Buka halaman "Device Management" di dashboard
2. Isi Device ID (contoh: `ESP32_WATER_002`)
3. Isi nama dan lokasi device
4. Klik "Add Device"
5. Update Device ID di kode ESP32

## ⚠️ Catatan Penting

### Limitasi Streamlit untuk API

Streamlit **tidak didesain sebagai REST API server**. Aplikasi ini menggunakan workaround untuk simulasi API:

- `/verify` endpoint: menggunakan `st.query_params`
- `/data` endpoint: menggunakan kombinasi query params dan session state

### Alternatif untuk Production

Untuk production yang serius, pertimbangkan menggunakan:

1. **FastAPI + Streamlit** (recommended):
   - FastAPI untuk API endpoints
   - Streamlit untuk dashboard
   - Deploy keduanya terpisah

2. **Flask + Streamlit**:
   - Flask untuk API
   - Streamlit untuk monitoring

3. **Cloud Platform**:
   - AWS Lambda + API Gateway
   - Google Cloud Functions
   - Azure Functions

## 🔧 Troubleshooting

### ESP32 tidak bisa connect ke server

1. Pastikan URL server benar (tanpa trailing slash)
2. Cek WiFi credentials
3. Cek serial monitor untuk error messages
4. Pastikan device sudah terdaftar di server

### Data tidak muncul di dashboard

1. Cek di halaman "Raw Data"
2. Pastikan Device ID match dengan yang terdaftar
3. Test API di halaman "API Testing"

## 📊 Data Storage

Data disimpan dalam file JSON lokal:
- `water_flow_data.json`: Data pengukuran
- `registered_devices.json`: Daftar device terdaftar

⚠️ **Warning**: Data akan hilang jika app di-restart di Streamlit Cloud. Untuk persistent storage, gunakan database external (PostgreSQL, MongoDB, etc).

## 🎯 Next Steps

Untuk meningkatkan sistem:

1. Tambahkan authentication/API key
2. Gunakan database external (PostgreSQL/MongoDB)
3. Tambahkan alerting untuk anomali
4. Implementasi data retention policy
5. Tambahkan real-time notifications
6. Buat mobile app

## 📞 Support

Jika ada pertanyaan atau issue, silakan buat issue di GitHub repository.

---

Made with ❤️ for Smart Water Monitoring
