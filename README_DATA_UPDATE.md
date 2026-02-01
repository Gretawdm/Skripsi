# 📊 Sistem Update Data - Panduan Penggunaan

## ✨ Fitur yang Sudah Ditambahkan

### 1. **Fetch Data dari API** 🌐
Fungsi untuk mengambil data langsung dari sumber eksternal:
- **OWID Energy Data** - Data konsumsi energi fosil
- **World Bank GDP Data** - Data GDP Indonesia

**Fitur:**
- ✅ Filter berdasarkan jenis data (Semua/Energi/GDP)
- ✅ Filter berdasarkan rentang tahun
- ✅ Progress monitoring real-time
- ✅ Auto-save ke file CSV

### 2. **Upload File Manual** 📁
Fungsi untuk upload data dari file lokal:
- ✅ Support format CSV dan Excel (.xlsx, .xls)
- ✅ Validasi format file otomatis
- ✅ Upload terpisah untuk data energi dan GDP
- ✅ Preview data setelah upload

---

## 🚀 Cara Menggunakan

### A. Fetch Data dari API

1. Buka halaman: `http://localhost:5000/admin/scraping-data`
2. Klik **"Fetch dari API"**
3. Pilih jenis data yang ingin diambil:
   - **Semua Data** - Energi + GDP
   - **Data Energi Saja**
   - **Data GDP Saja**
4. Tentukan rentang tahun (misal: 1990 - 2023)
5. Klik **"Fetch Data Sekarang"**
6. Tunggu proses selesai (ada progress bar)
7. Data otomatis tersimpan di folder `data/raw/`

### B. Upload File Manual

1. Buka halaman: `http://localhost:5000/admin/scraping-data`
2. Klik **"Upload File"**
3. Pilih file untuk:
   - **File Data Energi** (opsional)
   - **File Data GDP** (opsional)
4. Klik **"Upload Files"**
5. Data akan divalidasi dan disimpan

**Format File yang Diperlukan:**

**Energy CSV/Excel:**
```
year,value,Entity
2020,84.5,Indonesia
2021,85.1,Indonesia
```

**GDP CSV/Excel:**
```
year,gdp
2020,1058423838327.52
2021,1186092991320.04
```

---

## 📁 Struktur File

```
Skripsi/
├── services/
│   └── update_data_api.py          # ⭐ Update: Fungsi-fungsi baru
├── routes/
│   ├── admin.py                    # Update: Import fungsi baru
│   └── api.py                      # ⭐ Update: Endpoint API baru
├── templates/admin/
│   └── scraping_data.html          # Frontend sudah ada
├── data/raw/
│   ├── energy.csv                  # Output data energi
│   └── gdp.csv                     # Output data GDP
├── sample_energy.csv               # ⭐ New: Contoh file energi
├── sample_gdp.csv                  # ⭐ New: Contoh file GDP
├── requirements.txt                # ⭐ New: Dependencies
└── API_DOCUMENTATION.md            # ⭐ New: Dokumentasi API

⭐ = File baru/diupdate
```

---

## 🔧 Fungsi-Fungsi Baru di `update_data_api.py`

### 1. `fetch_data_from_api(data_type, start_year, end_year)`
```python
# Fetch data dari API dengan filter
result = fetch_data_from_api('all', 1990, 2023)
# Returns: {"success": True, "energyCount": 34, "gdpCount": 34}
```

### 2. `upload_data_from_files(energy_file, gdp_file)`
```python
# Upload file CSV/Excel
result = upload_data_from_files(energy_file, gdp_file)
# Returns: {"success": True, "energyCount": 10, "gdpCount": 10}
```

### 3. `get_data_stats()`
```python
# Get statistik data
stats = get_data_stats()
# Returns: {"energyCount": 50, "gdpCount": 45, "lastUpdate": "..."}
```

### 4. `get_energy_data(limit)`
```python
# Get preview data energi
data = get_energy_data(10)
# Returns: [{"year": 2023, "country": "Indonesia", "value": 86.2}]
```

### 5. `get_gdp_data(limit)`
```python
# Get preview data GDP
data = get_gdp_data(10)
# Returns: [{"year": 2023, "country": "Indonesia", "value": 1371000000000}]
```

---

## 🌐 API Endpoints Baru

### GET `/api/data/stats`
Mendapatkan statistik data

### POST `/api/data/fetch`
Fetch data dari API eksternal

### POST `/api/data/upload`
Upload file data

### GET `/api/data/energy?limit=10`
Preview data energi

### GET `/api/data/gdp?limit=10`
Preview data GDP

**Detail lengkap:** Lihat [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 🧪 Testing

### Test dengan Sample Files:
```bash
# File sample sudah tersedia:
# - sample_energy.csv
# - sample_gdp.csv

# Upload via frontend atau test dengan curl:
curl -X POST http://localhost:5000/api/data/upload \
  -F "energyFile=@sample_energy.csv" \
  -F "gdpFile=@sample_gdp.csv"
```

### Test Fetch dari API:
```bash
curl -X POST http://localhost:5000/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{"dataType":"all","startYear":2015,"endYear":2023}'
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

Library yang ditambahkan:
- `openpyxl` - Untuk membaca file Excel (.xlsx)
- `xlrd` - Untuk membaca file Excel lama (.xls)

---

## ⚠️ Catatan Penting

1. **Format File Upload:**
   - Energy harus punya kolom: `year`, `value`
   - GDP harus punya kolom: `year`, `gdp`

2. **Koneksi Internet:**
   - Fetch dari API butuh koneksi internet
   - Upload file tidak perlu koneksi

3. **Storage:**
   - Semua data disimpan di `data/raw/`
   - File lama akan di-overwrite

4. **Error Handling:**
   - Semua error akan ditampilkan di frontend
   - Check console browser untuk detail error

---

## 🎯 Roadmap Future Features

- [ ] Background processing dengan Celery
- [ ] Scheduled scraping otomatis (APScheduler)
- [ ] Data versioning/history
- [ ] Export data dalam berbagai format
- [ ] Data validation lebih advanced
- [ ] Multi-country support
- [ ] Real-time notification

---

## 📞 Support

Jika ada pertanyaan atau issue:
1. Check API_DOCUMENTATION.md untuk detail endpoint
2. Lihat error message di browser console
3. Check terminal output untuk server errors

---

**Happy Coding! 🚀**
