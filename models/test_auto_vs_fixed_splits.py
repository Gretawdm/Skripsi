"""
Test AUTO ARIMA dengan berbagai Train/Test Split

Tujuan: 
1. Cek order apa yang dipilih auto_arima untuk setiap split
2. Bandingkan MAPE auto_arima vs fixed (1,1,1)
3. Tentukan kombinasi split + model terbaik

Author: Generated for thesis methodology
Date: January 2026
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pmdarima import auto_arima
import warnings
warnings.filterwarnings('ignore')

def test_auto_arima_splits():
    print("=" * 80)
    print("UJI AUTO ARIMA DENGAN BERBAGAI TRAIN/TEST SPLIT")
    print("=" * 80)
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
    
    print(f"Total data: {len(df)} observasi")
    print(f"Period: {int(df['year'].min())}-{int(df['year'].max())}")
    print()
    
    # Prepare data
    y = df["energy"]
    exog = df[["gdp"]]
    
    # Test berbagai split ratios
    split_ratios = [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]
    
    results_auto = []
    results_fixed = []
    
    print("=" * 80)
    print("TESTING AUTO ARIMA vs FIXED (1,1,1)")
    print("=" * 80)
    print()
    
    for ratio in split_ratios:
        train_size = int(len(df) * ratio)
        test_size = len(df) - train_size
        
        # Validasi
        if test_size < 5 or train_size < 30:
            continue
        
        y_train = y.iloc[:train_size]
        y_test = y.iloc[train_size:]
        exog_train = exog.iloc[:train_size]
        exog_test = exog.iloc[train_size:]
        
        split_label = f"{int(ratio*100)}:{int((1-ratio)*100)}"
        
        print(f"Split {split_label} (Train: {train_size}, Test: {test_size})")
        print("-" * 80)
        
        # ===== AUTO ARIMA =====
        print("  [AUTO ARIMA] Finding optimal order...")
        try:
            auto_model = auto_arima(
                y_train,
                exogenous=exog_train,
                start_p=0, start_q=0,
                max_p=3, max_q=3,
                d=None, max_d=2,
                seasonal=False,
                trace=False,
                error_action='ignore',
                suppress_warnings=True,
                stepwise=True,
                information_criterion='aic'
            )
            
            auto_order = auto_model.order
            predictions_auto = auto_model.predict(n_periods=len(y_test), exogenous=exog_test)
            
            mae_auto = mean_absolute_error(y_test, predictions_auto)
            rmse_auto = np.sqrt(mean_squared_error(y_test, predictions_auto))
            mape_auto = np.mean(np.abs((y_test - predictions_auto) / y_test)) * 100
            
            ss_res = np.sum((y_test - predictions_auto) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2_auto = 1 - (ss_res / ss_tot)
            
            print(f"  [AUTO ARIMA] ✓ Order: {auto_order}")
            print(f"  [AUTO ARIMA] ✓ MAPE: {mape_auto:.2f}%, R²: {r2_auto:.4f}")
            
            results_auto.append({
                'Split': split_label,
                'Train_Size': train_size,
                'Test_Size': test_size,
                'Model': f'AUTO {auto_order}',
                'Order': str(auto_order),
                'p': auto_order[0],
                'd': auto_order[1],
                'q': auto_order[2],
                'MAPE': mape_auto,
                'RMSE': rmse_auto,
                'MAE': mae_auto,
                'R2': r2_auto,
                'AIC': auto_model.aic(),
                'Status': 'Success'
            })
            
        except Exception as e:
            print(f"  [AUTO ARIMA] ✗ FAILED: {str(e)[:50]}")
            results_auto.append({
                'Split': split_label,
                'Model': 'AUTO ARIMA',
                'Status': f'Failed: {str(e)[:30]}'
            })
        
        # ===== FIXED (1,1,1) =====
        print("  [FIXED 111] Training...")
        try:
            model_fixed = SARIMAX(
                y_train,
                exog=exog_train,
                order=(1, 1, 1),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            result_fixed = model_fixed.fit(disp=False)
            predictions_fixed = result_fixed.forecast(steps=len(y_test), exog=exog_test)
            
            mae_fixed = mean_absolute_error(y_test, predictions_fixed)
            rmse_fixed = np.sqrt(mean_squared_error(y_test, predictions_fixed))
            mape_fixed = np.mean(np.abs((y_test - predictions_fixed) / y_test)) * 100
            
            ss_res = np.sum((y_test - predictions_fixed) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2_fixed = 1 - (ss_res / ss_tot)
            
            print(f"  [FIXED 111] ✓ MAPE: {mape_fixed:.2f}%, R²: {r2_fixed:.4f}")
            
            results_fixed.append({
                'Split': split_label,
                'Train_Size': train_size,
                'Test_Size': test_size,
                'Model': 'FIXED (1,1,1)',
                'Order': '(1, 1, 1)',
                'p': 1,
                'd': 1,
                'q': 1,
                'MAPE': mape_fixed,
                'RMSE': rmse_fixed,
                'MAE': mae_fixed,
                'R2': r2_fixed,
                'AIC': result_fixed.aic,
                'Status': 'Success'
            })
            
        except Exception as e:
            print(f"  [FIXED 111] ✗ FAILED: {str(e)[:50]}")
        
        # Comparison
        if results_auto and results_auto[-1]['Status'] == 'Success':
            winner = "AUTO" if mape_auto < mape_fixed else "FIXED"
            diff = abs(mape_auto - mape_fixed)
            print(f"  [WINNER] {winner} (Δ{diff:.2f}% MAPE)")
        
        print()
    
    # Combine results
    all_results = pd.DataFrame(results_auto + results_fixed)
    all_results = all_results[all_results['Status'] == 'Success']
    
    print()
    print("=" * 80)
    print("HASIL: AUTO ARIMA - Order yang Dipilih untuk Setiap Split")
    print("=" * 80)
    print()
    
    auto_only = pd.DataFrame(results_auto)
    auto_only = auto_only[auto_only['Status'] == 'Success']
    print(auto_only[['Split', 'Order', 'MAPE', 'R2']].to_string(index=False))
    print()
    
    print("=" * 80)
    print("PERBANDINGAN: AUTO vs FIXED (1,1,1)")
    print("=" * 80)
    print()
    
    # Pivot untuk comparison
    comparison = []
    for split in all_results['Split'].unique():
        split_data = all_results[all_results['Split'] == split]
        
        auto_row = split_data[split_data['Model'].str.contains('AUTO')]
        fixed_row = split_data[split_data['Model'] == 'FIXED (1,1,1)']
        
        if not auto_row.empty and not fixed_row.empty:
            auto_row = auto_row.iloc[0]
            fixed_row = fixed_row.iloc[0]
            
            comparison.append({
                'Split': split,
                'Auto_Order': auto_row['Order'],
                'Auto_MAPE': auto_row['MAPE'],
                'Auto_R2': auto_row['R2'],
                'Fixed_MAPE': fixed_row['MAPE'],
                'Fixed_R2': fixed_row['R2'],
                'MAPE_Diff': auto_row['MAPE'] - fixed_row['MAPE'],
                'Winner': 'AUTO' if auto_row['MAPE'] < fixed_row['MAPE'] else 'FIXED'
            })
    
    df_comparison = pd.DataFrame(comparison)
    print(df_comparison.to_string(index=False))
    print()
    
    # Best overall
    print("=" * 80)
    print("REKOMENDASI FINAL")
    print("=" * 80)
    print()
    
    best_overall = all_results.sort_values('MAPE').iloc[0]
    
    print(f"🏆 KOMBINASI TERBAIK:")
    print(f"   Model: {best_overall['Model']}")
    print(f"   Split: {best_overall['Split']}")
    print(f"   Train: {int(best_overall['Train_Size'])} obs")
    print(f"   Test:  {int(best_overall['Test_Size'])} obs")
    print(f"   MAPE:  {best_overall['MAPE']:.2f}%")
    print(f"   R²:    {best_overall['R2']:.4f}")
    print()
    
    # Summary statistics
    auto_wins = (df_comparison['Winner'] == 'AUTO').sum()
    fixed_wins = (df_comparison['Winner'] == 'FIXED').sum()
    total = len(df_comparison)
    
    print(f"WIN RATE:")
    print(f"   AUTO ARIMA:    {auto_wins}/{total} ({auto_wins/total*100:.1f}%)")
    print(f"   FIXED (1,1,1): {fixed_wins}/{total} ({fixed_wins/total*100:.1f}%)")
    print()
    
    # Best for each
    best_auto = all_results[all_results['Model'].str.contains('AUTO')].sort_values('MAPE').iloc[0]
    best_fixed = all_results[all_results['Model'] == 'FIXED (1,1,1)'].sort_values('MAPE').iloc[0]
    
    print(f"BEST AUTO ARIMA:")
    print(f"   Split: {best_auto['Split']}, Order: {best_auto['Order']}")
    print(f"   MAPE: {best_auto['MAPE']:.2f}%, R²: {best_auto['R2']:.4f}")
    print()
    
    print(f"BEST FIXED (1,1,1):")
    print(f"   Split: {best_fixed['Split']}")
    print(f"   MAPE: {best_fixed['MAPE']:.2f}%, R²: {best_fixed['R2']:.4f}")
    print()
    
    # Save results
    all_results.to_csv("models/auto_vs_fixed_split_comparison.csv", index=False)
    df_comparison.to_csv("models/split_comparison_summary.csv", index=False)
    
    print("✓ Saved: models/auto_vs_fixed_split_comparison.csv")
    print("✓ Saved: models/split_comparison_summary.csv")
    print()
    
    # Recommendation
    print("=" * 80)
    print("KESIMPULAN UNTUK LAPORAN")
    print("=" * 80)
    print()
    
    if best_overall['Model'] == 'FIXED (1,1,1)':
        print("✓ REKOMENDASI: GUNAKAN FIXED (1,1,1)")
        print()
        print(f"  Alasan:")
        print(f"  1. Performa terbaik: MAPE {best_overall['MAPE']:.2f}% pada split {best_overall['Split']}")
        print(f"  2. Reproducible: Parameter tetap, hasil konsisten")
        print(f"  3. Interpretable: Koefisien dapat dijelaskan")
        print(f"  4. Win rate: {fixed_wins}/{total} kali mengalahkan AUTO ARIMA")
    else:
        print(f"⚠️ AUTO ARIMA lebih baik pada split {best_overall['Split']}")
        print(f"   Order: {best_overall['Order']}, MAPE: {best_overall['MAPE']:.2f}%")
        print()
        print(f"   Namun perlu pertimbangkan:")
        print(f"   - Reproducibility: AUTO bisa pilih order berbeda di run lain")
        print(f"   - Consistency: FIXED lebih predictable untuk laporan")
    
    print()
    
    return all_results, df_comparison


if __name__ == "__main__":
    results, comparison = test_auto_arima_splits()
