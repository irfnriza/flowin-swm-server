"""
Panduan Testing ESP32 Smart Water Meter
========================================

Sebelum deploy ke Streamlit Cloud, test dulu di local.
"""

# 1. INSTALL DEPENDENCIES
print("Step 1: Install dependencies")
print("pip install -r requirements.txt")
print()

# 2. RUN STREAMLIT APP
print("Step 2: Run Streamlit app")
print("streamlit run streamlit_app.py")
print()

# 3. TEST API ENDPOINTS
print("Step 3: Test API endpoints")
print()

# Test Verify
print("Test Verify (di browser atau Postman):")
print("GET http://localhost:8501/?device_id=ESP32_WATER_001")
print()

# Test Data
print("Test Data (gunakan halaman 'API Testing' di Streamlit UI)")
print()

# 4. KONFIGURASI ESP32
print("Step 4: Konfigurasi ESP32")
print("""
Update file smartwatermeterv2.cpp:

const String DEVICE_ID = "ESP32_WATER_001";
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";

// Untuk testing lokal
const String SERVER_URL = "http://YOUR_COMPUTER_IP:8501";

// Untuk production (setelah deploy ke Streamlit)
const String SERVER_URL = "https://your-app.streamlit.app";
""")
print()

# 5. UPLOAD KE ESP32
print("Step 5: Upload ke ESP32")
print("1. Buka Arduino IDE atau PlatformIO")
print("2. Select board: ESP32 Dev Module")
print("3. Select port: COM port ESP32 Anda")
print("4. Upload code")
print()

# 6. MONITOR SERIAL
print("Step 6: Monitor Serial Output")
print("Buka Serial Monitor (115200 baud)")
print("Anda akan melihat:")
print("- Device ID: ESP32_WATER_001")
print("- WiFi connecting...")
print("- WiFi OK")
print("- Verify response code: 200")
print("- Verified!")
print()

# 7. CEK DASHBOARD
print("Step 7: Cek Dashboard")
print("Buka http://localhost:8501")
print("Lihat data yang masuk di tab 'Dashboard'")
print()

# 8. TROUBLESHOOTING
print("TROUBLESHOOTING:")
print()
print("Problem: ESP32 tidak bisa connect WiFi")
print("Solution: Cek SSID dan password, pastikan WiFi 2.4GHz")
print()
print("Problem: Verify failed")
print("Solution: Pastikan device sudah terdaftar di registered_devices.json")
print()
print("Problem: Data tidak muncul")
print("Solution: Cek Serial Monitor, lihat response code. Harus 200.")
print()

# 9. DEPLOYMENT KE STREAMLIT CLOUD
print("DEPLOYMENT KE STREAMLIT CLOUD:")
print()
print("1. Push ke GitHub:")
print("   git add .")
print("   git commit -m 'Add water meter server'")
print("   git push origin main")
print()
print("2. Login ke https://streamlit.io/cloud")
print()
print("3. Klik 'New app'")
print()
print("4. Pilih repository dan branch")
print()
print("5. Set main file: production_server/streamlit_app.py")
print()
print("6. Klik 'Deploy'")
print()
print("7. Tunggu 2-3 menit")
print()
print("8. Copy URL aplikasi Anda")
print()
print("9. Update ESP32 code dengan URL production")
print()
print("10. Re-upload ke ESP32")
print()

print("=" * 60)
print("SELAMAT! Setup selesai.")
print("=" * 60)
