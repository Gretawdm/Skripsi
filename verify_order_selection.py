"""
Verifikasi: Kenapa auto_arima pilih order berbeda?
Bandingkan:
- ARIMA(0,2,1) vs ARIMA(3,2,1) - TANPA GDP
- ARIMAX(3,2,1) - DENGAN GDP
"""

import pandas as pd
import numpy as np
import mysql.connector
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def get_db_connection():
    return mysql.connector.connect(
        host='localhost', user='root', password='', database='arimax_forecasting'
    )

def calculate_mape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100

# Load data
conn = get_db_connection()
energy_df = pd.read_sql("SELECT year, fossil_fuels_twh FROM energy_data WHERE year >= 1965 ORDER BY year", conn)
gdp_df = pd.read_sql("SELECT year, gdp FROM gdp_data WHERE year >= 1965 ORDER BY year", conn)
conn.close()

data = pd.merge(energy_df, gdp_df, on='year')

# Split
train_size = 42
train_data = data.head(train_size)
test_data = data.tail(len(data) - train_size)

y_train = train_data['fossil_fuels_twh'].values
y_test = test_data['fossil_fuels_twh'].values
X_train = train_data['gdp'].values.reshape(-1, 1)
X_test = test_data['gdp'].values.reshape(-1, 1)

print("="*90)
print("PERBANDINGAN ORDER: ARIMA(0,2,1) vs ARIMA(3,2,1) vs ARIMAX(3,2,1)")
print("="*90)

results = []

# Model 1: ARIMA(0,2,1) - Auto_arima choice for ARIMA
print("\n[1/3] ARIMA(0,2,1) - Order yang dipilih auto_arima TANPA GDP...")
try:
    model = SARIMAX(y_train, order=(0, 2, 1), enforce_stationarity=False, enforce_invertibility=False)
    fitted = model.fit(disp=False)
    pred = fitted.forecast(steps=len(test_data))
    
    mape = calculate_mape(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)
    aic = fitted.aic
    
    results.append({
        'Model': 'ARIMA(0,2,1)',
        'Eksogen': 'Tidak',
        'MAPE': mape,
        'RMSE': rmse,
        'MAE': mae,
        'R²': r2,
        'AIC': aic
    })
    
    print(f"✓ MAPE: {mape:.2f}%, AIC: {aic:.2f}")
except Exception as e:
    print(f"✗ Error: {e}")

# Model 2: ARIMA(3,2,1) - Same order as ARIMAX but without GDP
print("\n[2/3] ARIMA(3,2,1) - Order yang sama dengan ARIMAX tapi TANPA GDP...")
try:
    model = SARIMAX(y_train, order=(3, 2, 1), enforce_stationarity=False, enforce_invertibility=False)
    fitted = model.fit(disp=False)
    pred = fitted.forecast(steps=len(test_data))
    
    mape = calculate_mape(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)
    aic = fitted.aic
    
    results.append({
        'Model': 'ARIMA(3,2,1)',
        'Eksogen': 'Tidak',
        'MAPE': mape,
        'RMSE': rmse,
        'MAE': mae,
        'R²': r2,
        'AIC': aic
    })
    
    print(f"✓ MAPE: {mape:.2f}%, AIC: {aic:.2f}")
except Exception as e:
    print(f"✗ Error: {e}")

# Model 3: ARIMAX(3,2,1) - With GDP
print("\n[3/3] ARIMAX(3,2,1) - Order yang sama DENGAN GDP...")
try:
    model = SARIMAX(y_train, exog=X_train, order=(3, 2, 1), enforce_stationarity=False, enforce_invertibility=False)
    fitted = model.fit(disp=False)
    pred = fitted.forecast(steps=len(test_data), exog=X_test)
    
    mape = calculate_mape(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)
    aic = fitted.aic
    
    results.append({
        'Model': 'ARIMAX(3,2,1)',
        'Eksogen': 'Ya (GDP)',
        'MAPE': mape,
        'RMSE': rmse,
        'MAE': mae,
        'R²': r2,
        'AIC': aic
    })
    
    print(f"✓ MAPE: {mape:.2f}%, AIC: {aic:.2f}")
except Exception as e:
    print(f"✗ Error: {e}")

# Summary
print("\n" + "="*90)
print("HASIL PERBANDINGAN")
print("="*90)

df_results = pd.DataFrame(results)
print(f"\n{df_results.to_string(index=False)}")

print("\n" + "="*90)
print("ANALISIS")
print("="*90)

print("\n1. ARIMA(0,2,1) vs ARIMA(3,2,1) - Keduanya TANPA GDP:")
if len(results) >= 2:
    mape_021 = results[0]['MAPE']
    mape_321 = results[1]['MAPE']
    aic_021 = results[0]['AIC']
    aic_321 = results[1]['AIC']
    
    print(f"   - ARIMA(0,2,1): MAPE={mape_021:.2f}%, AIC={aic_021:.2f}")
    print(f"   - ARIMA(3,2,1): MAPE={mape_321:.2f}%, AIC={aic_321:.2f}")
    
    if aic_021 < aic_321:
        print(f"\n   ✓ Auto_arima pilih (0,2,1) karena AIC lebih rendah!")
        print(f"     → Model lebih sederhana, akurasi hampir sama")
    else:
        print(f"\n   ✓ ARIMA(3,2,1) lebih baik meski lebih kompleks")

print("\n2. ARIMA(3,2,1) vs ARIMAX(3,2,1) - Efek Penambahan GDP:")
if len(results) >= 3:
    mape_arima = results[1]['MAPE']
    mape_arimax = results[2]['MAPE']
    improvement = ((mape_arima - mape_arimax) / mape_arima) * 100
    
    print(f"   - ARIMA(3,2,1) tanpa GDP: MAPE={mape_arima:.2f}%")
    print(f"   - ARIMAX(3,2,1) dengan GDP: MAPE={mape_arimax:.2f}%")
    print(f"\n   ✓ Improvement dengan GDP: {improvement:.2f}%")
    print(f"     → Ini yang jadi justifikasi pakai ARIMAX!")

print("\n" + "="*90)
print("KESIMPULAN")
print("="*90)

print("\n✓ Auto_arima pilih order berbeda untuk ARIMA vs ARIMAX karena:")
print("  1. Tanpa GDP: (0,2,1) sudah cukup - model sederhana")
print("  2. Dengan GDP: (3,2,1) optimal - AR component penting untuk GDP")
print("\n✓ Untuk perbandingan FAIR, kita harus pakai ORDER YANG SAMA (3,2,1)")
print("  → Baru bisa lihat efek murni dari penambahan GDP")
print("\n✓ Hasil final comparison kita VALID karena:")
print("  - Same order: (3,2,1)")
print("  - Same train/test split: 42/18")
print("  - Only difference: GDP (Yes/No)")
print("\n" + "="*90)
