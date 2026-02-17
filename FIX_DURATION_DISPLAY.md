# Fix: Training Duration di Dashboard

## Masalah
- Duration di dashboard selalu menampilkan "-" (tidak ada data)
- Kolom `training_duration` tidak ada di tabel `training_history`
- API mencari kolom yang tidak ada

## Solusi yang Diterapkan

### 1. Database Schema Update
✅ Menambahkan kolom `training_duration` ke tabel `training_history`:
```sql
ALTER TABLE training_history 
ADD COLUMN training_duration DECIMAL(10, 2) NULL 
COMMENT 'Training duration in seconds'
```

### 2. Update Database Service
✅ File: `services/database_service.py`
- Update fungsi `save_training_history()` untuk menerima parameter `training_duration`
- Menambahkan `training_duration` ke query INSERT (untuk kedua case: dengan dan tanpa viz_plots)

### 3. Update Training Service  
✅ File: `services/train_service.py`
- Menambahkan parameter `training_duration` saat memanggil `save_training_history()`
- Duration sudah dihitung di training service, hanya perlu dipass ke database

### 4. Update API Endpoint
✅ File: `routes/api.py`
- Menyederhanakan kode untuk mengambil `training_duration` dari database
- Menghapus fallback ke file `model_metrics.pkl` (tidak diperlukan)

## Cara Testing

### 1. Jalankan server Flask:
```bash
python app.py
```

### 2. Test API endpoint:
```bash
python test_duration_display.py
```

### 3. Atau buka dashboard admin:
```
http://localhost:5000/admin/dashboard
```

## Expected Result

Setelah melakukan training model baru:
- Duration akan muncul di card "Model Performance Details"
- Format: `"2.34s"` atau `"45.67s"` (dalam detik)
- Data diambil dari kolom `training_duration` di tabel `training_history`

## Note

⚠️ **Duration hanya akan muncul setelah melakukan training model yang baru**

Model yang di-training sebelum update ini tidak memiliki data duration, sehingga akan tetap menampilkan "-". Untuk melihat duration:

1. Pergi ke `/admin/update-model`
2. Klik "Retrain Model" 
3. Setelah training selesai, duration akan tersimpan
4. Aktivasi model tersebut
5. Duration akan muncul di dashboard

## Files Modified
1. `add_training_duration_column.py` (NEW) - Script untuk update schema
2. `services/database_service.py` - Update save_training_history()
3. `services/train_service.py` - Pass training_duration ke database
4. `routes/api.py` - Simplify duration retrieval
5. `test_duration_display.py` (NEW) - Script untuk testing

## Files Created for Testing
- `check_duration_column.py` - Check database structure
- `test_duration_display.py` - Test API response
