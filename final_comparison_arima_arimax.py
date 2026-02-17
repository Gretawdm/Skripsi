"""
PERBANDINGAN FINAL: ARIMA vs ARIMAX
Pakai order yang sama (3,2,1) dan data split yang sama (42 train, 18 test)
Untuk menunjukkan pengaruh variabel eksogen GDP
"""

import pandas as pd
import numpy as np
import mysql.connector
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
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

# Calculate MAPE
def calculate_mape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100

# Load data
def load_data():
    conn = get_db_connection()
    
    energy_query = "SELECT year, fossil_fuels_twh FROM energy_data WHERE year >= 1965 ORDER BY year"
    energy_df = pd.read_sql(energy_query, conn)
    
    gdp_query = "SELECT year, gdp FROM gdp_data WHERE year >= 1965 ORDER BY year"
    gdp_df = pd.read_sql(gdp_query, conn)
    
    conn.close()
    
    data = pd.merge(energy_df, gdp_df, on='year')
    return data

print("="*90)
print("PERBANDINGAN ARIMA vs ARIMAX - Final Analysis")
print("="*90)

# Load data
data = load_data()
print(f"\n✓ Data loaded: {len(data)} years ({data['year'].min()}-{data['year'].max()})")

# Split: 70% train, 30% test (sama seperti model aktif: 42 train, 18 test)
train_size = 42
train_data = data.head(train_size)
test_data = data.tail(len(data) - train_size)

print(f"\n✓ Training: {train_data['year'].min()}-{train_data['year'].max()} ({len(train_data)} years)")
print(f"✓ Testing:  {test_data['year'].min()}-{test_data['year'].max()} ({len(test_data)} years)")

y_train = train_data['fossil_fuels_twh'].values
y_test = test_data['fossil_fuels_twh'].values

X_train = train_data['gdp'].values.reshape(-1, 1)
X_test = test_data['gdp'].values.reshape(-1, 1)

# Model order (same as active model)
order = (3, 2, 1)

print(f"\n{'='*90}")
print(f"MODEL 1: ARIMA{order} - TANPA GDP")
print(f"{'='*90}")

