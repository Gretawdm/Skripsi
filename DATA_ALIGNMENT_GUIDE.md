# 🔍 Panduan Data Alignment & Validasi

## ❓ Masalah yang Diatasi

Saat user input rentang tahun berbeda untuk data energi dan GDP dari API, bisa terjadi:
- **Jumlah data tidak sama** antara variabel X (GDP) dan Y (Energi)
- **Tahun yang tidak overlap** (misal: Energi 1990-2023, GDP 2000-2023)
- **Model ARIMAX error** karena memerlukan jumlah data yang sama

## ✅ Solusi yang Diimplementasikan

### 1. **Automatic Data Alignment** 🎯

Sistem akan otomatis:
- ✅ Mencari tahun yang **ada di kedua dataset** (intersection)
- ✅ Filter hanya tahun yang **match**
- ✅ Buang tahun yang hanya ada di satu dataset
- ✅ Informasikan ke user berapa data yang di-skip

**Contoh:**
```
Data Energi: 1990-2023 (34 tahun)
Data GDP:    2000-2023 (24 tahun)
Result:      2000-2023 (24 tahun) ✅
             10 tahun energi di-skip (1990-1999)
```

### 2. **Data Validation** ✔️

Sebelum training model, sistem validasi:
- ✅ File data ada atau tidak
- ✅ Kolom yang diperlukan tersedia
- ✅ Ada tahun yang overlap minimal 10 tahun
- ✅ Tidak ada missing values critical

### 3. **Error Prevention** 🛡️

Sistem mencegah error dengan:
- ✅ Inner join berdasarkan tahun (hanya ambil yang match)
- ✅ Validasi minimal 10 data points
- ✅ Drop NA values otomatis
- ✅ Error message yang jelas dan actionable

---

## 🔧 Implementasi Teknis

### A. Fetch dari API

File: `services/update_data_api.py` → `fetch_data_from_api()`

**Yang dilakukan:**
1. Fetch data energi dari OWID
2. Fetch data GDP dari World Bank
3. **Cari intersection tahun** (tahun yang ada di keduanya)
4. **Filter kedua dataset** hanya untuk tahun yang match
5. Save ke CSV
6. Return info berapa data yang di-align

**Kode:**
```python
# Cari tahun yang ada di kedua dataset
energy_years = set(energy_df["Year"].unique())
gdp_years = set(gdp_df["year"].unique())
common_years = sorted(energy_years.intersection(gdp_years))

# Filter hanya tahun yang match
energy_df = energy_df[energy_df["Year"].isin(common_years)]
gdp_df = gdp_df[gdp_df["year"].isin(common_years)]
```

### B. Upload File

File: `services/update_data_api.py` → `upload_data_from_files()`

**Yang dilakukan:**
1. Upload file energi & GDP
2. Validasi format dan kolom
3. **Align data** sama seperti fetch API
4. Save hanya data yang match
5. Return warning jika ada data di-skip

### C. Training Model

File: `services/train_service.py` → `retrain_model()`

**Yang dilakukan:**
1. Load data energi & GDP
2. **Inner join** berdasarkan tahun
3. Validasi minimal 10 data points
4. Drop NA values
5. Train ARIMAX model
6. Return detail info training

**Kode:**
```python
# INNER JOIN - ambil hanya tahun yang ada di kedua dataset
df = pd.merge(energy_clean, gdp_clean, on="year", how="inner")

# Validasi minimal data
if len(df) < 10:
    return error message
```

---

## 📊 API Endpoints Baru

### 1. Validasi Data
**GET** `/api/data/validate`

Cek apakah data siap untuk training.

**Response:**
```json
{
  "valid": true,
  "message": "Data kompatibel: 34 tahun cocok untuk training",
  "summary": {
    "total_energy_years": 62,
    "total_gdp_years": 64,
    "matched_years": 34,
    "year_range": "1965-2022"
  },
  "warnings": [
    "28 tahun energi tanpa GDP: [1965, 1966, ...]"
  ]
}
```

### 2. Alignment Report
**GET** `/api/data/alignment-report`

Get detail lengkap alignment data.

**Response:**
```json
{
  "energy": {
    "total_records": 62,
    "total_years": 62,
    "year_range": "1965-2022",
    "years": [1965, 1966, ...]
  },
  "gdp": {
    "total_records": 64,
    "total_years": 64,
    "year_range": "1960-2023",
    "years": [1960, 1961, ...]
  },
  "alignment": {
    "common_years": [1965, 1966, ...],
    "total_matched": 34,
    "year_range": "1965-2022",
    "energy_only_years": [],
    "gdp_only_years": [1960, 1961, 1962, 1963, 1964, 2023]
  }
}
```

