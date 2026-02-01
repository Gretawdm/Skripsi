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

def predict_energy_service(scenario, years):
    """
    Predict energy consumption dengan ARIMAX model
    
    Args:
        scenario: 'optimis', 'moderat', atau 'pesimistis'
        years: jumlah tahun prediksi ke depan
        
    Returns:
        list: forecast values dalam TWh (nilai asli, TIDAK dalam billion)
    """
    # Check if model file has been modified (untuk detect perubahan model aktif)
    current_mtime = os.path.getmtime(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
    
    # Reload model jika file berubah atau belum di-load
    if _model_cache['model'] is None or _model_cache['mtime'] != current_mtime:
        # Try to load as pickle first (new format), fallback to joblib (old format)
        try:
            with open(MODEL_PATH, 'rb') as f:
                model_info = pickle.load(f)
                if isinstance(model_info, dict) and 'model' in model_info:
                    model = model_info['model']
                else:
                    # Old format - direct model object
                    model = model_info
        except:
            # Fallback to joblib
            model = joblib.load(MODEL_PATH)
        
        # Update cache
        _model_cache['model'] = model
        _model_cache['mtime'] = current_mtime
        print(f"✓ Model loaded/reloaded from {MODEL_PATH}")
    else:
        model = _model_cache['model']
        print(f"✓ Using cached model")

    # Ambil GDP terakhir dari data training (dalam nilai asli)
    last_gdp = model.data.orig_exog['gdp'].iloc[-1]

    # Growth rate sesuai skenario
    if scenario == "optimis":
        growth = 0.06
    elif scenario == "moderat":
        growth = 0.05
    else:  # pesimistis
        growth = 0.03

    # Generate future GDP (dalam nilai asli, TIDAK di-scale)
    future_gdp = []
    current = last_gdp

    for _ in range(years):
        current *= (1 + growth)
        future_gdp.append(current)

    # Buat dataframe dengan kolom 'gdp' (lowercase, sesuai training)
    future_gdp_df = pd.DataFrame({"gdp": future_gdp})

    # Get forecast with confidence intervals (95%)
    forecast_result = model.get_forecast(steps=years, exog=future_gdp_df)
    forecast = forecast_result.predicted_mean
    confidence_intervals = forecast_result.conf_int(alpha=0.05)  # 95% confidence interval

    # Return forecast values with confidence intervals
    return {
        'predictions': forecast.round(2).tolist(),
        'lower_bounds': confidence_intervals.iloc[:, 0].round(2).tolist(),
        'upper_bounds': confidence_intervals.iloc[:, 1].round(2).tolist()
    }
