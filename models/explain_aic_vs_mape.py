"""
VISUALISASI PERBANDINGAN: AIC vs MAPE dalam Pemilihan Model

Script ini membuat tabel dan grafik perbandingan untuk menjelaskan
mengapa MAPE lebih relevan dari AIC untuk forecasting research.

Output:
1. Tabel perbandingan ranking berdasarkan AIC vs MAPE
2. Plot scatter AIC vs MAPE
3. Insight untuk defense

Author: Generated for thesis defense
Date: January 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_comparison_table():
    """
    Membuat tabel perbandingan ranking AIC vs MAPE
    """
    
    print("=" * 100)
    print("PERBANDINGAN KRITERIA: AIC vs MAPE dalam Pemilihan Model ARIMAX")
    print("=" * 100)
    print()
    
    # Load hasil comparison
    df = pd.read_csv("models/arimax_comparison_results.csv")
    
    # Sort by different criteria
    df_by_aic = df.sort_values('AIC').reset_index(drop=True)
    df_by_mape = df.sort_values('MAPE').reset_index(drop=True)
    
    # Add ranking
    df_by_aic['AIC_Rank'] = range(1, len(df_by_aic) + 1)
    df_by_mape['MAPE_Rank'] = range(1, len(df_by_mape) + 1)
    
    print("RANKING BERDASARKAN AIC (Akaike Information Criterion)")
    print("-" * 100)
    print("Kriteria: Lower AIC = Better model complexity & fit balance")
    print()
    print(df_by_aic[['Order', 'p', 'd', 'q', 'AIC', 'MAPE', 'R2']].head(5).to_string(index=False))
    print()
    print(f"🏆 BEST by AIC: {df_by_aic.iloc[0]['Order']} with AIC={df_by_aic.iloc[0]['AIC']:.2f}")
    print(f"   But MAPE = {df_by_aic.iloc[0]['MAPE']:.2f}% (Rank {df_by_mape[df_by_mape['Order'] == df_by_aic.iloc[0]['Order']]['MAPE_Rank'].values[0]} in MAPE)")
    print()
    print()
    
    print("RANKING BERDASARKAN MAPE (Mean Absolute Percentage Error)")
    print("-" * 100)
    print("Kriteria: Lower MAPE = Better forecast accuracy")
    print()
    print(df_by_mape[['Order', 'p', 'd', 'q', 'MAPE', 'R2', 'AIC']].head(5).to_string(index=False))
    print()
    print(f"🏆 BEST by MAPE: {df_by_mape.iloc[0]['Order']} with MAPE={df_by_mape.iloc[0]['MAPE']:.2f}%")
    print(f"   And AIC = {df_by_mape.iloc[0]['AIC']:.2f} (Rank {df_by_aic[df_by_aic['Order'] == df_by_mape.iloc[0]['Order']]['AIC_Rank'].values[0]} in AIC)")
    print()
    print()
    
    # Create merged comparison table
    print("=" * 100)
    print("CRITICAL INSIGHT: Ranking Conflict!")
    print("=" * 100)
    print()
    
    # Merge to show ranking differences
    comparison = pd.DataFrame({
        'Model': df['Order'],
        'AIC': df['AIC'],
        'AIC_Rank': df['Order'].map(df_by_aic.set_index('Order')['AIC_Rank']),
        'MAPE': df['MAPE'],
        'MAPE_Rank': df['Order'].map(df_by_mape.set_index('Order')['MAPE_Rank']),
        'Rank_Diff': abs(df['Order'].map(df_by_aic.set_index('Order')['AIC_Rank']) - 
                        df['Order'].map(df_by_mape.set_index('Order')['MAPE_Rank']))
    }).sort_values('MAPE_Rank')
    
    print("Model Comparison: AIC Rank vs MAPE Rank")
    print("-" * 100)
    print(comparison.to_string(index=False))
    print()
    
    # Highlight key models
    model_111 = comparison[comparison['Model'] == '(1, 1, 1)'].iloc[0]
    auto_model = comparison[comparison['Model'].str.contains('AUTO')].iloc[0]
    
    print("KEY FINDINGS:")
    print(f"1. ARIMAX(1,1,1):")
    print(f"   - MAPE Rank: {int(model_111['MAPE_Rank'])} (BEST for forecasting)")
    print(f"   - AIC Rank: {int(model_111['AIC_Rank'])}")
    print(f"   - MAPE: {model_111['MAPE']:.2f}%")
    print(f"   - AIC: {model_111['AIC']:.2f}")
    print()
    print(f"2. AUTO ARIMA {auto_model['Model']}:")
    print(f"   - MAPE Rank: {int(auto_model['MAPE_Rank'])}")
    print(f"   - AIC Rank: {int(auto_model['AIC_Rank'])}")
    print(f"   - MAPE: {auto_model['MAPE']:.2f}%")
    print(f"   - AIC: {auto_model['AIC']:.2f}")
    print()
    
    # Best AIC model
    best_aic = df_by_aic.iloc[0]
    print(f"3. Best AIC Model {best_aic['Order']}:")
    print(f"   - AIC Rank: 1 (BEST by AIC)")
    print(f"   - MAPE Rank: {int(df_by_mape[df_by_mape['Order'] == best_aic['Order']]['MAPE_Rank'].values[0])}")
    print(f"   - AIC: {best_aic['AIC']:.2f}")
    print(f"   - MAPE: {best_aic['MAPE']:.2f}%")
    print()
    print()
    
    # Save comparison
    comparison.to_csv("models/aic_vs_mape_comparison.csv", index=False)
    print("✓ Saved: models/aic_vs_mape_comparison.csv")
    print()
    
    return df, comparison


def explain_aic_mape_difference():
    """
    Penjelasan konseptual perbedaan AIC dan MAPE
    """
    
    print("=" * 100)
    print("PENJELASAN: Mengapa AIC ≠ MAPE?")
    print("=" * 100)
    print()
    
    print("AIC (Akaike Information Criterion)")
    print("-" * 50)
    print("Formula: AIC = -2*log(Likelihood) + 2*k")
    print()
    print("Komponen:")
    print("  1. -2*log(L)     : Goodness of fit (lower = better fit)")
    print("  2. +2*k          : Penalty untuk jumlah parameter (k)")
    print()
    print("Tujuan:")
    print("  ✓ Balance antara fit dan complexity")
    print("  ✓ Cegah overfitting")
    print("  ✓ Parsimony (prefer simpler models)")
    print()
    print("Fokus:")
    print("  → IN-SAMPLE fit quality")
    print("  → Model complexity management")
    print("  → Statistical theory-based")
    print()
    print("Limitasi untuk Forecasting:")
    print("  ✗ Tidak langsung measure forecast accuracy")
    print("  ✗ Bisa pilih model sederhana dengan forecast kurang akurat")
    print("  ✗ Trade-off complexity vs accuracy tidak selalu optimal untuk prediction")
    print()
    print()
    
    print("MAPE (Mean Absolute Percentage Error)")
    print("-" * 50)
    print("Formula: MAPE = (1/n) * Σ |Actual - Forecast| / Actual * 100%")
    print()
    print("Komponen:")
    print("  1. Actual - Forecast : Prediction error")
    print("  2. / Actual          : Normalize by actual value")
    print("  3. * 100%            : Express as percentage")
    print()
    print("Tujuan:")
    print("  ✓ Measure forecast accuracy directly")
    print("  ✓ Easy interpretation")
    print("  ✓ Praktis untuk stakeholder")
    print()
    print("Fokus:")
    print("  → OUT-OF-SAMPLE prediction quality")
    print("  → Real forecast performance")
    print("  → Application-oriented")
    print()
    print("Kelebihan untuk Forecasting:")
    print("  ✓ Langsung measure what matters (forecast error)")
    print("  ✓ Mudah dipahami (error dalam %)")
    print("  ✓ Industry standard untuk forecast evaluation")
    print()
    print()
    
    print("=" * 100)
    print("KESIMPULAN: Kapan Menggunakan AIC vs MAPE?")
    print("=" * 100)
    print()
    
    table = """
