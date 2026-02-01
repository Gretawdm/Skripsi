"""
PANDUAN PERHITUNGAN MANUAL ARIMAX (1,1,1) UNTUK LAPORAN SKRIPSI

Script ini menunjukkan langkah-langkah perhitungan manual ARIMAX
yang sama persis dengan sistem, untuk validasi laporan skripsi.

Model: ARIMAX(1,1,1) dengan exogenous variable GDP
- p=1: AR(1) - autoregressive order 1
- d=1: Differencing order 1 (untuk stasioneritas)
- q=1: MA(1) - moving average order 1

Author: Generated for thesis validation
Date: January 2026
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

def manual_arimax_calculation():
    """
    Perhitungan manual ARIMAX step-by-step untuk validasi laporan
    """
    
    print("=" * 80)
    print("PERHITUNGAN MANUAL ARIMAX(1,1,1) - UNTUK LAPORAN SKRIPSI")
    print("=" * 80)
    print()
    
    # ========== STEP 1: LOAD DATA ==========
    print("STEP 1: LOADING DATA")
    print("-" * 80)
    
    energy = pd.read_csv("data/raw/energy.csv")
    gdp = pd.read_csv("data/raw/gdp.csv")
    
    print(f"✓ Energy data loaded: {len(energy)} records")
    print(f"✓ GDP data loaded: {len(gdp)} records")
    print()
    
    # ========== STEP 2: DATA PREPROCESSING ==========
    print("STEP 2: DATA PREPROCESSING & ALIGNMENT")
    print("-" * 80)
    
    # Identifikasi kolom
    energy_year_col = "Year" if "Year" in energy.columns else "year"
    gdp_year_col = "year" if "year" in gdp.columns else "Year"
    
    energy_value_col = None
    for col in ["fossil_fuels__twh", "fossil_fuels", "value", "Energy"]:
        if col in energy.columns:
            energy_value_col = col
            break
    
    gdp_value_col = "gdp" if "gdp" in gdp.columns else "GDP"
    
    # Standardize
    energy_clean = energy[[energy_year_col, energy_value_col]].copy()
    energy_clean.columns = ["year", "energy"]
    
    gdp_clean = gdp[[gdp_year_col, gdp_value_col]].copy()
    gdp_clean.columns = ["year", "gdp"]
    
    # Remove duplicates & sort
    energy_clean = energy_clean.drop_duplicates(subset=["year"]).sort_values("year")
    gdp_clean = gdp_clean.drop_duplicates(subset=["year"]).sort_values("year")
    
    # INNER JOIN - hanya tahun yang ada di kedua dataset
    df = pd.merge(energy_clean, gdp_clean, on="year", how="inner")
    df = df.dropna()
    
    print(f"✓ Energy years: {energy_clean['year'].min()}-{energy_clean['year'].max()} ({len(energy_clean)} records)")
    print(f"✓ GDP years: {gdp_clean['year'].min()}-{gdp_clean['year'].max()} ({len(gdp_clean)} records)")
    print(f"✓ Matched years: {df['year'].min()}-{df['year'].max()} ({len(df)} records)")
    print()
    
    # ========== STEP 3: TRAIN-TEST SPLIT ==========
    print("STEP 3: TRAIN-TEST SPLIT")
    print("-" * 80)
    
    # Gunakan 80% untuk training (sesuai default sistem)
    train_ratio = 0.8
    train_size = int(len(df) * train_ratio)
    
    y = df["energy"]
    exog = df[["gdp"]]
    
    y_train = y.iloc[:train_size]
    y_test = y.iloc[train_size:]
    exog_train = exog.iloc[:train_size]
    exog_test = exog.iloc[train_size:]
    
    print(f"Total data: {len(df)} records")
    print(f"Training set: {len(y_train)} records ({int(train_ratio*100)}%)")
    print(f"Testing set: {len(y_test)} records ({int((1-train_ratio)*100)}%)")
    print(f"Train years: {df.iloc[:train_size]['year'].min()}-{df.iloc[:train_size]['year'].max()}")
    print(f"Test years: {df.iloc[train_size:]['year'].min()}-{df.iloc[train_size:]['year'].max()}")
    print()
    
    # ========== STEP 4: MODEL SPECIFICATION ==========
    print("STEP 4: MODEL SPECIFICATION - ARIMAX(1,1,1)")
    print("-" * 80)
    print("Model: ARIMAX(p, d, q) dengan exogenous variable")
    print("  p = 1  →  AR(1): Yt bergantung pada Yt-1")
    print("  d = 1  →  First differencing: ΔYt = Yt - Yt-1")
    print("  q = 1  →  MA(1): Error term bergantung pada εt-1")
    print("  exog   →  GDP sebagai variabel eksternal")
    print()
    print("Persamaan ARIMAX(1,1,1):")
    print("  ΔYt = β0 + φ1*ΔYt-1 + θ1*εt-1 + β*GDPt + εt")
    print()
    print("Dimana:")
    print("  ΔYt    = Yt - Yt-1 (first difference)")
    print("  φ1     = AR coefficient")
    print("  θ1     = MA coefficient")
    print("  β      = GDP coefficient")
    print("  εt     = Error term")
    print()
    
    # ========== STEP 5: MODEL TRAINING ==========
    print("STEP 5: MODEL TRAINING (Maximum Likelihood Estimation)")
    print("-" * 80)
    
    model = SARIMAX(
        y_train,
        exog=exog_train,
        order=(1, 1, 1),  # FIXED ORDER untuk reproducibility
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    
    result = model.fit(disp=False)
    
    print("✓ Model training selesai menggunakan MLE (Maximum Likelihood Estimation)")
    print()
    print("Parameter Estimates:")
    print("-" * 40)
    print(result.summary().tables[1])
    print()
    
    # ========== STEP 6: PREDICTION & EVALUATION ==========
    print("STEP 6: PREDICTION & EVALUATION METRICS")
    print("-" * 80)
    
    # Predict on test set
    predictions = result.forecast(steps=len(y_test), exog=exog_test)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
    
    # R-squared
    ss_res = np.sum((y_test - predictions) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    r2 = 1 - (ss_res / ss_tot)
    
    print("EVALUATION METRICS:")
    print(f"  MAE (Mean Absolute Error)    : {mae:.2f} TWh")
    print(f"  RMSE (Root Mean Squared Error): {rmse:.2f} TWh")
    print(f"  MAPE (Mean Absolute % Error)  : {mape:.2f}%")
    print(f"  R² (Coefficient of Determination): {r2:.4f}")
    print()
    
    # ========== STEP 7: DETAILED PREDICTION TABLE ==========
    print("STEP 7: DETAILED PREDICTION COMPARISON")
    print("-" * 80)
    
    comparison_df = pd.DataFrame({
        'Year': df.iloc[train_size:]['year'].values,
        'Actual (TWh)': y_test.values,
        'Predicted (TWh)': predictions.values,
        'Error (TWh)': y_test.values - predictions.values,
        'Absolute Error': np.abs(y_test.values - predictions.values),
        'APE (%)': np.abs((y_test.values - predictions.values) / y_test.values) * 100
    })
    
    print(comparison_df.to_string(index=False))
    print()
    print(f"Average APE (MAPE): {comparison_df['APE (%)'].mean():.2f}%")
    print()
    
    # ========== STEP 8: FORMULA & MANUAL CALCULATION EXAMPLE ==========
    print("STEP 8: CONTOH PERHITUNGAN MANUAL")
    print("-" * 80)
    print("Untuk validasi manual, gunakan parameter yang diperoleh dari Step 5:")
    print()
    
    # Extract coefficients
    ar_param = result.params.get('ar.L1', 0)
    ma_param = result.params.get('ma.L1', 0)
    gdp_param = result.params.get('gdp', 0)
    
    print(f"  AR coefficient (φ1)  : {ar_param:.6f}")
    print(f"  MA coefficient (θ1)  : {ma_param:.6f}")
    print(f"  GDP coefficient (β)  : {gdp_param:.6f}")
    print()
    print("Contoh prediksi untuk tahun pertama di test set:")
    print(f"  Tahun: {comparison_df.iloc[0]['Year']}")
    print(f"  Actual: {comparison_df.iloc[0]['Actual (TWh)']:.2f} TWh")
    print(f"  Predicted: {comparison_df.iloc[0]['Predicted (TWh)']:.2f} TWh")
    print(f"  Error: {comparison_df.iloc[0]['Error (TWh)']:.2f} TWh")
    print(f"  APE: {comparison_df.iloc[0]['APE (%)']:.2f}%")
    print()
    
    # ========== STEP 9: SAVE RESULTS ==========
    print("STEP 9: SAVE RESULTS FOR DOCUMENTATION")
    print("-" * 80)
    
    # Save comparison table to CSV
    comparison_df.to_csv("models/manual_calculation_results.csv", index=False)
    print("✓ Saved: models/manual_calculation_results.csv")
    
    # Save model summary to text file
    with open("models/model_summary.txt", "w") as f:
        f.write("=" * 80 + "\n")
        f.write("ARIMAX(1,1,1) MODEL SUMMARY - FOR THESIS DOCUMENTATION\n")
        f.write("=" * 80 + "\n\n")
        f.write(str(result.summary()))
        f.write("\n\n")
        f.write("=" * 80 + "\n")
        f.write("EVALUATION METRICS\n")
        f.write("=" * 80 + "\n")
        f.write(f"MAE  : {mae:.2f} TWh\n")
        f.write(f"RMSE : {rmse:.2f} TWh\n")
        f.write(f"MAPE : {mape:.2f}%\n")
        f.write(f"R²   : {r2:.4f}\n")
    
    print("✓ Saved: models/model_summary.txt")
    print()
    
    print("=" * 80)
    print("VALIDASI SELESAI!")
    print("=" * 80)
    print()
    print("File yang bisa digunakan untuk laporan:")
    print("  1. manual_calculation_results.csv - Tabel perbandingan prediksi vs actual")
    print("  2. model_summary.txt - Ringkasan lengkap model dan parameter")
    print()
    print("Untuk perhitungan manual di laporan, gunakan:")
    print("  - Parameter estimates dari model_summary.txt")
    print("  - Data training/testing yang sudah di-split")
    print("  - Persamaan ARIMAX(1,1,1) yang sudah dijelaskan di atas")
    print()
    
    return {
        'mae': mae,
        'rmse': rmse,
        'mape': mape,
        'r2': r2,
        'comparison': comparison_df,
        'model_summary': result.summary()
    }


if __name__ == "__main__":
    results = manual_arimax_calculation()
