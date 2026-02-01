# 📊 ALUR DATA PREDIKSI DI DASHBOARD

## ✅ Ya, Ini Data ASLI dari Hasil Training Model!

### 🔄 Alur Lengkap Data:

#### 1️⃣ **Data Historis (1965-2024)**
   - **Sumber**: Database MySQL
   - **Tabel**: 
     - `energy_data` → 60 records (1965-2024)
     - `gdp_data` → 60 records (1965-2024)
   - **Data Terakhir**: 
     - Energy 2024: **2663.05 TWh**
     - GDP 2024: **$1,238,236,350,136.56**

#### 2️⃣ **Model Training**
   - **File Model**: `models/arimax_model.pkl`
   - **Last Training**: 27 Januari 2026, 23:45:38
   - **Performa Model**:
     - MAPE: **7.07%** (akurasi sangat baik!)
     - R²: **0.3539**
     - MAE: 167.75 TWh
     - RMSE: 241.92 TWh

#### 3️⃣ **Prediksi (2025-2030)**
   - **Source Code**: `services/predict_service.py`
   - **Fungsi**: `predict_energy_service(scenario, years)`
   - **Method**: 
     1. Load model ARIMAX yang sudah di-training
     2. Ambil GDP terakhir (2024) dari data training
     3. Generate future GDP berdasarkan growth scenario:
        - Optimis: +6%/tahun
        - **Moderat: +5%/tahun** ← yang ditampilkan
        - Pesimistis: +3%/tahun
     4. Model melakukan forecast untuk 6 tahun (2025-2030)
     5. Return nilai dalam TWh

#### 4️⃣ **API Endpoint**
   - **Route**: `/api/dashboard/prediction`
   - **File**: `routes/api.py` baris 724-823
   - **Proses**:
     ```
     1. Ambil data energy dari tabel `energy_data`
     2. Ambil data GDP dari tabel `gdp_data`
     3. Panggil predict_energy_service() untuk prediksi
     4. Return JSON dengan historical + predictions
     ```

#### 5️⃣ **Tampilan Dashboard**
   - **Template**: `templates/admin/dashboard.html`
   - **Fungsi JS**: `loadPredictionData()` → `populatePredictionTable()`
   - **Data Ditampilkan**:
     ```
     2025: 3089.17 TWh
     2026: 3160.41 TWh
     2027: 3430.85 TWh
     2028: 3739.13 TWh
     2029: 3850.24 TWh
     2030: 4196.05 TWh
     ```

---

## 📌 Kesimpulan

**SEMUA DATA ASLI!**

✅ Data historis: Dari database tabel `energy_data` dan `gdp_data`  
✅ Prediksi: Hasil REAL dari model ARIMAX yang di-training  
✅ Bukan dummy/hardcoded  
✅ Model accuracy: MAPE 7.07% (sangat baik)  

### Tabel Database yang Digunakan:
1. **`energy_data`** - Data konsumsi energi fosil Indonesia (1965-2024)
2. **`gdp_data`** - Data GDP Indonesia (1965-2024)
3. **`training_history`** - Riwayat training model
4. **`prediction_history`** - History prediksi yang pernah dibuat (opsional)
