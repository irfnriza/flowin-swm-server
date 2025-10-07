# API Testing dengan cURL & Postman

## 🧪 Testing Endpoints

### 1. Test Verify Endpoint

#### cURL (Windows PowerShell)
```powershell
# Local
Invoke-WebRequest -Uri "http://localhost:8501/verify?device_id=ESP32_WATER_001" -Method GET

# Production
Invoke-WebRequest -Uri "https://your-app.streamlit.app/verify?device_id=ESP32_WATER_001" -Method GET
```

#### cURL (Linux/Mac)
```bash
# Local
curl "http://localhost:8501/verify?device_id=ESP32_WATER_001"

# Production
curl "https://your-app.streamlit.app/verify?device_id=ESP32_WATER_001"
```

#### Expected Response
```json
{
  "status": "verified",
  "device_id": "ESP32_WATER_001",
  "device_info": {
    "name": "Water Meter 001",
    "location": "Main Building",
    "registered_at": "2025-10-07T00:00:00"
  }
}
```

---

### 2. Test Data Endpoint

#### cURL (Windows PowerShell)
```powershell
$body = @'
[
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
'@

# Local
Invoke-WebRequest -Uri "http://localhost:8501/data?device_id=ESP32_WATER_001" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

# Production
Invoke-WebRequest -Uri "https://your-app.streamlit.app/data?device_id=ESP32_WATER_001" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

#### cURL (Linux/Mac)
```bash
# Local
curl -X POST "http://localhost:8501/data?device_id=ESP32_WATER_001" \
  -H "Content-Type: application/json" \
  -d '[
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
  ]'

# Production
curl -X POST "https://your-app.streamlit.app/data?device_id=ESP32_WATER_001" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "timestamp": 123456789,
      "flow_rate": 2.5,
      "volume": 150.2
    }
  ]'
```

#### Expected Response
```json
{
  "status": "success",
  "message": "Received 2 data points",
  "device_id": "ESP32_WATER_001"
}
```

---

## 📮 Postman Collection

### Import ke Postman

1. Buat Collection baru: "Smart Water Meter API"
2. Tambahkan 2 requests:

#### Request 1: Verify Device
```
Name: Verify Device
Method: GET
URL: {{base_url}}/verify?device_id={{device_id}}

Environment Variables:
- base_url: http://localhost:8501 (atau production URL)
- device_id: ESP32_WATER_001
```

#### Request 2: Send Data
```
Name: Send Data
Method: POST
URL: {{base_url}}/data?device_id={{device_id}}
Headers:
- Content-Type: application/json

Body (raw JSON):
[
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
```

---

## 🧪 Python Testing Script

```python
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8501"  # Ganti dengan production URL
DEVICE_ID = "ESP32_WATER_001"

def test_verify():
    """Test verify endpoint"""
    url = f"{BASE_URL}/verify?device_id={DEVICE_ID}"
    
    print(f"Testing: {url}")
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    return response.status_code == 200

def test_send_data():
    """Test data endpoint"""
    url = f"{BASE_URL}/data?device_id={DEVICE_ID}"
    
    # Sample data
    data = [
        {
            "timestamp": int(time.time() * 1000),
            "flow_rate": 2.5,
            "volume": 150.2
        },
        {
            "timestamp": int(time.time() * 1000) + 60000,
            "flow_rate": 2.3,
            "volume": 152.5
        }
    ]
    
    print(f"Testing: {url}")
    print(f"Payload: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        url,
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    return response.status_code == 200

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Smart Water Meter API Tests")
    print("=" * 60)
    print()
    
    # Test 1: Verify
    print("Test 1: Verify Device")
    print("-" * 60)
    verify_ok = test_verify()
    print(f"Result: {'✅ PASSED' if verify_ok else '❌ FAILED'}")
    print()
    
    # Test 2: Send Data
    print("Test 2: Send Data")
    print("-" * 60)
    data_ok = test_send_data()
    print(f"Result: {'✅ PASSED' if data_ok else '❌ FAILED'}")
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Verify Endpoint: {'✅ PASSED' if verify_ok else '❌ FAILED'}")
    print(f"Data Endpoint:   {'✅ PASSED' if data_ok else '❌ FAILED'}")
    print()
    
    if verify_ok and data_ok:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    run_tests()
```

Simpan sebagai `test_api.py` dan jalankan:
```bash
python test_api.py
```

---

## 🔍 Advanced Testing

### Load Testing (Multiple Devices)
```python
import requests
import concurrent.futures

def send_data_for_device(device_id):
    url = f"http://localhost:8501/data?device_id={device_id}"
    data = [{"timestamp": 123456789, "flow_rate": 2.5, "volume": 150.2}]
    response = requests.post(url, json=data)
    return device_id, response.status_code

# Test dengan 10 devices sekaligus
devices = [f"ESP32_WATER_{i:03d}" for i in range(1, 11)]

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(send_data_for_device, devices))

for device_id, status_code in results:
    print(f"{device_id}: {status_code}")
```

### Stress Testing (High Frequency)
```python
import requests
import time

url = "http://localhost:8501/data?device_id=ESP32_WATER_001"

# Kirim 100 requests
for i in range(100):
    data = [{"timestamp": i * 1000, "flow_rate": 2.5, "volume": i * 0.1}]
    response = requests.post(url, json=data)
    print(f"Request {i+1}: {response.status_code}")
    time.sleep(0.1)  # 100ms delay
```

---

## 📊 Response Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200  | ✅ OK | Request successful |
| 400  | ❌ Bad Request | Missing parameters or invalid data |
| 404  | ❌ Not Found | Device not registered |
| 500  | ❌ Server Error | Internal server error |

---

## 🐛 Debugging Tips

### Enable Verbose Output
```bash
# cURL verbose
curl -v "http://localhost:8501/verify?device_id=ESP32_WATER_001"

# PowerShell verbose
Invoke-WebRequest -Uri "http://localhost:8501/verify?device_id=ESP32_WATER_001" -Verbose
```

### Check Response Headers
```python
import requests

response = requests.get("http://localhost:8501/verify?device_id=ESP32_WATER_001")
print("Headers:", response.headers)
print("Status:", response.status_code)
print("Body:", response.text)
```

### Log Network Traffic
```bash
# Windows: Use Fiddler or Wireshark
# Linux/Mac: Use tcpdump
sudo tcpdump -i any port 8501 -w capture.pcap
```

---

## ⚠️ Common Issues

### Issue 1: Connection Refused
```
Error: Connection refused
```
**Solution:** Pastikan server Streamlit running di `http://localhost:8501`

### Issue 2: 404 Not Found
```json
{
  "status": "error",
  "message": "device not registered"
}
```
**Solution:** Register device di tab "Device Management"

### Issue 3: Invalid JSON
```json
{
  "status": "error",
  "message": "data must be a JSON array"
}
```
**Solution:** Pastikan payload adalah array `[...]` bukan object `{...}`

### Issue 4: CORS Error (Browser)
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```
**Solution:** Gunakan Streamlit UI untuk testing, atau deploy Flask API

---

## 📝 Testing Checklist

- [ ] Test verify dengan device terdaftar
- [ ] Test verify dengan device tidak terdaftar
- [ ] Test send data dengan 1 record
- [ ] Test send data dengan multiple records
- [ ] Test send data tanpa device_id parameter
- [ ] Test send data dengan device tidak terdaftar
- [ ] Test send data dengan invalid JSON
- [ ] Test send data dengan empty array
- [ ] Verify data muncul di dashboard
- [ ] Verify data tersimpan di water_flow_data.json

---

**Happy Testing! 🧪**
