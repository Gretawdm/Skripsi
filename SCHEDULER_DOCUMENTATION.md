# 🕐 Fitur Jadwal Scraping Otomatis

## ✅ Status: **AKTIF & BERFUNGSI**

Fitur jadwal scraping otomatis sekarang sudah **fully functional** menggunakan **APScheduler**!

---

## 📋 Fitur yang Tersedia

### 1. **Pengaturan Jadwal**
- ✅ Frekuensi: Harian, Mingguan, Bulanan, atau **Tahunan**
- ✅ Pilih waktu eksekusi (misal: 02:00)
- ✅ Support zona waktu Indonesia (WIB/WITA/WIT)
- ✅ Enable/Disable kapan saja

### 2. **Monitoring**
- ✅ Lihat waktu eksekusi berikutnya
- ✅ Status aktif/nonaktif
- ✅ Log eksekusi di console/terminal

### 3. **Persistensi**
- ✅ Konfigurasi tersimpan di file JSON
- ✅ Auto-load saat aplikasi restart
- ✅ Jadwal tetap jalan meski server restart

---

## 🚀 Cara Menggunakan

### Aktivasi Jadwal:

1. Buka halaman: `http://localhost:5000/admin/scraping-data`
2. Scroll ke bagian **"Jadwal Scraping Otomatis"**
3. Klik toggle **"Aktifkan Jadwal Otomatis"**
4. Pilih pengaturan:
   - **Frekuensi**: Harian/Mingguan/Bulanan/**Tahunan**
   - **Waktu Eksekusi**: Misal 02:00 (jam 2 pagi)
   - **Zona Waktu**: WIB/WITA/WIT
5. Klik **"Simpan Jadwal"**
6. Sistem akan menampilkan **waktu eksekusi berikutnya**

### Contoh Konfigurasi:

**Scraping Harian (setiap hari jam 2 pagi WIB):**
- Frekuensi: Harian
- Waktu: 02:00
- Zona Waktu: WIB

**Scraping Mingguan (setiap Senin jam 3 pagi WIB):**
- Frekuensi: Mingguan
- Waktu: 03:00
- Zona Waktu: WIB

**Scraping Bulanan (setiap tanggal 1 jam 2 pagi WIB):**
- Frekuensi: Bulanan
- Waktu: 02:00
- Zona Waktu: WIB

**Scraping Tahunan (setiap 1 Juni jam 2 pagi WIB):** ⭐ RECOMMENDED
- Frekuensi: Tahunan
- Waktu: 02:00
- Zona Waktu: WIB
- **Cocok untuk data yang rilis tahunan di bulan Juni**

---

## 🔧 Technical Details

### Backend (Scheduler Service)

File: `services/scheduler_service.py`

**Fungsi Utama:**
- `setup_schedule()` - Setup cron job
- `save_schedule_config()` - Save ke JSON
- `load_schedule_config()` - Load dari JSON
- `get_schedule_status()` - Get status & next run
- `scheduled_fetch_job()` - Job yang dijalankan otomatis
- `initialize_scheduler()` - Auto-load saat app start

**Library:** APScheduler 3.10.4

### Frontend

**API Endpoints:**
- `POST /api/data/schedule` - Save jadwal
- `GET /api/data/schedule` - Get status jadwal

**UI Features:**
- Toggle switch untuk enable/disable
- Form pengaturan jadwal
- Display next run time
- Toast notification untuk feedback

---

## 📁 File Konfigurasi

Lokasi: `data/schedule_config.json`

Contoh isi:
```json
{
  "enabled": true,
  "frequency": "daily",
  "time": "02:00",
  "timezone": "Asia/Jakarta"
}
```

File ini otomatis dibuat saat pertama kali save jadwal.

---

## 📊 Cara Kerja

1. **User mengatur jadwal** via frontend
2. **Backend setup cron trigger** dengan APScheduler
3. **Config disimpan** ke JSON file
4. **Scheduler berjalan** di background
5. **Saat waktu tiba**, scheduler memanggil `scheduled_fetch_job()`
6. **Fungsi job** menjalankan `fetch_data_from_api('all', 1990, 2023)`
7. **Data tersimpan** ke CSV di `data/raw/`
8. **Log tampil** di terminal/console

---

## 🔍 Monitoring Jadwal

### Di Frontend:
- Lihat "Jadwal Berikutnya" di bagian schedule section
- Status badge akan update otomatis

### Di Terminal/Console:
```
[2026-01-22 23:45:30] Running scheduled data fetch...
[2026-01-22 23:45:35] Scheduled fetch completed successfully!
  - Energy records: 62
  - GDP records: 64
```

### Check Manual via API:
```bash
curl http://localhost:5000/api/data/schedule
```

Response:
```json
{
  "enabled": true,
  "frequency": "daily",
  "time": "02:00",
  "timezone": "Asia/Jakarta",
  "next_run": "23 Jan 2026 02:00:00",
  "is_running": true
}
```

---

## ⚠️ Catatan Penting

1. **Server Harus Running**
   - Jadwal hanya jalan saat Flask app running
   - Untuk production, gunakan systemd/supervisor/PM2

2. **Timezone**
   - Pastikan pilih timezone yang benar
   - Default: Asia/Jakarta (WIB)

3. **Koneksi Internet**
   - Job fetch data butuh internet
   - **Tahunan: Setiap 1 Juni pada waktu yg ditentukan** ⭐ NEW
   - Jika gagal, akan muncul error log

4. **Frekuensi Eksekusi**
   - Harian: Setiap hari pada waktu yg ditentukan
   - Mingguan: Setiap Senin pada waktu yg ditentukan
   - Bulanan: Setiap tanggal 1 pada waktu yg ditentukan

5. **Update Jadwal**
   - Bisa diupdate kapan saja
   - Otomatis replace jadwal lama
   - Disable dengan uncheck toggle

---

## 🧪 Testing

### Test Schedule Setup:
1. Set jadwal 2-3 menit dari sekarang
2. Tunggu dan lihat console log
3. Check apakah data terupdate di `data/raw/`

### Manual Trigger (untuk testing):
Buka Python console:
```python
from services.scheduler_service import scheduled_fetch_job
scheduled_fetch_job()
```

---

## 🎯 Roadmap Future Enhancements

- [ ] Email notification saat job selesai
- [ ] Retry mechanism jika gagal
- [ ] Job history/logs dalam database
- [ ] Multiple schedules (berbeda untuk energy & GDP)
- [ ] Custom date range per schedule
- [ ] Webhook notification
- [ ] Slack/Discord integration

---

## 🐛 Troubleshooting

**Jadwal tidak jalan:**
- Check apakah Flask app masih running
- Lihat terminal untuk error message
- Pastikan file `data/schedule_config.json` ada

**Next run time tidak muncul:**
- Refresh halaman
- Check console browser untuk error
- Pastikan jadwal sudah disimpan

**Data tidak terupdate:**
- Check internet connection
- Lihat error log di terminal
- Manual test dengan fetch data button

---

**Fitur ini sekarang fully functional! 🎉**

Jadwal akan berjalan otomatis sesuai konfigurasi dan data akan di-fetch secara otomatis tanpa intervensi manual.
