# 🚀 CARA SETUP & PAKAI SISTEM DATABASE MYSQL

## 1. NYALAKAN XAMPP MySQL ⚡

1. Buka **XAMPP Control Panel**
2. Klik **Start** di MySQL
3. Tunggu sampai muncul hijau "Running"

## 2. BUAT DATABASE 📦

1. Buka browser: `http://localhost/phpmyadmin`
2. Klik tab **"Databases"**
3. Di "Create database", ketik: `arimax_forecasting`
4. Klik **"Create"**

## 3. JALANKAN APLIKASI 🎯

```bash
python app.py
```

Output yang benar:
```
✓ Database tables initialized successfully!
✓ Data tables initialized successfully!
✓ Database initialized successfully
```

Kalau ada error "Can't connect", cek XAMPP MySQL sudah running.

## 4. CARA KERJA SISTEM 🔄

### A. Fetch/Upload Data
```
User fetch data dari API atau upload file CSV
  ↓
Data disimpan ke:
  1. CSV file (data/raw/energy.csv & gdp.csv) → Untuk training model
  2. MySQL (energy_data & gdp_data) → Untuk tampilan & riwayat
  ↓
Riwayat tersimpan di: data_update_history
```

### B. Training Model
```
User klik "Mulai Training"
  ↓
Model baca dari CSV (data/raw/*.csv)
  ↓
Training selesai, metrics dihitung
  ↓
Hasil disimpan ke:
  1. File .pkl (models/*.pkl) → Untuk prediksi
  2. MySQL (training_history) → Untuk riwayat
  ↓
Tampil di halaman Riwayat
```

### C. Halaman Scraping Data
- Tabel Energy & GDP **LOAD DARI MySQL**
- Bukan dari CSV lagi!
- Refresh otomatis setelah fetch/upload

### D. Halaman Riwayat
- Tab Training: Lihat semua riwayat training dari database
- Tab Data Update: Lihat riwayat fetch/upload
- Tab Prediction: (Belum diimplementasi)

## 5. TEST SETELAH SETUP ✅

### Test 1: Koneksi Database
```bash
python -c "from services.database_service import test_connection; print('✓ Connected' if test_connection() else '✗ Failed')"
```

### Test 2: Fetch Data
1. Buka: `http://127.0.0.1:5000/admin/scraping-data`
2. Klik **"Fetch Data dari API"**
3. Tunggu proses selesai
4. Lihat tabel Energy & GDP terisi

### Test 3: Training & Riwayat
1. Buka: `http://127.0.0.1:5000/admin/update-model`
2. Klik **"Mulai Training"**
3. Tunggu sampai selesai (progress 100%)
4. Buka: `http://127.0.0.1:5000/admin/riwayat`
5. Tab "Riwayat Training Model" harus ada 1 data

## 6. TABEL DATABASE 📊

### Tabel `training_history`
- Menyimpan setiap kali training model
- Kolom: p, d, q, mape, rmse, mae, r2, dll

### Tabel `data_update_history`
- Menyimpan setiap kali fetch/upload data
- Kolom: update_type, source, records_added, status

### Tabel `energy_data`
- Data energy per tahun
- Kolom: year, fossil_fuels_twh

### Tabel `gdp_data`
- Data GDP per tahun
- Kolom: year, gdp

### Tabel `prediction_history`
- Belum diimplementasi (untuk prediksi user)

## 7. TROUBLESHOOTING 🔧

**❌ Error: Can't connect to MySQL server**
- Solusi: Cek XAMPP MySQL running (lampu hijau)

**❌ Error: Database 'arimax_forecasting' doesn't exist**
- Solusi: Buat manual di phpMyAdmin

**❌ Tabel kosong di halaman riwayat**
- Solusi: Belum ada training. Lakukan training dulu di Update Model

**❌ Tabel energy/GDP kosong di Scraping Data**
- Solusi: Belum fetch data. Klik "Fetch Data dari API"

**❌ Error: No module named 'mysql'**
```bash
pip install mysql-connector-python
```

## 8. CEK DATABASE DI PHPMYADMIN 🔍

1. Buka: `http://localhost/phpmyadmin`
2. Klik database `arimax_forecasting` di sidebar kiri
3. Lihat tabel:
   - `training_history` → Riwayat training
   - `data_update_history` → Riwayat update data
   - `energy_data` → Data energy
   - `gdp_data` → Data GDP
   - `prediction_history` → (Kosong, belum implementasi)

## 9. RESET DATABASE (OPTIONAL) 🗑️

Kalau mau mulai dari awal:

```bash
# Hapus semua riwayat
python -c "from services.database_service import clear_all_history; clear_all_history(); print('✓ History cleared')"
```

Atau manual di phpMyAdmin:
- Klik database `arimax_forecasting`
- Centang semua tabel
- Dropdown "With selected" → pilih "Empty"

## 10. BACKUP DATABASE 💾

Di phpMyAdmin:
1. Klik database `arimax_forecasting`
2. Tab "Export"
3. Klik "Go"
4. File `.sql` akan terdownload
