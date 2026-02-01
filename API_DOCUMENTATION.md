# API Endpoints untuk Data Management

## Endpoint yang Tersedia

### 1. Get Data Statistics
**GET** `/api/data/stats`

Mendapatkan statistik data energi dan GDP (jumlah records dan waktu update terakhir).

**Response:**
```json
{
  "energyCount": 50,
  "gdpCount": 45,
  "lastUpdate": "22 Jan 2026 14:30"
}
```

---

### 2. Fetch Data dari API
**POST** `/api/data/fetch`

Mengambil data dari API eksternal (OWID Energy & World Bank GDP).

**Request Body:**
```json
{
  "dataType": "all",  // "all", "energy", atau "gdp"
  "startYear": 1990,
  "endYear": 2023
}
```

**Response:**
```json
{
  "success": true,
  "energyCount": 34,
  "gdpCount": 34,
  "message": "Data berhasil diambil dari API"
}
```

---

### 3. Upload File Data
**POST** `/api/data/upload`

Upload file CSV atau Excel untuk data energi dan/atau GDP.

**Request:** multipart/form-data
- `energyFile`: File CSV/Excel untuk data energi (optional)
- `gdpFile`: File CSV/Excel untuk data GDP (optional)

**Format File:**
- **Energy:** harus memiliki kolom `year` dan `value`
- **GDP:** harus memiliki kolom `year` dan `gdp`

**Response:**
```json
{
  "success": true,
  "energyCount": 30,
  "gdpCount": 30,
  "message": "File berhasil diupload"
}
```

---

### 4. Get Energy Data Preview
**GET** `/api/data/energy?limit=10`

Mendapatkan preview data energi terbaru.

**Query Parameters:**
- `limit`: Jumlah data yang ditampilkan (default: 10)

**Response:**
```json
[
  {
    "year": 2023,
    "country": "Indonesia",
    "value": 85.5,
    "updated": "22 Jan 2026"
  }
]
```

---

### 5. Get GDP Data Preview
**GET** `/api/data/gdp?limit=10`

Mendapatkan preview data GDP terbaru.

**Query Parameters:**
- `limit`: Jumlah data yang ditampilkan (default: 10)

**Response:**
```json
[
  {
    "year": 2023,
    "country": "Indonesia",
    "value": 1319100271351.89,
    "updated": "22 Jan 2026"
  }
]
```

---

### 6. Monitor Progress
**GET** `/api/data/progress/{task_id}`

Monitor progress untuk operasi data (saat ini return completed status, bisa dikembangkan dengan Celery).

**Response:**
```json
{
  "status": "completed",
  "progress": 100,
  "log": "Proses selesai"
}
```

---

### 7. Save Schedule
**POST** `/api/data/schedule`

Menyimpan jadwal scraping otomatis (placeholder untuk future implementation).

**Request Body:**
```json
{
  "enabled": true,
  "frequency": "monthly",
  "time": "02:00",
  "timezone": "Asia/Jakarta"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Jadwal berhasil disimpan",
  "schedule": { ... }
}
```

---

## Cara Menggunakan

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Jalankan Aplikasi
```bash
python app.py
```

### Akses Frontend
Buka browser dan akses:
```
http://localhost:5000/admin/scraping-data
```

---

## Fitur Frontend

1. **Fetch dari API**
   - Pilih jenis data (Semua/Energi/GDP)
   - Tentukan rentang tahun
   - Klik "Fetch Data Sekarang"

2. **Upload File**
   - Pilih file CSV atau Excel
   - Upload untuk data energi dan/atau GDP
   - Klik "Upload Files"

3. **Preview Data**
   - Lihat data energi dan GDP terbaru
   - Refresh preview setelah update
   - Data ditampilkan dalam tabel yang rapi

4. **Schedule Otomatis**
   - Aktifkan jadwal scraping otomatis
   - Pilih frekuensi dan waktu eksekusi
   - (Feature akan dikembangkan lebih lanjut)

---

## Error Handling

Semua endpoint mengembalikan error dalam format:
```json
{
  "success": false,
  "message": "Deskripsi error"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad Request (input tidak valid)
- 500: Internal Server Error
