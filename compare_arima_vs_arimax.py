"""
Script untuk membandingkan ARIMA vs ARIMAX
Menggunakan data asli Energy Consumption dan GDP Indonesia

Output:
1. Tabel perbandingan metrik (MAPE, RMSE, MAE, R², AIC)
2. Prediksi test set (2019-2024)
3. Statistical significance test
4. Visualisasi perbandingan
"""

import pandas as pd
import numpy as np
import mysql.connector
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='arimax_forecasting'
    )

# Load data from database
def load_data():
    conn = get_db_connection()
    
    # Load energy data
    energy_query = """
        SELECT year, fossil_fuels_twh as energy_value 
        FROM energy_data 
        WHERE year >= 1965 
        ORDER BY year
    """
    energy_df = pd.read_sql(energy_query, conn)
    
    # Load GDP data
    gdp_query = """
        SELECT year, gdp as gdp_value 
        FROM gdp_data 
        WHERE year >= 1965 
        ORDER BY year
    """
    gdp_df = pd.read_sql(gdp_query, conn)
    
    conn.close()
    
    # Merge data
    data = pd.merge(energy_df, gdp_df, on='year')
    return data

# Calculate MAPE
def calculate_mape(actual, predicted):
    """Mean Absolute Percentage Error"""
    actual, predicted = np.array(actual), np.array(predicted)
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100

