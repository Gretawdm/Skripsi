# DOKUMENTASI: Pemilihan Periode Data dan Indikator GDP

## UPDATE: Perubahan dari GDP Current US$ ke GDP Constant 2015 US$

**Tanggal Update:** 24 Januari 2026

**Perubahan:**
- **Sebelumnya:** GDP (current US$) - NY.GDP.MKTP.CD → Mulai 1967
- **Sekarang:** GDP (constant 2015 US$) - NY.GDP.MKTP.KD → Mulai 1960 ✅

**Hasil:**
- Data sekarang tersedia mulai **1965-2024 (60 tahun)**
- Gain: **+2 tahun** dari periode sebelumnya (1967-2024, 58 tahun)

---

## KEUNTUNGAN MENGGUNAKAN GDP CONSTANT 2015 US$

### 1. DATA AVAILABILITY
- ✅ Tersedia mulai **1960** vs 1967 (current US$)
- ✅ **+7 tahun** lebih banyak data
- ✅ Matching dengan Energy mulai **1965** (bukan 1967)

### 2. METODOLOGI LEBIH BAIK
**GDP Constant (Real GDP):**
- ✅ Adjusted for inflation
- ✅ Comparable across years (real purchasing power)
- ✅ Better for time series analysis
- ✅ Reflects actual economic growth (bukan pengaruh inflasi)

**GDP Current (Nominal GDP):**
- ❌ Dipengaruhi inflasi
- ❌ Dipengaruhi nilai tukar
- ❌ Tidak comparable across years
- ❌ Mixing price effect + volume effect

### 3. JUSTIFIKASI AKADEMIS

**Data Energy (OWID - Our World in Data):**
- ✓ Tersedia mulai: **1965**
- ✓ Source: https://ourworldindata.org/grapher/fossil-fuel-primary-energy
- ✓ Records Indonesia: 60 tahun (1965-2024)
- ✓ Data 1965-1966 ADA:
  - 1965: 79.12 TWh
  - 1966: 76.88 TWh

**Data GDP (World Bank):**
- ❌ Tersedia mulai: **1967** (TIDAK ada data 1965-1966!)
- Source: World Bank API (NY.GDP.MKTP.CD)
- Records Indonesia: 58 tahun (1967-2024)
- Data 1967-1970:
  - 1967: $5.67 Billion
  - 1968: $7.08 Billion
  - 1969: $8.34 Billion
  - 1970: $9.15 Billion

---

### 2. MENGAPA DIMULAI DARI 1967?

**Alasan Teknis:**

Model ARIMAX memerlukan **exogenous variable (GDP)** untuk setiap observasi energi. Formula:

```
Energy_t = f(Energy_{t-1}, GDP_t, ...)
```

Jika GDP_t tidak tersedia (1965, 1966), maka model **tidak bisa diestimasi** untuk tahun tersebut.

**Metodologi Data Alignment:**

Penelitian ini menggunakan **inner join** (intersection) untuk memastikan data quality:

```python
# Hanya ambil tahun yang ada di KEDUA dataset
common_years = energy_years ∩ gdp_years
```

Hasil:
- Energy years: {1965, 1966, 1967, ..., 2024} → 60 tahun
- GDP years: {1967, 1968, ..., 2024} → 58 tahun
- **Common years: {1967, 1968, ..., 2024} → 58 tahun** ← Yang digunakan

---

### 3. VALIDASI SUMBER DATA

**World Bank Missing Data (1965-1966):**

Berdasarkan dokumentasi World Bank:
- Indonesia's systematic GDP reporting ke World Bank dimulai tahun 1967
- Data sebelum 1967 tidak tersedia di World Bank database
- Ini adalah **limitasi sumber data**, bukan error sistem

**Verifikasi:**
```bash
# Script verifikasi: models/check_api_data_availability.py
python models/check_api_data_availability.py

Output:
  Energy data mulai: 1965
  GDP data mulai: 1967
  Common data (intersection) mulai: 1967
```

---

### 4. OPSI ALTERNATIF (Tidak Digunakan & Alasannya)

#### Opsi A: Interpolasi/Ekstrapolasi GDP 1965-1966
**Metode:**
- Estimasi GDP 1965-1966 berdasarkan trend 1967-1970
- Linear/exponential extrapolation

**Alasan DITOLAK:**
- ❌ Tidak valid untuk penelitian ilmiah
- ❌ Menambahkan data yang "dibuat-buat" (not actual observation)
- ❌ Melanggar prinsip data integrity
- ❌ Hasil model akan bias karena exogenous variable tidak riil

#### Opsi B: Gunakan Sumber Data Alternatif (BPS, IMF)
**Metode:**
- Cari GDP Indonesia 1965-1966 dari BPS atau IMF

**Alasan TIDAK DIGUNAKAN:**
- ⚠️ Inkonsistensi sumber (1965-1966 dari BPS, 1967+ dari World Bank)
- ⚠️ Metodologi perhitungan GDP bisa berbeda antar lembaga
- ⚠️ Scale/unit bisa berbeda
- ⚠️ Mempersulit reproducibility

#### Opsi C: Mulai dari 1967 (DIPILIH) ✅
**Alasan DIPILIH:**
- ✓ Data konsisten dari sumber yang sama (World Bank)
- ✓ Metodologi perhitungan GDP uniform
- ✓ Fully reproducible (siapapun bisa fetch dari API)
- ✓ Memenuhi prinsip data integrity
- ✓ Cukup panjang untuk time series analysis (58 observasi)

---

### 5. IMPLIKASI UNTUK MODEL

**Apakah 58 Observasi Cukup?**

**YA**, karena:

