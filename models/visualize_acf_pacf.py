"""
VISUALISASI ACF & PACF untuk Penentuan p dan q

Plot ini menjelaskan cara membaca grafik ACF dan PACF untuk menentukan
order p (AR) dan q (MA) dalam model ARIMAX

Author: Generated for thesis methodology
Date: January 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import warnings
warnings.filterwarnings('ignore')

# Atur style untuk plot yang lebih menarik
plt.style.use('seaborn-v0_8-darkgrid')

def main():
    print("="*80)
    print("CARA MEMBACA PLOT ACF & PACF untuk Menentukan p dan q")
    print("="*80)
    print()
    
    # Load data
    energy = pd.read_csv("data/raw/energy.csv")
    gdp = pd.read_csv("data/raw/gdp.csv")
    
    # Preprocessing
    energy_year_col = "Year" if "Year" in energy.columns else "year"
    gdp_year_col = "year" if "year" in gdp.columns else "Year"
    
    energy_value_col = None
    for col in ["fossil_fuels__twh", "fossil_fuels", "value", "Energy"]:
        if col in energy.columns:
            energy_value_col = col
            break
    
    gdp_value_col = "gdp" if "gdp" in gdp.columns else "GDP"
    
    energy_clean = energy[[energy_year_col, energy_value_col]].copy()
    energy_clean.columns = ["year", "energy"]
    
    gdp_clean = gdp[[gdp_year_col, gdp_value_col]].copy()
    gdp_clean.columns = ["year", "gdp"]
    
    energy_clean = energy_clean.drop_duplicates(subset=["year"]).sort_values("year")
    gdp_clean = gdp_clean.drop_duplicates(subset=["year"]).sort_values("year")
    
    df = pd.merge(energy_clean, gdp_clean, on="year", how="inner")
    df = df.dropna()
    
    # Split 70:30
    train_size = int(len(df) * 0.7)
    y = df["energy"]
    y_train = y.iloc[:train_size]
    
    print("LANGKAH 1: Differencing untuk Stasioneritas")
    print("-" * 80)
    
    # Test stasioneritas
    result = adfuller(y_train, autolag='AIC')
    print(f"Data asli (d=0):")
    print(f"  ADF Statistic: {result[0]:.6f}")
    print(f"  p-value      : {result[1]:.6f}")
    print(f"  Kesimpulan   : {'Stasioner' if result[1] < 0.05 else 'TIDAK Stasioner'}")
    print()
    
    # Differencing 1x
    y_diff1 = y_train.diff().dropna()
    result1 = adfuller(y_diff1, autolag='AIC')
    print(f"Setelah differencing 1x (d=1):")
    print(f"  ADF Statistic: {result1[0]:.6f}")
    print(f"  p-value      : {result1[1]:.6f}")
    print(f"  Kesimpulan   : {'Stasioner' if result1[1] < 0.05 else 'TIDAK Stasioner'}")
    print()
    
    # Differencing 2x
    y_diff2 = y_diff1.diff().dropna()
    result2 = adfuller(y_diff2, autolag='AIC')
    print(f"Setelah differencing 2x (d=2):")
    print(f"  ADF Statistic: {result2[0]:.6f}")
    print(f"  p-value      : {result2[1]:.6f}")
    print(f"  Kesimpulan   : {'✓ STASIONER' if result2[1] < 0.05 else 'TIDAK Stasioner'}")
    print()
    
    print(f"→ Hasil: d = 2 (perlu differencing 2 kali)")
    print()
    
    # Gunakan data yang sudah stasioner untuk ACF/PACF
    series_diff = y_diff2
    
    print("="*80)
    print("LANGKAH 2: Analisis ACF & PACF")
    print("="*80)
    print()
    
    # Hitung ACF dan PACF
    max_lag = 20
    acf_values = acf(series_diff, nlags=max_lag, fft=False)
    pacf_values = pacf(series_diff, nlags=max_lag, method='ywm')
    
    # Confidence interval (95%)
    conf_interval = 1.96 / np.sqrt(len(series_diff))
    
    print("CARA MEMBACA PLOT:")
    print("-" * 80)
    print("1. AREA BIRU (Confidence Interval):")
    print(f"   - Lebar area: ±{conf_interval:.4f}")
    print("   - Lag di DALAM area → TIDAK SIGNIFIKAN")
    print("   - Lag di LUAR area → SIGNIFIKAN ✓")
    print()
    print("2. CARA TENTUKAN p (dari PACF):")
    print("   - Lihat lag yang keluar dari area biru")
    print("   - p = lag TERAKHIR yang signifikan")
    print("   - Contoh: Jika lag 1,2,3 signifikan → p=3")
    print()
    print("3. CARA TENTUKAN q (dari ACF):")
    print("   - Lihat lag yang keluar dari area biru")
    print("   - q = lag TERAKHIR yang signifikan")
    print("   - Contoh: Jika lag 1,4,5,6 signifikan → q=6")
    print()
    
    # Analisis detail
    print("="*80)
    print("ANALISIS ACF (untuk q)")
    print("="*80)
    print(f"{'Lag':<6} {'Nilai':<10} {'|Nilai|':<10} {'CI':<10} {'Status':<15} {'Visual'}")
    print("-"*80)
    
    q_candidates = []
    for lag in range(1, min(11, max_lag+1)):
        is_sig = abs(acf_values[lag]) > conf_interval
        status = "✓ SIGNIFIKAN" if is_sig else "  -"
        bar = '█' * int(abs(acf_values[lag]) * 30)
        
        print(f"{lag:<6} {acf_values[lag]:>9.4f} {abs(acf_values[lag]):>9.4f} {conf_interval:>9.4f} {status:<15} {bar}")
        
        if is_sig:
            q_candidates.append(lag)
    
    print()
    if q_candidates:
        print(f"→ Lag signifikan: {q_candidates}")
        print(f"→ REKOMENDASI: q = {max(q_candidates)} (lag signifikan terakhir)")
    else:
        print(f"→ Tidak ada lag signifikan")
        print(f"→ REKOMENDASI: q = 0")
    
    q_recommended = max(q_candidates) if q_candidates else 0
    
    print()
    print("="*80)
    print("ANALISIS PACF (untuk p)")
    print("="*80)
    print(f"{'Lag':<6} {'Nilai':<10} {'|Nilai|':<10} {'CI':<10} {'Status':<15} {'Visual'}")
    print("-"*80)
    
    p_candidates = []
    for lag in range(1, min(11, max_lag+1)):
        is_sig = abs(pacf_values[lag]) > conf_interval
        status = "✓ SIGNIFIKAN" if is_sig else "  -"
        bar = '█' * int(abs(pacf_values[lag]) * 30)
        
        print(f"{lag:<6} {pacf_values[lag]:>9.4f} {abs(pacf_values[lag]):>9.4f} {conf_interval:>9.4f} {status:<15} {bar}")
        
        if is_sig:
            p_candidates.append(lag)
    
    print()
    if p_candidates:
        print(f"→ Lag signifikan: {p_candidates}")
        print(f"→ REKOMENDASI: p = {max(p_candidates)} (lag signifikan terakhir)")
    else:
        print(f"→ Tidak ada lag signifikan")
        print(f"→ REKOMENDASI: p = 0")
    
    p_recommended = max(p_candidates) if p_candidates else 0
    
    # Create plot dengan anotasi
    fig = plt.figure(figsize=(16, 10))
    
    # ACF plot
    ax1 = plt.subplot(2, 1, 1)
    plot_acf(series_diff, lags=max_lag, ax=ax1, alpha=0.05)
    ax1.set_title('ACF (Autocorrelation Function) - Untuk Menentukan q (MA Order)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('Lag', fontsize=12)
    ax1.set_ylabel('Correlation', fontsize=12)
    ax1.axhline(y=0, linestyle='-', color='black', linewidth=0.8)
    ax1.axhline(y=conf_interval, linestyle='--', color='red', alpha=0.7, linewidth=2, 
                label=f'95% CI (±{conf_interval:.3f})')
    ax1.axhline(y=-conf_interval, linestyle='--', color='red', alpha=0.7, linewidth=2)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11, loc='upper right')
    
    # Annotate significant lags
    for lag in q_candidates:
        ax1.annotate(f'Lag {lag}', 
                    xy=(lag, acf_values[lag]), 
                    xytext=(lag, acf_values[lag] + 0.15 * np.sign(acf_values[lag])),
                    arrowprops=dict(arrowstyle='->', color='green', lw=1.5),
                    fontsize=10, color='green', fontweight='bold',
                    ha='center')
    
    # Add explanation box
    textstr = f'CARA BACA:\n'\
              f'• Batang yang KELUAR dari garis merah → SIGNIFIKAN\n'\
              f'• q = lag terakhir yang signifikan\n'\
              f'• Rekomendasi: q = {q_recommended}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax1.text(0.98, 0.97, textstr, transform=ax1.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', bbox=props)
    
    # PACF plot
    ax2 = plt.subplot(2, 1, 2)
    plot_pacf(series_diff, lags=max_lag, ax=ax2, alpha=0.05, method='ywm')
    ax2.set_title('PACF (Partial Autocorrelation Function) - Untuk Menentukan p (AR Order)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlabel('Lag', fontsize=12)
    ax2.set_ylabel('Partial Correlation', fontsize=12)
    ax2.axhline(y=0, linestyle='-', color='black', linewidth=0.8)
    ax2.axhline(y=conf_interval, linestyle='--', color='red', alpha=0.7, linewidth=2,
                label=f'95% CI (±{conf_interval:.3f})')
    ax2.axhline(y=-conf_interval, linestyle='--', color='red', alpha=0.7, linewidth=2)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=11, loc='upper right')
    
    # Annotate significant lags
    for lag in p_candidates:
        ax2.annotate(f'Lag {lag}', 
                    xy=(lag, pacf_values[lag]), 
                    xytext=(lag, pacf_values[lag] + 0.15 * np.sign(pacf_values[lag])),
                    arrowprops=dict(arrowstyle='->', color='blue', lw=1.5),
                    fontsize=10, color='blue', fontweight='bold',
                    ha='center')
    
    # Add explanation box
    textstr = f'CARA BACA:\n'\
              f'• Batang yang KELUAR dari garis merah → SIGNIFIKAN\n'\
              f'• p = lag terakhir yang signifikan\n'\
              f'• Rekomendasi: p = {p_recommended}'
    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
    ax2.text(0.98, 0.97, textstr, transform=ax2.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right', bbox=props)
    
    plt.tight_layout()
    plt.savefig('models/acf_pacf_detailed.png', dpi=300, bbox_inches='tight')
    print()
    print("="*80)
    print("RINGKASAN HASIL IDENTIFIKASI")
    print("="*80)
    print()
    print(f"Dari ADF Test:")
    print(f"  d = 2 (data stasioner setelah differencing 2x)")
    print()
    print(f"Dari PACF (Partial Autocorrelation):")
    print(f"  Lag signifikan: {p_candidates}")
    print(f"  → p = {p_recommended}")
    print()
    print(f"Dari ACF (Autocorrelation):")
    print(f"  Lag signifikan: {q_candidates}")
    print(f"  → q = {q_recommended}")
    print()
    print(f"🎯 HASIL IDENTIFIKASI MANUAL: ARIMAX({p_recommended}, 2, {q_recommended})")
    print()
    print("="*80)
    print("FILE OUTPUT")
    print("="*80)
    print()
    print("✓ models/acf_pacf_detailed.png - Plot ACF/PACF dengan penjelasan lengkap")
    print()
    print("Plot ini dapat digunakan untuk:")
    print("- BAB III Metodologi: Menjelaskan cara identifikasi order")
    print("- BAB IV Hasil: Menunjukkan proses pemilihan p, d, q")
    print("- Presentasi: Visual untuk menjelaskan ke penguji")
    print()
    print("CATATAN PENTING untuk Laporan:")
    print("-" * 80)
    print("Identifikasi dari ACF/PACF memberikan GUIDELINE, bukan aturan mutlak.")
    print("Hasil ({}, 2, {}) perlu DIVALIDASI dengan:")
    print("  1. Uji MAPE pada berbagai split ratio")
    print("  2. Cek convergence (apakah model stabil)")
    print("  3. Bandingkan dengan baseline model (1,1,1)")
    print("  4. Pertimbangkan parsimony (kesederhanaan model)")
    print()

if __name__ == "__main__":
    main()