try:
    # ARIMA without exogenous
    model_arima = SARIMAX(y_train, order=order, enforce_stationarity=False, enforce_invertibility=False)
    fitted_arima = model_arima.fit(disp=False)
    
    # Predict
    pred_arima = fitted_arima.forecast(steps=len(test_data))
    
    # Metrics
    mape_arima = calculate_mape(y_test, pred_arima)
    rmse_arima = np.sqrt(mean_squared_error(y_test, pred_arima))
    mae_arima = mean_absolute_error(y_test, pred_arima)
    r2_arima = r2_score(y_test, pred_arima)
    aic_arima = fitted_arima.aic
    
    print(f"✓ MAPE: {mape_arima:.2f}%")
    print(f"✓ RMSE: {rmse_arima:.2f} TWh")
    print(f"✓ MAE:  {mae_arima:.2f} TWh")
    print(f"✓ R²:   {r2_arima:.4f}")
    print(f"✓ AIC:  {aic_arima:.2f}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    mape_arima = rmse_arima = mae_arima = r2_arima = aic_arima = None

print(f"\n{'='*90}")
print(f"MODEL 2: ARIMAX{order} - DENGAN GDP")
print(f"{'='*90}")

try:
    # ARIMAX with GDP
    model_arimax = SARIMAX(y_train, exog=X_train, order=order, enforce_stationarity=False, enforce_invertibility=False)
    fitted_arimax = model_arimax.fit(disp=False)
    
    # Predict
    pred_arimax = fitted_arimax.forecast(steps=len(test_data), exog=X_test)
    
    # Metrics
    mape_arimax = calculate_mape(y_test, pred_arimax)
    rmse_arimax = np.sqrt(mean_squared_error(y_test, pred_arimax))
    mae_arimax = mean_absolute_error(y_test, pred_arimax)
    r2_arimax = r2_score(y_test, pred_arimax)
    aic_arimax = fitted_arimax.aic
    
    print(f"✓ MAPE: {mape_arimax:.2f}%")
    print(f"✓ RMSE: {rmse_arimax:.2f} TWh")
    print(f"✓ MAE:  {mae_arimax:.2f} TWh")
    print(f"✓ R²:   {r2_arimax:.4f}")
    print(f"✓ AIC:  {aic_arimax:.2f}")
    
    # GDP coefficient
    gdp_coef = fitted_arimax.params[-1]  # Last parameter is exog coefficient
    gdp_pvalue = fitted_arimax.pvalues[-1]
    print(f"✓ GDP Coefficient: {gdp_coef:.6f} (p-value: {gdp_pvalue:.4f})")
    
    if gdp_pvalue < 0.05:
        print(f"  → GDP adalah prediktor yang SIGNIFIKAN! (p < 0.05)")
    else:
        print(f"  → GDP tidak signifikan (p >= 0.05)")
    
except Exception as e:
    print(f"✗ Error: {e}")
    mape_arimax = rmse_arimax = mae_arimax = r2_arimax = aic_arimax = None

# Comparison
if mape_arima and mape_arimax:
    print(f"\n{'='*90}")
    print(f"PERBANDINGAN METRIK")
    print(f"{'='*90}")
    
    print(f"\n{'Metric':<20} {'ARIMA':<15} {'ARIMAX':<15} {'Improvement':<15}")
    print(f"{'-'*90}")
    
    metrics = [
        ('MAPE (%)', mape_arima, mape_arimax, 'lower'),
        ('RMSE (TWh)', rmse_arima, rmse_arimax, 'lower'),
        ('MAE (TWh)', mae_arima, mae_arimax, 'lower'),
        ('R²', r2_arima, r2_arimax, 'higher'),
        ('AIC', aic_arima, aic_arimax, 'lower')
    ]
    
    for metric_name, arima_val, arimax_val, better in metrics:
        if better == 'lower':
            improvement = ((arima_val - arimax_val) / arima_val) * 100
            symbol = "↓"
        else:
            improvement = ((arimax_val - arima_val) / abs(arima_val)) * 100 if arima_val != 0 else 0
            symbol = "↑"
        
        print(f"{metric_name:<20} {arima_val:<15.4f} {arimax_val:<15.4f} {symbol} {abs(improvement):<.2f}%")
    
    # Predictions table
    print(f"\n{'='*90}")
    print(f"PREDIKSI TEST SET")
    print(f"{'='*90}")
    
    print(f"\n{'Year':<8} {'Actual':<12} {'ARIMA':<12} {'Error %':<10} {'ARIMAX':<12} {'Error %':<10} {'Winner'}")
    print(f"{'-'*90}")
    
    arimax_wins = 0
    arima_wins = 0
    
    for i, year in enumerate(test_data['year'].values):
        actual = y_test[i]
        arima_pred = pred_arima[i]
        arimax_pred = pred_arimax[i]
        
        error_arima = abs((actual - arima_pred) / actual) * 100
        error_arimax = abs((actual - arimax_pred) / actual) * 100
        
        if error_arimax < error_arima:
            winner = "ARIMAX ✓"
            arimax_wins += 1
        else:
            winner = "ARIMA"
            arima_wins += 1
        
        print(f"{year:<8} {actual:<12.1f} {arima_pred:<12.1f} {error_arima:<10.2f} {arimax_pred:<12.1f} {error_arimax:<10.2f} {winner}")
    
    print(f"\nWin Rate: ARIMAX {arimax_wins}/{len(test_data)} ({arimax_wins/len(test_data)*100:.1f}%), ARIMA {arima_wins}/{len(test_data)} ({arima_wins/len(test_data)*100:.1f}%)")
    
    # Save results
    print(f"\n{'='*90}")
    print(f"SAVING RESULTS")
    print(f"{'='*90}")
    
    comparison_df = pd.DataFrame({
        'Model': ['ARIMA(3,2,1)', 'ARIMAX(3,2,1)+GDP'],
        'MAPE_%': [round(mape_arima, 2), round(mape_arimax, 2)],
        'RMSE_TWh': [round(rmse_arima, 2), round(rmse_arimax, 2)],
        'MAE_TWh': [round(mae_arima, 2), round(mae_arimax, 2)],
        'R²': [round(r2_arima, 4), round(r2_arimax, 4)],
        'AIC': [round(aic_arima, 2), round(aic_arimax, 2)]
    })
    comparison_df.to_csv('models/final_arima_vs_arimax.csv', index=False)
    print("✓ Saved: models/final_arima_vs_arimax.csv")
    
    predictions_df = pd.DataFrame({
        'Year': test_data['year'].values,
        'Actual_TWh': y_test,
        'ARIMA_Prediction': pred_arima,
        'ARIMA_Error_%': [abs((y_test[i]-pred_arima[i])/y_test[i]*100) for i in range(len(y_test))],
        'ARIMAX_Prediction': pred_arimax,
        'ARIMAX_Error_%': [abs((y_test[i]-pred_arimax[i])/y_test[i]*100) for i in range(len(y_test))]
    })
    predictions_df.to_csv('models/final_test_predictions.csv', index=False)
    print("✓ Saved: models/final_test_predictions.csv")
    
    # Summary
    print(f"\n{'='*90}")
    print(f"KESIMPULAN")
    print(f"{'='*90}")
    
    mape_improvement = ((mape_arima - mape_arimax) / mape_arima) * 100
    
    print(f"\n1. MAPE ARIMA  (tanpa GDP): {mape_arima:.2f}%")
    print(f"2. MAPE ARIMAX (dengan GDP): {mape_arimax:.2f}%")
    print(f"3. IMPROVEMENT: {mape_improvement:.2f}%")
    
    if mape_improvement > 0:
        print(f"\n✓ Dengan menambahkan GDP sebagai variabel eksogen,")
        print(f"  akurasi prediksi MENINGKAT {mape_improvement:.2f}%!")
        print(f"\n✓ ARIMAX menang di {arimax_wins}/{len(test_data)} tahun test ({arimax_wins/len(test_data)*100:.1f}%)")
    else:
        print(f"\n⚠ Warning: ARIMAX tidak lebih baik dari ARIMA pada data ini")
        print(f"  Possible reasons: data size, anomalies, or weak GDP correlation")
    
    print(f"\n{'='*90}")