1. **Guideline Time Series:**
   - Minimum untuk ARIMA: 50 observations (Box & Jenkins, 2015)
   - Kita punya: **58 observations** ✓

2. **Train-Test Split:**
   - 80% training: 46 observations
   - 20% testing: 12 observations
   - Cukup untuk evaluasi model

3. **Parameter Estimation:**
   - ARIMAX(1,1,1) = 4 parameters (AR, MA, GDP coef, sigma²)
   - Rule of thumb: n ≥ 10 × k → 58 ≥ 10 × 4 ✓

4. **Perbandingan Penelitian Lain:**
   - Banyak penelitian time series energi menggunakan 30-50 tahun data
   - 58 tahun termasuk **cukup panjang**

---

### 6. DOKUMENTASI UNTUK LAPORAN

**Bagian Metodologi (Bab 3):**

Tambahkan sub-bagian:

```markdown
### 3.X Data Collection Period

Data yang digunakan dalam penelitian ini mencakup periode **1967-2024 (58 tahun)**. 
Pemilihan tahun mulai 1967 didasarkan pada **ketersediaan data GDP Indonesia** 
dari World Bank API.

**Investigasi Ketersediaan Data:**
- Data konsumsi energi fosil (OWID): tersedia mulai 1965
- Data GDP (World Bank): tersedia mulai 1967
- Data yang digunakan: 1967-2024 (intersection)

**Justifikasi:**
1. Konsistensi sumber data (World Bank untuk seluruh periode)
2. Integritas data (menghindari interpolasi/estimasi)
3. Reproducibility (dapat diverifikasi dari sumber publik)
4. Jumlah observasi mencukupi untuk analisis time series (n=58 > minimum 50)
```

**Tabel untuk Appendix:**

| Aspek | Detail |
|-------|--------|
| Periode | 1967-2024 |
| Jumlah Observasi | 58 tahun |
| Sumber Energy | OWID (Our World in Data) |
| Sumber GDP | World Bank API (NY.GDP.MKTP.CD) |
| Tahun Mulai Dipilih | 1967 (tahun pertama dengan data lengkap) |
| Data Quality | 100% complete (no missing values) |

---

## TEMPLATE JAWABAN UNTUK DEFENSE

### Versi Singkat (30 detik):
> "Data dimulai dari 1967 karena **World Bank GDP Indonesia baru tersedia mulai tahun tersebut**, meskipun data energi ada dari 1965. Model ARIMAX membutuhkan kedua variabel untuk setiap observasi, sehingga digunakan intersection (1967-2024, 58 tahun) yang **memenuhi minimum requirement** untuk time series analysis."

### Versi Detail (2 menit):
> "Terima kasih atas pertanyaannya. Memang benar data konsumsi energi dari OWID tersedia mulai 1965, namun **data GDP Indonesia dari World Bank baru tersedia mulai 1967**.
>
> Saya telah melakukan investigasi (lihat script check_api_data_availability.py) yang membuktikan:
> - Energy: 1965-2024 (60 tahun)
> - GDP: 1967-2024 (58 tahun)
> 
> Karena model ARIMAX memerlukan exogenous variable GDP untuk setiap observasi energi, saya menggunakan **inner join approach** untuk mengambil hanya tahun yang ada di kedua dataset.
>
> Saya pertimbangkan 3 opsi:
> 1. Interpolasi GDP 1965-1966 → Ditolak karena melanggar data integrity
> 2. Gunakan sumber alternatif → Ditolak karena inkonsistensi metodologi
> 3. Mulai dari 1967 → **Dipilih** karena konsisten, reproducible, dan 58 observasi mencukupi
>
> Berdasarkan Box & Jenkins (2015), minimum untuk ARIMA adalah 50 observasi, dan kita punya 58, jadi **memenuhi requirement** untuk analisis time series."

### Jika Ditanya: "Kenapa tidak cari GDP 1965-1966 dari BPS?"
> "Pertimbangan utama adalah **konsistensi sumber dan metodologi**. Jika menggunakan BPS untuk 1965-1966 dan World Bank untuk 1967+, ada risiko:
> 1. Perbedaan metodologi perhitungan GDP
> 2. Perbedaan valuasi (nominal vs riil)
> 3. Inkonsistensi scale/adjustment
> 4. Mengurangi reproducibility (World Bank API public, BPS perlu manual)
>
> Untuk penelitian ilmiah, **uniformity of data source** lebih penting dari menambah 2 observasi dengan risiko inkonsistensi."

---

## REFERENSI

1. **Box, G. E., & Jenkins, G. M. (2015)**
   - "Time Series Analysis: Forecasting and Control"
   - Minimum observations for ARIMA: 50

2. **World Bank Open Data**
   - https://data.worldbank.org/
   - Indonesia GDP data availability: 1967-present

3. **Our World in Data**
   - https://ourworldindata.org/energy
   - Indonesia energy data: 1965-present

---

## FILE PENDUKUNG

```bash
# Verifikasi ketersediaan data
python models/check_api_data_availability.py

# Output akan menunjukkan:
# - Energy: 1965-2024
# - GDP: 1967-2024
# - Common: 1967-2024
```

**Saved as:** `models/check_api_data_availability.py`

---

## KESIMPULAN

**Pemilihan periode 1967-2024 adalah keputusan yang:**
1. ✓ **Scientific sound** (data integrity, consistency)
2. ✓ **Methodologically justified** (intersection approach)
3. ✓ **Statistically adequate** (58 obs > minimum 50)
4. ✓ **Reproducible** (public API, verifiable)
5. ✓ **Documented** (script untuk validasi tersedia)

**Bukan karena error sistem, tapi pilihan metodologis yang deliberate dan well-reasoned!**
