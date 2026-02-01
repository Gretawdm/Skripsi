# Setup Database MySQL

## 1. Buat Database

Buka phpMyAdmin (XAMPP) dan buat database baru:

```sql
CREATE DATABASE arimax_forecasting;
```

## 2. Konfigurasi Database

File: `services/database_service.py`

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''  # Kosong untuk XAMPP default
}
```

Kalau password MySQL kamu bukan kosong, ubah di line `password`.

## 3. Tabel Otomatis Dibuat

Saat pertama kali jalankan `python app.py`, tabel-tabel ini otomatis dibuat:

### Tabel `training_history`
Menyimpan riwayat training model:
- training_date
- model_version
- p, d, q (parameter ARIMAX)
- mape, rmse, mae, r2 (metrics)
- train_size, test_size
- year_range
- energy & GDP statistics

### Tabel `data_update_history`
Menyimpan riwayat update data:
- update_date
- update_type (fetch_api / manual_upload)
- source
- records_added, records_updated
- status

### Tabel `prediction_history`
Menyimpan riwayat prediksi:
- prediction_date
- scenario (optimis/moderat/pesimistis)
- years
- prediction_data (JSON)
- model_version

## 4. Cara Kerja

### A. Saat Training Model
```
User klik "Mulai Training" 
  → Model training
  → Metrics dihitung
  → Simpan ke file .pkl (existing)
  → **BARU: Simpan ke database (training_history)**
  → Tampil di halaman Update Model
  → **BARU: Tampil di halaman Riwayat**
```

### B. Halaman Riwayat
- **Tab Training**: Lihat semua riwayat training dari database
- **Tab Data Update**: Lihat riwayat fetch/upload data (belum implementasi simpan)
- **Tab Prediction**: Lihat riwayat prediksi (belum implementasi simpan)

## 5. API Endpoints Baru

```
GET  /api/history/training      - List training history
GET  /api/history/data-update   - List data update history
GET  /api/history/prediction    - List prediction history
GET  /api/history/summary       - Summary statistics
DELETE /api/history/clear       - Clear all history
```

## 6. Test Database

```bash
# Test koneksi
python -c "from services.database_service import test_connection; print('✓ OK' if test_connection() else '✗ Failed')"

# Init database manually
python -c "from services.database_service import init_database; init_database()"
```

## 7. Troubleshooting

**Error: No module named 'mysql'**
```bash
pip install mysql-connector-python
```

**Error: Access denied for user 'root'**
- Cek password MySQL di phpMyAdmin
- Update `password` di `DB_CONFIG`

**Tabel tidak terbuat**
- Pastikan XAMPP MySQL sudah running
- Cek di phpMyAdmin apakah database `arimax_forecasting` ada
- Run manual: `python -c "from services.database_service import init_database; init_database()"`
