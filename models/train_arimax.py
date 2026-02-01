"""
LEGACY TRAINING SCRIPT - FOR DEVELOPMENT/EXPERIMENTATION ONLY
===============================================================

⚠️ WARNING: File ini TIDAK dipakai oleh web application!

Gunakan: services/train_service.py untuk production training via web app

File ini adalah script standalone untuk:
- Eksperimen dan development
- Testing parameter ARIMAX manual
- Generating plots untuk analisis
- Running training secara offline

PERBEDAAN dengan train_service.py:
- train_arimax.py: Standalone script, hardcoded paths, auto_arima, visualisasi
- train_service.py: Production service, dynamic paths, web-ready, API integration

CARA PAKAI file ini:
$ cd models
$ python train_arimax.py

Untuk training via web app, gunakan halaman "Update Model" di admin panel.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from pmdarima import auto_arima
import joblib
import os

# ===============================
# 1. LOAD DATA
# ===============================
energy = pd.read_csv('../data/fossil-fuel-primary-energy.csv')

gdp = pd.read_csv(
    '../data/indonesia_gdp_only.csv',

    skiprows=3
)

# ===============================
# 2. PREPROCESS GDP (WORLD BANK)
# ===============================
gdp = gdp[gdp['Country Name'] == 'Indonesia']

gdp = gdp.drop(columns=[
    'Country Name',
    'Country Code',
    'Indicator Name',
    'Indicator Code',
    'Unnamed: 69'
])

gdp = gdp.melt(
    var_name='Year',
    value_name='GDP'
)

gdp['Year'] = gdp['Year'].astype(int)
gdp['GDP'] = pd.to_numeric(gdp['GDP'], errors='coerce')
gdp.dropna(inplace=True)

# ===============================
# 3. PREPROCESS ENERGY
# ===============================
energy = energy[['Year', 'Fossil fuels (TWh)']]
energy.rename(columns={'Fossil fuels (TWh)': 'Energy'}, inplace=True)

# ===============================
# 4. MERGE DATA
# ===============================
data = pd.merge(energy, gdp, on='Year')

data.set_index('Year', inplace=True)
data.index = pd.PeriodIndex(data.index, freq='Y')

print("Data final:")
print(data.head())

# ===============================
# 5. TRAIN-TEST SPLIT
# ===============================
train_size = int(len(data) * 0.8)

train = data.iloc[:train_size]
test = data.iloc[train_size:]

y_train = train['Energy']
y_test = test['Energy']

x_train = train[['GDP']].copy()
x_test = test[['GDP']].copy()

# ===============================
# 6. SCALE EXOGENOUS (GDP)
# ===============================
scaler = StandardScaler()
x_train.loc[:, 'GDP'] = scaler.fit_transform(x_train[['GDP']])
x_test.loc[:, 'GDP'] = scaler.transform(x_test[['GDP']])

# ===============================
# 7. AUTO ARIMA (ARIMAX)
# ===============================
auto_model = auto_arima(
    y_train,
    exogenous=x_train,
    start_p=0,
    start_q=0,
    max_p=3,
    max_q=3,
    d=1,
    seasonal=False,
    trace=True,
    error_action='ignore',
    suppress_warnings=True,
    stepwise=True
)

best_order = auto_model.order
print("Best ARIMAX order:", best_order)

# ===============================
# 8. TRAIN FINAL ARIMAX MODEL
# ===============================
model = SARIMAX(
    y_train,
    exog=x_train,
    order=best_order,
    enforce_stationarity=False,
    enforce_invertibility=False
)

model_fit = model.fit(disp=False)
print(model_fit.summary())

# ===============================
# 9. PREDICTION (TEST SET)
# ===============================
pred = model_fit.forecast(
    steps=len(test),
    exog=x_test
)
pred.index = test.index

# ===============================
# 10. EVALUATION (MAE, RMSE, MAPE)
# ===============================
def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

mae = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))
mape = mean_absolute_percentage_error(y_test, pred)

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"MAPE : {mape:.2f}%")

# ===============================
# 11. FORECAST UNTIL 2030
# ===============================
last_year = data.index[-1].year
future_years = list(range(last_year + 1, 2031))

last_gdp = data['GDP'].iloc[-1]
gdp_growth_rate = 0.05  # asumsi 5% per tahun

future_gdp = []
current_gdp = last_gdp

for _ in future_years:
    current_gdp *= (1 + gdp_growth_rate)
    future_gdp.append(current_gdp)

future_gdp = pd.DataFrame(
    {'GDP': future_gdp},
    index=pd.PeriodIndex(future_years, freq='Y')
)

future_gdp.loc[:, 'GDP'] = scaler.transform(future_gdp[['GDP']])

future_pred = model_fit.forecast(
    steps=len(future_gdp),
    exog=future_gdp
)
future_pred.index = future_gdp.index

print("\nForecast Energi Fosil sampai 2030:")
print(future_pred)

# ===============================
# 12. VISUALIZATION
# ===============================
plt.figure(figsize=(10,5))
plt.plot(data.index.to_timestamp(), data['Energy'], label='Actual')
plt.plot(pred.index.to_timestamp(), pred, label='Test Prediction', color='orange')
plt.plot(future_pred.index.to_timestamp(), future_pred, label='Forecast 2030', color='red')
plt.legend()
plt.title('ARIMAX Forecast Konsumsi Energi Fosil Indonesia sampai 2030')
plt.xlabel('Year')
plt.ylabel('Energy (TWh)')
plt.tight_layout()
plt.show()

# ===============================
# 13. SAVE MODEL
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "arimax_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "gdp_scaler.pkl")

joblib.dump(model_fit, MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)

print("✅ Model & scaler tersimpan di folder models/")
print("📦", MODEL_PATH)
print("📦", SCALER_PATH)
