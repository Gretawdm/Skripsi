from pyexpat import model
import joblib
import pandas as pd
import os
import pickle

MODEL_PATH = "models/arimax_model.pkl"

# Cache untuk menghindari reload berulang dalam satu request
_model_cache = {
    'model': None,
    'mtime': None
}

def predict_energy_service(scenario, years, baseline=None):

    current_mtime = os.path.getmtime(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
    
    if _model_cache['model'] is None or _model_cache['mtime'] != current_mtime:
        try:
            with open(MODEL_PATH, 'rb') as f:
                model_info = pickle.load(f)
                if isinstance(model_info, dict) and 'model' in model_info:
                    model = model_info['model']
                else:
                    model = model_info
        except:
            model = joblib.load(MODEL_PATH)

        _model_cache['model'] = model
        _model_cache['mtime'] = current_mtime
        print(f"✓ Model loaded/reloaded from {MODEL_PATH}")
    else:
        model = _model_cache['model']
        print("✓ Using cached model")

    # Ambil GDP terakhir dari data training
    last_gdp = model.data.orig_exog['gdp'].iloc[-1]

    # =========================
    # Growth Logic (FIXED)
    # =========================
    if baseline is None:
        # fallback default
        if scenario == "optimis":
            growth = 0.06
        elif scenario == "moderat":
            growth = 0.05
        else:
            growth = 0.03
    else:
        if scenario == "optimis":
            growth = baseline + 0.02
        elif scenario == "moderat":
            growth = baseline
        else:
            growth = baseline - 0.02

    # Generate future GDP
    future_gdp = []
    current = last_gdp

    for _ in range(years):
        current *= (1 + growth)
        future_gdp.append(current)

    future_gdp_df = pd.DataFrame({"gdp": future_gdp})

    forecast_result = model.get_forecast(steps=years, exog=future_gdp_df)
    forecast = forecast_result.predicted_mean
    confidence_intervals = forecast_result.conf_int(alpha=0.05)
    last_actual_year = model.data.row_labels[-1]
    last_actual_value = model.data.orig_endog.iloc[-1]  

    return {
        'predictions': forecast.round(2).tolist(),
        'lower_bounds': confidence_intervals.iloc[:, 0].round(2).tolist(),
        'upper_bounds': confidence_intervals.iloc[:, 1].round(2).tolist(),
        'growth_used': round(growth * 100, 2),
        "last_actual_year": int(last_actual_year),
        "last_actual_value": round(float(last_actual_value), 2)
    }
