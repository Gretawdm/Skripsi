# Fix: Preview Tabel Data Energy Tidak Muncul

## Masalah Yang Ditemukan

1. **Duplikasi Route** - Ada 2 fungsi dengan route yang sama `/api/data/energy` dan `/api/data/gdp`
   - Fungsi pertama: `energy_data()` dan `gdp_data()`
   - Fungsi kedua: `get_energy_preview()` dan `get_gdp_preview()` (duplikat)
   - Flask menggunakan yang terakhir, sehingga response tidak konsisten

2. **Format Response Tidak Konsisten**
   - Frontend mengharapkan: `{success: true, data: [...]}`
   - API mengembalikan: array langsung `[...]` (tanpa wrapper)
   - Ini menyebabkan `result.success` dan `result.data` undefined

3. **Nama Kolom Tidak Sesuai**
   - Frontend mencari: `energy_value`
   - API mengembalikan: `fossil_fuels__twh`
   - Solusi: tambahkan alias `energy_value` di response

## Solusi Yang Diterapkan

### 1. Hapus Fungsi Duplikat
✅ Menghapus `get_energy_preview()` dan `get_gdp_preview()` yang duplikat

### 2. Perbaiki Format Response
✅ Semua API sekarang mengembalikan format konsisten:
```json
{
  "success": true,
  "data": [...],
  "count": 10
}
```

### 3. Tambahkan Alias Kolom
✅ Response energy data sekarang memiliki kedua nama kolom:
```json
{
  "year": 2020,
  "fossil_fuels__twh": 1234.56,
  "energy_value": 1234.56,  // Alias untuk frontend
  "updated_at": "2024-01-01T00:00:00"
}
```

### 4. Ubah Default Limit
✅ Mengubah default limit dari 100 menjadi 10 untuk konsistensi dengan frontend

### 5. Handle Data Kosong
✅ Saat data kosong, API tetap return `success: true` dengan `data: []` dan message informatif

## Files Modified

1. **routes/api.py**
   - Perbaiki `energy_data()` endpoint
   - Perbaiki `gdp_data()` endpoint
   - Hapus duplikat `get_energy_preview()` dan `get_gdp_preview()`

## Testing

### 1. Jalankan Flask server:
```bash
python app.py
```

### 2. Test API secara manual:
```bash
python test_preview_api.py
```

### 3. Test di browser:
1. Buka http://localhost:5000/admin/scraping-data
2. Klik tab "Data Energi" - seharusnya muncul data jika sudah ada di database
3. Klik tab "Data GDP" - seharusnya muncul data jika sudah ada di database
4. Klik "Refresh Preview" - data akan di-reload
5. Coba "Fetch dari API" atau "Upload File" - preview harus muncul setelah selesai

## Expected Result

✅ **Preview tabel energy** akan menampilkan data dengan kolom:
- No
- Tahun
- Negara (Indonesia)
- Konsumsi Energi Fosil (TWh)
- Terakhir Diupdate

✅ **Preview tabel GDP** akan menampilkan data dengan kolom:
- No
- Tahun
- Negara (Indonesia)
- GDP (USD)
- Terakhir Diupdate

## Troubleshooting

Jika masih tidak muncul:

1. **Cek Console Browser (F12)**
   - Lihat apakah ada error di Console
   - Lihat Network tab untuk cek response API

2. **Cek Database**
   - Pastikan ada data di tabel `energy_data` dan `gdp_data`
   - Run: `SELECT COUNT(*) FROM energy_data;`

3. **Cek Flask Log**
   - Lihat terminal tempat Flask running
   - Cek error message jika ada

4. **Test API Langsung**
   - Buka: http://localhost:5000/api/data/energy?limit=5
   - Buka: http://localhost:5000/api/data/gdp?limit=5
   - Harus return JSON dengan `success: true`