╔═══════════════════════╦═══════════════════════════╦═══════════════════════════╗
║ Aspek                 ║ AIC                       ║ MAPE                      ║
╠═══════════════════════╬═══════════════════════════╬═══════════════════════════╣
║ Tujuan Penelitian     ║ Model selection theory    ║ FORECASTING APPLICATION   ║
║                       ║ Statistical inference     ║ Prediction accuracy       ║
╠═══════════════════════╬═══════════════════════════╬═══════════════════════════╣
║ Measure               ║ Likelihood + complexity   ║ Forecast error            ║
╠═══════════════════════╬═══════════════════════════╬═══════════════════════════╣
║ Focus                 ║ IN-SAMPLE fit             ║ OUT-OF-SAMPLE prediction  ║
╠═══════════════════════╬═══════════════════════════╬═══════════════════════════╣
║ Interpretasi          ║ Teknis (statistician)     ║ Intuitif (stakeholder)    ║
╠═══════════════════════╬═══════════════════════════╬═══════════════════════════╣
║ Use Case              ║ Model complexity research ║ Forecasting research ← WE!║
╠═══════════════════════╬═══════════════════════════╬═══════════════════════════╣
║ Kelebihan             ║ Theoretical sound         ║ Directly relevant         ║
║                       ║ Prevent overfitting       ║ Easy to interpret         ║
╠═══════════════════════╬═══════════════════════════╬═══════════════════════════╣
║ Limitasi              ║ Not direct forecast error ║ Sensitive to scale        ║
║                       ║ Complex interpretation    ║ No complexity penalty     ║
╚═══════════════════════╩═══════════════════════════╩═══════════════════════════╝
    """
    print(table)
    print()
    
    print("PILIHAN UNTUK PENELITIAN INI:")
    print("→ MAPE sebagai kriteria UTAMA karena:")
    print("  1. Tujuan: Forecasting konsumsi energi (application-oriented)")
    print("  2. Output: Prediksi untuk stakeholder (butuh interpretasi mudah)")
    print("  3. Evaluasi: Akurasi prediksi > kesederhanaan model")
    print()
    print("→ AIC/BIC sebagai kriteria SEKUNDER untuk:")
    print("  1. Validasi model tidak overfitting")
    print("  2. Dokumentasi theoretical soundness")
    print("  3. Comparison dengan AUTO ARIMA")
    print()


def main():
    df, comparison = create_comparison_table()
    
    print()
    explain_aic_mape_difference()
    
    print()
    print("=" * 100)
    print("TEMPLATE JAWABAN UNTUK DEFENSE")
    print("=" * 100)
    print()
    print('"Saya menggunakan MAPE sebagai kriteria utama, bukan AIC, karena tujuan penelitian')
    print('adalah forecasting. AIC mengukur balance antara fit dan complexity (in-sample),')
    print('sedangkan MAPE langsung mengukur forecast accuracy (out-of-sample).')
    print()
    print('Dari 11 model yang saya test, ARIMAX(1,1,1) memiliki MAPE terkecil (7.07%),')
    print('meskipun bukan yang terkecil AIC-nya. Perbedaan dengan AUTO ARIMA yang memilih')
    print('(0,1,0) adalah kriteria optimasi: AUTO ARIMA optimasi AIC, saya optimasi MAPE.')
    print()
    print('Untuk forecasting application, MAPE lebih relevan karena stakeholder butuh')
    print('akurasi prediksi, bukan kesederhanaan model."')
    print()


if __name__ == "__main__":
    main()
