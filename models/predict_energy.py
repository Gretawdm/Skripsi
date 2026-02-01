import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "arimax_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "gdp_scaler.pkl")


def predict_energy(scenario: str, years: int):
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    growth_rates = {
        "optimis": 0.06,
        "moderat": 0.05,
        "pesimistis": 0.03
    }

    growth = growth_rates.get(scenario, 0.05)

    last_gdp = model.data.orig_exog.iloc[-1, 0]
    future_gdp = []

    gdp_now = last_gdp
    for _ in range(years):
        gdp_now *= (1 + growth)
        future_gdp.append(gdp_now)

    future_exog = pd.DataFrame({'GDP': future_gdp})
    future_exog['GDP'] = scaler.transform(future_exog[['GDP']])

    forecast = model.forecast(steps=years, exog=future_exog)

    return forecast.tolist()