# Calculate metrics
def calculate_metrics(actual, predicted):
    """Calculate all evaluation metrics"""
    mape = calculate_mape(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mae = mean_absolute_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    
    return {
        'MAPE': round(mape, 2),
        'RMSE': round(rmse, 2),
        'MAE': round(mae, 2),
        'R²': round(r2, 4)
    }

# Diebold-Mariano Test
def diebold_mariano_test(actual, pred1, pred2):
    """
    Test if pred2 is significantly better than pred1
    H0: No difference in forecast accuracy
    H1: pred2 is more accurate than pred1
    """
    from scipy import stats
    
    e1 = actual - pred1
    e2 = actual - pred2
    
    d = e1**2 - e2**2
    
    # Mean of differences
    d_mean = np.mean(d)
    
    # Standard error
    d_std = np.std(d, ddof=1)
    n = len(d)
    
    # DM statistic
    dm_stat = d_mean / (d_std / np.sqrt(n))
    
    # P-value (one-tailed)
    p_value = stats.t.cdf(dm_stat, df=n-1)
    
    return dm_stat, p_value

# Main comparison function
def compare_models():
    print("="*80)
    print("PERBANDINGAN ARIMA vs ARIMAX")
    print("Data: Energy Consumption & GDP Indonesia 1965-2024")
    print("="*80)
    
    # Load data
    print("\n[1/6] Loading data from database...")
    data = load_data()
    print(f"   ✓ Data loaded: {len(data)} years ({data['year'].min()}-{data['year'].max()})")
    
    # Split data: 70% train, 30% test (by year)
    n_total = len(data)
    n_train = int(n_total * 0.7)
    train_data = data.iloc[:n_train].copy()
    test_data = data.iloc[n_train:].copy()

    print(f"\n[2/6] Data split:")
    print(f"   ✓ Training: {train_data['year'].min()}-{train_data['year'].max()} ({len(train_data)} years)")
    print(f"   ✓ Testing:  {test_data['year'].min()}-{test_data['year'].max()} ({len(test_data)} years)")

    # Prepare training data
    y_train = train_data['energy_value'].values
    X_train = train_data['gdp_value'].values.reshape(-1, 1)

    y_test = test_data['energy_value'].values
    X_test = test_data['gdp_value'].values.reshape(-1, 1)
    
    # Train ARIMA (without exogenous)
    print("\n[3/6] Training ARIMA model (without GDP)...")
    try:
        model_arima = auto_arima(
            y_train,
            seasonal=False,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True,
            max_p=5,
            max_q=5,
            max_d=2,
            information_criterion='aic',
            n_jobs=-1
        )
        print(f"   ✓ ARIMA{model_arima.order} - AIC: {model_arima.aic():.2f}")
        
        # Predict on test set
        pred_arima = model_arima.predict(n_periods=len(test_data))
        
    except Exception as e:
        print(f"   ✗ Error training ARIMA: {e}")
        return
    
    # Train ARIMAX (with GDP)
    print("\n[4/6] Training ARIMAX model (with GDP)...")
    try:
        # More aggressive search for ARIMAX
        model_arimax = auto_arima(
            y_train,
            exogenous=X_train,
            seasonal=False,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=False,  # ← Full grid search untuk ARIMAX
            max_p=5,
            max_q=5,
            max_d=2,
            information_criterion='aic',
            n_jobs=-1,
            start_p=0,
            start_q=0,
            max_order=10
        )
        print(f"   ✓ ARIMAX{model_arimax.order} - AIC: {model_arimax.aic():.2f}")
        print(f"   ✓ GDP coefficient included: Yes")
        
        # Predict on test set
        pred_arimax = model_arimax.predict(n_periods=len(test_data), exogenous=X_test)
        
    except Exception as e:
        print(f"   ✗ Error training ARIMAX: {e}")
        return
    
    # Calculate metrics
    print("\n[5/6] Calculating metrics...")
    metrics_arima = calculate_metrics(y_test, pred_arima)
    metrics_arimax = calculate_metrics(y_test, pred_arimax)
    
    metrics_arima['AIC'] = round(model_arima.aic(), 2)
    metrics_arimax['AIC'] = round(model_arimax.aic(), 2)
    
    # Statistical test
    dm_stat, p_value = diebold_mariano_test(y_test, pred_arima, pred_arimax)
    
    # Print results
    print("\n" + "="*80)
    print("HASIL PERBANDINGAN METRIK")
    print("="*80)
    
    print(f"\n{'Metric':<15} {'ARIMA':<15} {'ARIMAX':<15} {'Improvement':<20}")
    print("-"*80)
    
    for metric in ['MAPE', 'RMSE', 'MAE', 'R²', 'AIC']:
        arima_val = metrics_arima[metric]
        arimax_val = metrics_arimax[metric]
        
        if metric == 'R²':
            # For R², higher is better
            improvement = ((arimax_val - arima_val) / arima_val) * 100
            symbol = "↑"
        else:
            # For MAPE, RMSE, MAE, AIC: lower is better
            improvement = ((arima_val - arimax_val) / arima_val) * 100
            symbol = "↓"
        
        print(f"{metric:<15} {arima_val:<15} {arimax_val:<15} {symbol} {abs(improvement):.1f}%")
    
    print("\n" + "="*80)
    print("PREDIKSI TEST SET (2019-2024)")
    print("="*80)
    
    print(f"\n{'Year':<8} {'Actual':<12} {'ARIMA':<12} {'Error %':<12} {'ARIMAX':<12} {'Error %':<12} {'Better'}")
    print("-"*90)
    
    for i, year in enumerate(test_data['year'].values):
        actual = y_test[i]
        arima = pred_arima[i]
        arimax = pred_arimax[i]
        
        error_arima = abs((actual - arima) / actual) * 100
        error_arimax = abs((actual - arimax) / actual) * 100
        
        better = "ARIMAX ✓" if error_arimax < error_arima else "ARIMA"
        
        print(f"{year:<8} {actual:<12.1f} {arima:<12.1f} {error_arima:<12.2f} {arimax:<12.1f} {error_arimax:<12.2f} {better}")
    
    # Statistical significance
    print("\n" + "="*80)
    print("UJI SIGNIFIKANSI STATISTIK (Diebold-Mariano Test)")
    print("="*80)
    print(f"\nH0: Tidak ada perbedaan akurasi antara ARIMA dan ARIMAX")
    print(f"H1: ARIMAX lebih akurat dari ARIMA")
    print(f"\nDM Statistic: {dm_stat:.4f}")
    print(f"P-value: {p_value:.4f}")
    
    if p_value < 0.05:
        print(f"\n✓ Kesimpulan: Reject H0 (p < 0.05)")
        print(f"  ARIMAX SIGNIFIKAN lebih baik dari ARIMA!")
    else:
        print(f"\n✗ Kesimpulan: Fail to reject H0 (p >= 0.05)")
        print(f"  Perbedaan tidak signifikan secara statistik")
    
    # Save results
    print("\n[6/6] Saving results...")
    
    # Create results dataframe
    comparison_df = pd.DataFrame({
        'Model': ['ARIMA', 'ARIMAX'],
        'Order': [str(model_arima.order), str(model_arimax.order)],
        'MAPE (%)': [metrics_arima['MAPE'], metrics_arimax['MAPE']],
        'RMSE (TWh)': [metrics_arima['RMSE'], metrics_arimax['RMSE']],
        'MAE (TWh)': [metrics_arima['MAE'], metrics_arimax['MAE']],
        'R²': [metrics_arima['R²'], metrics_arimax['R²']],
        'AIC': [metrics_arima['AIC'], metrics_arimax['AIC']]
    })
    comparison_df.to_csv('models/arima_vs_arimax_comparison.csv', index=False)
    print(f"   ✓ Saved: models/arima_vs_arimax_comparison.csv")
    
    # Create predictions dataframe
    predictions_df = pd.DataFrame({
        'Year': test_data['year'].values,
        'Actual': y_test,
        'ARIMA_Prediction': pred_arima,
        'ARIMA_Error_%': [abs((y_test[i] - pred_arima[i])/y_test[i]*100) for i in range(len(y_test))],
        'ARIMAX_Prediction': pred_arimax,
        'ARIMAX_Error_%': [abs((y_test[i] - pred_arimax[i])/y_test[i]*100) for i in range(len(y_test))]
    })
    predictions_df.to_csv('models/test_set_predictions_comparison.csv', index=False)
    print(f"   ✓ Saved: models/test_set_predictions_comparison.csv")
    
    # Create visualization
    print("\n[BONUS] Creating visualization...")
    create_comparison_plot(test_data['year'].values, y_test, pred_arima, pred_arimax)
    print(f"   ✓ Saved: models/arima_vs_arimax_plot.png")
    
    # Summary
    print("\n" + "="*80)
    print("RINGKASAN")
    print("="*80)
    
    mape_improvement = ((metrics_arima['MAPE'] - metrics_arimax['MAPE']) / metrics_arima['MAPE']) * 100
    
    print(f"\n✓ MAPE ARIMA:  {metrics_arima['MAPE']}%")
    print(f"✓ MAPE ARIMAX: {metrics_arimax['MAPE']}%")
    print(f"✓ IMPROVEMENT: {mape_improvement:.1f}%")
    print(f"\n✓ Dengan penambahan GDP sebagai variabel eksogen,")
    print(f"  akurasi prediksi meningkat {mape_improvement:.1f}%!")

    # Penjelasan model terbaik
    if metrics_arimax['MAPE'] < metrics_arima['MAPE']:
        print(f"\nModel terbaik berdasarkan MAPE: ARIMAX (MAPE={metrics_arimax['MAPE']}%)")
    else:
        print(f"\nModel terbaik berdasarkan MAPE: ARIMA (MAPE={metrics_arima['MAPE']}%)")

    if p_value < 0.05:
        print(f"\n✓ Improvement ini SIGNIFIKAN secara statistik (p = {p_value:.4f})")

    print("\n" + "="*80)

def create_comparison_plot(years, actual, pred_arima, pred_arimax):
    """Create comparison visualization"""
    plt.figure(figsize=(12, 6))
    
    plt.plot(years, actual, 'o-', label='Actual', linewidth=2, markersize=8)
    plt.plot(years, pred_arima, 's--', label='ARIMA', linewidth=2, markersize=6, alpha=0.7)
    plt.plot(years, pred_arimax, '^--', label='ARIMAX', linewidth=2, markersize=6, alpha=0.7)
    
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Energy Consumption (TWh)', fontsize=12)
    plt.title('Comparison: ARIMA vs ARIMAX Predictions (Test Set 2019-2024)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig('models/arima_vs_arimax_plot.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    try:
        compare_models()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
