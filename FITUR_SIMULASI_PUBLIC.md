# Fitur Simulasi Public Landing Page

## Konsep
Landing page menampilkan dua jenis prediksi:
1. **Prediksi Official** - Dibuat oleh admin, disimpan di database, menggunakan skenario GDP Moderat
2. **Simulasi User** - Dibuat oleh pengunjung public, TIDAK disimpan di database, hanya untuk visualisasi

## Flow

### 1. Load Prediksi Official (Default)
```javascript
// Chart menampilkan:
- Data historis (1990-2023) dari database
- Prediksi official (2024-2030) dengan skenario Moderat dari admin
```

**Indikator:** 
- Header chart: "Prediksi Official: Skenario GDP Moderat"
- Garis prediksi: Hijau solid dengan label "Prediksi Official (Moderat)"

### 2. User Menjalankan Simulasi
```javascript
// User memilih:
- Skenario GDP: Optimis / Moderat / Pesimistis
- Tahun target: 2025-2030

// Sistem:
1. Kirim POST request ke /api/predict dengan:
   {
     scenario: "optimis",
     years: 7,
     save_to_database: false  // PENTING!
   }

2. API menjalankan model ARIMAX dan return predictions

3. Chart diupdate dengan hasil simulasi (warna kuning)

4. Button "Reset ke Prediksi Official" muncul
```

**Indikator:**
- Garis prediksi: Kuning dashed dengan label "Simulasi (Optimis)"
- Button reset visible
- Warning: "Hasil simulasi hanya untuk visualisasi, tidak disimpan ke database"

### 3. User Reset ke Prediksi Official
```javascript
// User klik "Reset ke Prediksi Official"

// Sistem:
1. Chart dikembalikan ke prediksi official (hijau)
2. Button reset hidden
3. Form reset ke default
```

## API Endpoint

### POST /api/predict
```json
{
  "scenario": "optimis|moderat|pesimistis",
  "years": 1-10,
  "save_to_database": true|false  // Default: true
}
```

**Response:**
```json
{
  "status": "success",
  "scenario": "optimis",
  "years": 7,
  "predictions": [2850.23, 2920.45, ...],
  "lower_bounds": [2800.12, 2870.33, ...],
  "upper_bounds": [2900.34, 2970.56, ...],
  "saved_to_database": false
}
```

## Database Schema

### Prediksi Official (Disimpan)
- Table: `prediction_history`
- Dibuat oleh: Admin melalui dashboard
- Scenario: Default "moderat"
- Ditampilkan di: Landing page (default)

### Simulasi User (TIDAK Disimpan)
- Hanya di-render di frontend
- Tidak masuk ke database
- Hilang setelah refresh/reset

## UI/UX

### Landing Page Sections
1. **Chart Section**
   - Default: Prediksi Official (Moderat)
   - Info badge: "Prediksi Official: Skenario GDP Moderat"
   
2. **Simulasi Section**
   - Form: Skenario + Tahun
   - Warning: "Hasil simulasi hanya untuk visualisasi, tidak disimpan"
   - Button: "Jalankan Simulasi"
   - Button Reset (hidden by default)

3. **Hasil Simulasi**
   - Card nilai prediksi (TWh)
   - Card perubahan dari 2023 (%)
   - Info detail skenario

## Security & Performance

1. **Rate Limiting** (Recommended)
   - Batasi request simulasi per IP
   - Prevent API abuse

2. **Caching**
   - Cache prediksi official di frontend
   - Avoid repeated DB queries

3. **Validation**
   - Validate scenario value
   - Validate year range (2025-2030)
   - Validate save_to_database param di backend

## Testing

### Test Case 1: Load Default
```
1. Buka landing page
2. Verify chart tampil prediksi official (hijau)
3. Verify badge "Prediksi Official: Skenario GDP Moderat"
4. Verify button reset hidden
```

### Test Case 2: Run Simulation
```
1. Pilih skenario "Optimis"
2. Pilih tahun "2030"
3. Klik "Jalankan Simulasi"
4. Verify chart update (kuning)
5. Verify hasil simulasi tampil
6. Verify button reset visible
7. Verify database tidak bertambah record
```

### Test Case 3: Reset
```
1. Setelah simulasi
2. Klik "Reset ke Prediksi Official"
3. Verify chart kembali ke prediksi official (hijau)
4. Verify button reset hidden
5. Verify form reset
```

## Files Modified

1. `templates/index.html`
   - Tambah info badge prediksi official
   - Tambah warning simulasi
   - Tambah button reset

2. `static/assets/js/main.js`
   - Function loadOfficialPrediction()
   - Function updateChartWithSimulation()
   - Event handler reset button

3. `routes/api.py`
   - Update /api/predict endpoint
   - Support parameter save_to_database

## Notes

- Prediksi official dibuat oleh admin, scenario moderat adalah default
- User bisa coba skenario berbeda tanpa affect database
- Setelah refresh page, simulasi hilang, kembali ke prediksi official