---

## 🎯 Workflow User

### Scenario 1: Fetch dari API

1. User pilih rentang tahun: **1990-2023**
2. Sistem fetch data:
   - Energi: 1990-2023 (34 records)
   - GDP: 1960-2023 (64 records)
3. **Auto-align:** Ambil intersection 1990-2023 (34 records)
4. Save kedua file dengan 34 records
5. User dapat notifikasi: "Data disesuaikan: 34 tahun yang cocok"

### Scenario 2: Upload File

1. User upload:
   - `energy.csv`: 1965-2023 (59 tahun)
   - `gdp.csv`: 2000-2023 (24 tahun)
2. **Auto-align:** Ambil intersection 2000-2023 (24 records)
3. Save kedua file dengan 24 records
4. User dapat warning: "35 tahun energi di-skip"

### Scenario 3: Data Tidak Match

1. User upload:
   - `energy.csv`: 1990-2000
   - `gdp.csv`: 2010-2023
2. **Error:** "Tidak ada tahun yang sama"
3. User diminta upload data dengan tahun yang overlap

---

## 🧪 Testing

### Test Validasi Data
```bash
curl http://localhost:5000/api/data/validate
```

### Test Alignment Report
```bash
curl http://localhost:5000/api/data/alignment-report
```

### Test Fetch dengan Rentang Berbeda
```bash
curl -X POST http://localhost:5000/api/data/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "dataType": "all",
    "startYear": 1990,
    "endYear": 2023
  }'
```

---

## ⚠️ Aturan Validasi

### Minimal Requirements:
- ✅ **Minimal 10 tahun** data yang match
- ✅ **Kolom wajib:**
  - Energy: `year` + nilai (value/energy/fossil_fuels)
  - GDP: `year` + `gdp`
- ✅ **Tidak ada missing values** untuk tahun yang dipakai

### Error Messages:

**Jika data tidak cukup:**
```
"Data tidak cukup untuk training. Hanya 5 tahun yang cocok. 
Minimal 10 tahun diperlukan."
```

**Jika tidak ada overlap:**
```
"Tidak ada tahun yang sama antara data energi (1990-2000) 
dan GDP (2010-2023). Silakan sesuaikan rentang tahun."
```

---

## 💡 Best Practices

### 1. **Pilih Rentang Tahun yang Sama**
✅ DO:
- Start Year: 1990
- End Year: 2023
- (Kedua data sama)

❌ DON'T:
- Energy: 1965-2023
- GDP: 2000-2023
- (Akan banyak data di-skip)

### 2. **Check Validation Sebelum Training**
```javascript
// Frontend
fetch('/api/data/validate')
  .then(response => response.json())
  .then(data => {
    if (data.valid) {
      // OK untuk training
    } else {
      alert(data.message);
    }
  });
```

### 3. **Review Alignment Report**
Cek berapa data yang di-skip dan apakah masih cukup untuk training.

---

## 🔄 Diagram Flow

```
┌─────────────────┐
│ User Input Data │
│ (Fetch/Upload)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Parse & Extract     │
│ Year Columns        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Find Intersection   │
│ (Common Years)      │
└────────┬────────────┘
         │
         ▼
    ┌───┴───┐
    │ ≥10?  │
    └───┬───┘
        │
   YES  │  NO
    ▼   │   ▼
┌────────┐  ┌──────────┐
│ Filter │  │  Error   │
│  Data  │  │ Message  │
└───┬────┘  └──────────┘
    │
    ▼
┌────────────┐
│ Save to    │
│ CSV Files  │
└───┬────────┘
    │
    ▼
┌────────────┐
│ Ready for  │
│ Training   │
└────────────┘
```

---

## 📝 Summary

### Problem Solved ✅
- Jumlah data X dan Y tidak sama → **Auto-aligned**
- Tahun tidak overlap → **Intersection only**
- Model error → **Validated before training**
- User confusion → **Clear error messages**

### Key Features ✅
- Automatic data alignment
- Validation before training
- Detailed error messages
- Alignment report API
- Warning notifications

### Result ✅
Model ARIMAX selalu dapat data yang compatible dan tidak akan error karena perbedaan jumlah data! 🚀
