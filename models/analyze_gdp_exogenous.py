"""
ANALISIS MENDALAM: Peran Variabel Eksogen (GDP) dalam ARIMAX

PERTANYAAN KRITIS:
1. GDP masuk dimana dalam proses ARIMAX?
2. Apa bedanya ARIMA vs ARIMAX?
3. Bagaimana GDP mempengaruhi prediksi?

JAWABAN:
- ARIMA: y_t = f(y_{t-1}, y_{t-2}, ..., ε_{t-1}, ε_{t-2}, ...)
- ARIMAX: y_t = f(y_{t-1}, y_{t-2}, ..., **β·GDP_t**, ε_{t-1}, ε_{t-2}, ...)
                                           ↑
                                    VARIABEL EKSOGEN!
                                    
Author: Generated for thesis methodology
Date: January 2026
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

def test_with_different_splits(y, exog, order, model_name="ARIMAX"):
    """
    Test model dengan berbagai split ratio dan tampilkan koefisien GDP
    """
    
    splits = [0.70, 0.75, 0.80, 0.85]
    
    print(f"\n{'='*80}")
    print(f"TEST BERBAGAI SPLIT: {model_name}{order}")
    print(f"{'='*80}\n")
    
    results = []
    
    for ratio in splits:
        train_size = int(len(y) * ratio)
        test_size = len(y) - train_size
        
        if test_size < 5:
            continue
        
        y_train = y.iloc[:train_size]
        y_test = y.iloc[train_size:]
        exog_train = exog.iloc[:train_size]
        exog_test = exog.iloc[train_size:]
        
        split_label = f"{int(ratio*100)}:{int((1-ratio)*100)}"
        
        try:
            # Train model
            model = SARIMAX(
                y_train,
                exog=exog_train,
                order=order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            result = model.fit(disp=False, maxiter=200, method='lbfgs')
            
            # Predict
            predictions = result.forecast(steps=len(y_test), exog=exog_test)
            
            # Metrics
            mae = mean_absolute_error(y_test, predictions)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
            
            ss_res = np.sum((y_test - predictions) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            
            # Check convergence
            converged = not hasattr(result, 'mle_retvals') or \
                       (hasattr(result, 'mle_retvals') and result.mle_retvals.get('converged', True))
            
            # Check residual autocorrelation
            residuals = result.resid
            lb_test = acorr_ljungbox(residuals, lags=10, return_df=True)
            no_autocorr = (lb_test['lb_pvalue'] > 0.05).all()
            
            # EXTRACT KOEFISIEN GDP (variabel eksogen)
            gdp_coef = result.params['gdp']
            gdp_pvalue = result.pvalues['gdp']
            gdp_significant = gdp_pvalue < 0.05
            
            print(f"Split {split_label} (Train: {train_size}, Test: {test_size})")
            print(f"  MAPE          : {mape:>6.2f}%")
            print(f"  R²            : {r2:>6.4f}")
            print(f"  Converged     : {'✓' if converged else '⚠'}")
            print(f"  No Autocorr   : {'✓' if no_autocorr else '✗'}")
            print(f"  ")
            print(f"  📊 KOEFISIEN GDP (β):")
            print(f"     Nilai      : {gdp_coef:>10.6f}")
            print(f"     p-value    : {gdp_pvalue:>10.6f} {'(Signifikan ✓)' if gdp_significant else '(Tidak signifikan ✗)'}")
            print(f"     Interpretasi: Setiap GDP naik 1 Trillion → Energi {'naik' if gdp_coef > 0 else 'turun'} {abs(gdp_coef):.2f} TWh")
            print()
            
            results.append({
                'Model': f"{model_name}{order}",
                'Split': split_label,
                'Train_Size': train_size,
                'Test_Size': test_size,
                'MAPE': mape,
                'R2': r2,
                'MAE': mae,
                'RMSE': rmse,
                'GDP_Coef': gdp_coef,
                'GDP_pvalue': gdp_pvalue,
                'GDP_Significant': gdp_significant,
                'Converged': converged,
                'No_Autocorr': no_autocorr
            })
            
        except Exception as e:
            print(f"Split {split_label} - FAILED: {str(e)[:50]}\n")
    
    return pd.DataFrame(results)

def compare_arima_vs_arimax_detailed(y, exog, order, split_ratio=0.8):
    """
    Perbandingan detail ARIMA (tanpa GDP) vs ARIMAX (dengan GDP)
    Menunjukkan dimana GDP masuk dalam proses
    """
    
    print(f"\n{'='*80}")
    print(f"PERBANDINGAN DETAIL: ARIMA vs ARIMAX")
    print(f"Order: {order}, Split: {int(split_ratio*100)}:{int((1-split_ratio)*100)}")
    print(f"{'='*80}\n")
    
    train_size = int(len(y) * split_ratio)
    
    y_train = y.iloc[:train_size]
    y_test = y.iloc[train_size:]
    exog_train = exog.iloc[:train_size]
    exog_test = exog.iloc[train_size:]
    
    # ============== ARIMA (TANPA GDP) ==============
    print("="*80)
    print("MODEL 1: ARIMA (TANPA Variabel Eksogen)")
    print("="*80)
    print()
    print("Rumus Model:")
    print("  y_t = μ + φ₁·(y_{t-1} - μ) + φ₂·(y_{t-2} - μ) + ... +")
    print("        θ₁·ε_{t-1} + θ₂·ε_{t-2} + ... + ε_t")
    print()
    print("  Dimana:")
    print("  - y_t     : Konsumsi energi tahun t")
    print("  - y_{t-1} : Konsumsi energi tahun sebelumnya")
    print("  - φ (phi) : Koefisien AR (Autoregressive)")
    print("  - θ (theta): Koefisien MA (Moving Average)")
    print("  - ε (epsilon): Error/residual")
    print()
    print("  ❌ TIDAK ADA GDP dalam persamaan!")
    print()
    
    model_arima = SARIMAX(y_train, order=order, enforce_stationarity=False, enforce_invertibility=False)
    result_arima = model_arima.fit(disp=False)
    pred_arima = result_arima.forecast(steps=len(y_test))
    
    mape_arima = np.mean(np.abs((y_test - pred_arima) / y_test)) * 100
    mae_arima = mean_absolute_error(y_test, pred_arima)
    rmse_arima = np.sqrt(mean_squared_error(y_test, pred_arima))
    
    ss_res = np.sum((y_test - pred_arima) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    r2_arima = 1 - (ss_res / ss_tot)
    
    print("Hasil ARIMA:")
    print(f"  MAPE : {mape_arima:>8.2f}%")
    print(f"  MAE  : {mae_arima:>8.2f} TWh")
    print(f"  RMSE : {rmse_arima:>8.2f} TWh")
    print(f"  R²   : {r2_arima:>8.4f}")
    print(f"  AIC  : {result_arima.aic:>8.2f}")
    print()
    
    print("Parameter yang diestimasi:")
    print(result_arima.summary().tables[1])
    print()
    
    # ============== ARIMAX (DENGAN GDP) ==============
    print("="*80)
    print("MODEL 2: ARIMAX (DENGAN Variabel Eksogen GDP)")
    print("="*80)
    print()
    print("Rumus Model:")
    print("  y_t = μ + β·GDP_t + φ₁·(y_{t-1} - μ) + φ₂·(y_{t-2} - μ) + ... +")
    print("        θ₁·ε_{t-1} + θ₂·ε_{t-2} + ... + ε_t")
    print("           ↑")
    print("      VARIABEL EKSOGEN!")
    print()
    print("  Dimana:")
    print("  - y_t     : Konsumsi energi tahun t")
    print("  - GDP_t   : GDP tahun t (VARIABEL PENJELAS TAMBAHAN)")
    print("  - β (beta): KOEFISIEN GDP (pengaruh GDP terhadap energi)")
    print("  - y_{t-1} : Konsumsi energi tahun sebelumnya")
    print("  - φ (phi) : Koefisien AR")
    print("  - θ (theta): Koefisien MA")
    print()
    print("  ✅ GDP MASUK SEBAGAI PREDICTOR TAMBAHAN!")
    print()
    
    model_arimax = SARIMAX(
        y_train,
        exog=exog_train,
        order=order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    result_arimax = model_arimax.fit(disp=False)
    pred_arimax = result_arimax.forecast(steps=len(y_test), exog=exog_test)
    
    mape_arimax = np.mean(np.abs((y_test - pred_arimax) / y_test)) * 100
    mae_arimax = mean_absolute_error(y_test, pred_arimax)
    rmse_arimax = np.sqrt(mean_squared_error(y_test, pred_arimax))
    
    ss_res = np.sum((y_test - pred_arimax) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    r2_arimax = 1 - (ss_res / ss_tot)
    
    print("Hasil ARIMAX:")
    print(f"  MAPE : {mape_arimax:>8.2f}%")
    print(f"  MAE  : {mae_arimax:>8.2f} TWh")
    print(f"  RMSE : {rmse_arimax:>8.2f} TWh")
    print(f"  R²   : {r2_arimax:>8.4f}")
    print(f"  AIC  : {result_arimax.aic:>8.2f}")
    print()
    
    print("Parameter yang diestimasi:")
    print(result_arimax.summary().tables[1])
    print()
    
    # KOEFISIEN GDP
    gdp_coef = result_arimax.params['gdp']
    gdp_stderr = result_arimax.bse['gdp']
    gdp_pvalue = result_arimax.pvalues['gdp']
    gdp_ci_lower = result_arimax.conf_int().loc['gdp', 0]
    gdp_ci_upper = result_arimax.conf_int().loc['gdp', 1]
    
    print("="*80)
    print("📊 DETAIL KOEFISIEN GDP (β)")
    print("="*80)
    print()
    print(f"Nilai β (koefisien GDP)  : {gdp_coef:>10.6f}")
    print(f"Standard Error           : {gdp_stderr:>10.6f}")
    print(f"z-statistic              : {gdp_coef/gdp_stderr:>10.6f}")
    print(f"p-value                  : {gdp_pvalue:>10.6f}")
    print(f"95% Confidence Interval  : [{gdp_ci_lower:.6f}, {gdp_ci_upper:.6f}]")
    print()
    
    if gdp_pvalue < 0.05:
        print("✅ GDP SIGNIFIKAN (p-value < 0.05)")
        print(f"   → GDP memiliki pengaruh yang signifikan terhadap konsumsi energi")
    else:
        print("⚠️ GDP TIDAK SIGNIFIKAN (p-value >= 0.05)")
        print(f"   → Pengaruh GDP tidak terbukti signifikan")
    print()
    
    print("INTERPRETASI PRAKTIS:")
    print("-" * 80)
    print(f"Setiap kenaikan GDP sebesar 1 Trillion (2015 US$),")
    print(f"konsumsi energi akan {'NAIK' if gdp_coef > 0 else 'TURUN'} sebesar {abs(gdp_coef):.4f} TWh,")
    print(f"dengan asumsi faktor lain konstan (ceteris paribus).")
    print()
    
    # Example calculation
    sample_gdp = 500  # Trillion
    energy_contribution = gdp_coef * sample_gdp
    
    print("CONTOH PERHITUNGAN:")
    print("-" * 80)
    print(f"Jika GDP = {sample_gdp} Trillion,")
    print(f"Kontribusi GDP terhadap energi = β × GDP")
    print(f"                                = {gdp_coef:.6f} × {sample_gdp}")
    print(f"                                = {energy_contribution:.2f} TWh")
    print()
    
    # Comparison
    print("="*80)
    print("PERBANDINGAN ARIMA vs ARIMAX")
    print("="*80)
    print()
    
    improvement_mape = ((mape_arima - mape_arimax) / mape_arima) * 100
    improvement_aic = result_arima.aic - result_arimax.aic
    
    comparison = pd.DataFrame({
        'Metric': ['MAPE (%)', 'MAE (TWh)', 'RMSE (TWh)', 'R²', 'AIC'],
        'ARIMA': [mape_arima, mae_arima, rmse_arima, r2_arima, result_arima.aic],
        'ARIMAX': [mape_arimax, mae_arimax, rmse_arimax, r2_arimax, result_arimax.aic],
        'Improvement': [
            f"{improvement_mape:.2f}%",
            f"{mae_arima - mae_arimax:.2f}",
            f"{rmse_arima - rmse_arimax:.2f}",
            f"{r2_arimax - r2_arima:.4f}",
            f"{improvement_aic:.2f}"
        ]
    })
    
    print(comparison.to_string(index=False))
    print()
    
    if mape_arimax < mape_arima:
        print(f"✅ ARIMAX LEBIH BAIK!")
        print(f"   Penambahan variabel GDP meningkatkan akurasi {improvement_mape:.2f}%")
        print(f"   → JUSTIFIKASI: GDP terbukti membantu prediksi konsumsi energi")
    else:
        print(f"⚠️ ARIMA lebih baik")
        print(f"   GDP tidak memberikan improvement signifikan")
    print()
    
    return {
        'arima_mape': mape_arima,
        'arimax_mape': mape_arimax,
        'gdp_coef': gdp_coef,
        'gdp_pvalue': gdp_pvalue,
        'improvement': improvement_mape
    }

def main():
    print("="*80)
    print("ANALISIS: Peran GDP dalam ARIMAX + Test Split 80:20")
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
    
    y = df["energy"]
    exog = df[["gdp"]]
    
    print(f"Dataset: {len(df)} observasi ({int(df['year'].min())}-{int(df['year'].max())})")
    print()
    
    # Test kandidat terbaik dengan berbagai split
    print("="*80)
    print("BAGIAN 1: TEST KANDIDAT TERBAIK DENGAN BERBAGAI SPLIT")
    print("="*80)
    
    candidates = [
        (3, 2, 1),  # Best dari validasi sebelumnya
        (1, 1, 1),  # Baseline
        (3, 1, 1),  # Alternative
    ]
    
    all_results = []
    
    for order in candidates:
        df_result = test_with_different_splits(y, exog, order, "ARIMAX")
        all_results.append(df_result)
    
    df_all = pd.concat(all_results, ignore_index=True)
    
    # Focus on 80:20
    print("\n" + "="*80)
    print("FOKUS: HASIL DENGAN SPLIT 80:20")
    print("="*80)
    print()
    
    df_8020 = df_all[df_all['Split'] == '80:20'].sort_values('MAPE')
    
    if len(df_8020) > 0:
        print(df_8020[['Model', 'MAPE', 'R2', 'GDP_Coef', 'GDP_Significant', 'No_Autocorr']].to_string(index=False))
        print()
        
        best_8020 = df_8020.iloc[0]
        print(f"🏆 BEST dengan Split 80:20: {best_8020['Model']}")
        print(f"   MAPE: {best_8020['MAPE']:.2f}%")
        print(f"   R²  : {best_8020['R2']:.4f}")
        print(f"   GDP Coefficient: {best_8020['GDP_Coef']:.6f} ({'Signifikan ✓' if best_8020['GDP_Significant'] else 'Tidak ✗'})")
        print(f"   No Autocorr: {'✓' if best_8020['No_Autocorr'] else '✗'}")
    else:
        print("Tidak ada model yang berhasil dengan split 80:20")
    
    print()
    
    # Detailed ARIMA vs ARIMAX comparison
    print("="*80)
    print("BAGIAN 2: DIMANA GDP MASUK DALAM PROSES?")
    print("="*80)
    
    # Compare with best model
    best_order = (3, 2, 1)
    compare_arima_vs_arimax_detailed(y, exog, best_order, split_ratio=0.8)
    
    # Save
    df_all.to_csv("models/gdp_exogenous_analysis.csv", index=False)
    
    print("="*80)
    print("KESIMPULAN untuk SKRIPSI")
    print("="*80)
    print()
    print("PERAN VARIABEL EKSOGEN (GDP):")
    print("-" * 80)
    print("1. GDP masuk dalam PERSAMAAN MODEL sebagai predictor tambahan")
    print("   ARIMAX: y_t = μ + β·GDP_t + φ·y_{t-1} + θ·ε_{t-1} + ε_t")
    print("                     ↑")
    print("              Koefisien GDP (β)")
    print()
    print("2. GDP TIDAK masuk dalam proses differencing atau ACF/PACF")
    print("   - ACF/PACF hanya untuk menentukan p, d, q")
    print("   - GDP digunakan SETELAH model terbentuk")
    print()
    print("3. Koefisien β diestimasi bersama parameter lain (φ, θ)")
    print("   - Maximum Likelihood Estimation (MLE)")
    print("   - Minimasi sum of squared residuals")
    print()
    print("4. Untuk PREDIKSI:")
    print("   - Perlu data GDP masa depan (exogenous variable)")
    print("   - Energi_future = f(Energi_past, GDP_future)")
    print()
    
    print("✓ Saved: models/gdp_exogenous_analysis.csv")
    print()

if __name__ == "__main__":
    main()
