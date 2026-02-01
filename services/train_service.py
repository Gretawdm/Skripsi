import pandas as pd
import joblib
import os
import numpy as np
import time
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pmdarima import auto_arima
from services.database_service import save_training_history

def retrain_model(train_test_split=0.8, order_mode='auto', manual_order=None):
    """
    Retrain ARIMAX model dengan data terbaru
    
    Args:
        train_test_split (float): Ratio untuk train data (0.0-1.0). Default 0.8 (80% training, 20% testing)
        order_mode (str): 'auto' untuk auto_arima atau 'manual' untuk set manual. Default 'auto'
        manual_order (tuple): (p,d,q) jika order_mode='manual'. Default None
    """
    try:
        # Start timer
        start_time = time.time()
        
        # Check if files exist
        if not os.path.exists("data/raw/energy.csv") or not os.path.exists("data/raw/gdp.csv"):
            return {
                "status": "error",
                "message": "File data tidak ditemukan. Lakukan fetch/upload data terlebih dahulu."
            }
        
        energy = pd.read_csv("data/raw/energy.csv")
        gdp = pd.read_csv("data/raw/gdp.csv")
        
        # Identifikasi kolom tahun
        energy_year_col = "Year" if "Year" in energy.columns else "year"
        gdp_year_col = "year" if "year" in gdp.columns else "Year"
        
        # Identifikasi kolom nilai energi
        energy_value_col = None
        for col in ["fossil_fuels__twh", "fossil_fuels", "value", "Energy"]:
            if col in energy.columns:
                energy_value_col = col
                break
        
        if not energy_value_col:
            return {
                "status": "error",
                "message": f"Kolom nilai energi tidak ditemukan. Kolom tersedia: {list(energy.columns)}"
            }
        
        # Validasi kolom GDP
        if "gdp" not in gdp.columns and "GDP" not in gdp.columns:
            return {
                "status": "error",
                "message": f"Kolom GDP tidak ditemukan. Kolom tersedia: {list(gdp.columns)}"
            }
        
        gdp_value_col = "gdp" if "gdp" in gdp.columns else "GDP"
        
        # Standardize column names untuk merge
        energy_clean = energy[[energy_year_col, energy_value_col]].copy()
        energy_clean.columns = ["year", "energy"]
        
        gdp_clean = gdp[[gdp_year_col, gdp_value_col]].copy()
        gdp_clean.columns = ["year", "gdp"]
        
        # Remove duplicates dan sort
        energy_clean = energy_clean.drop_duplicates(subset=["year"]).sort_values("year")
        gdp_clean = gdp_clean.drop_duplicates(subset=["year"]).sort_values("year")
        
        # INNER JOIN - ambil hanya tahun yang ada di kedua dataset
        df = pd.merge(energy_clean, gdp_clean, on="year", how="inner")
        
        # Validasi: harus ada minimal 10 data points untuk training
        if len(df) < 10:
            return {
                "status": "error",
                "message": f"Data tidak cukup untuk training. Hanya {len(df)} tahun yang cocok. Minimal 10 tahun diperlukan.",
                "details": {
                    "energy_years": f"{energy_clean['year'].min()}-{energy_clean['year'].max()} ({len(energy_clean)} records)",
                    "gdp_years": f"{gdp_clean['year'].min()}-{gdp_clean['year'].max()} ({len(gdp_clean)} records)",
                    "matched_years": f"{df['year'].min()}-{df['year'].max()} ({len(df)} records)"
                }
            }
        
        # Drop missing values
        df = df.dropna()
        
        # Prepare data for ARIMAX
        y = df["energy"]
        exog = df[["gdp"]]
        
        # Train-test split untuk evaluasi (gunakan parameter dari user)
        train_size = int(len(df) * train_test_split)
        y_train = y.iloc[:train_size]
        y_test = y.iloc[train_size:]
        exog_train = exog.iloc[:train_size]
        exog_test = exog.iloc[train_size:]
        
        # Determine ARIMA order based on mode
        if order_mode == 'auto':
            print("Using AUTO ARIMA to find best parameters...")
            # Auto ARIMA untuk mencari parameter optimal
            auto_model = auto_arima(
                y_train,
                exogenous=exog_train,
                start_p=1, start_q=1,
                max_p=5, max_q=10,
                d=None,  # Let auto_arima determine d
                seasonal=False,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore',
                trace=True  # Print progress
            )
            best_order = auto_model.order
            print(f"Auto ARIMA found optimal order: {best_order}")
        else:
            # Manual order from user
            if manual_order and isinstance(manual_order, (tuple, list)) and len(manual_order) == 3:
                best_order = tuple(manual_order)
                print(f"Using manual ARIMAX order: {best_order}")
            else:
                # Default fallback
                best_order = (3, 2, 6)
                print(f"Using default ARIMAX order: {best_order}")
        
        print(f"Training with {len(df)} records (train: {train_size}, test: {len(y_test)})")
        
        # Train ARIMAX model dengan parameter optimal
        model = SARIMAX(
            y_train,
            exog=exog_train,
            order=best_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        result = model.fit(disp=False)
        
        # Predict on test set untuk evaluasi
        predictions = result.forecast(steps=len(y_test), exog=exog_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
        
        # R-squared
        ss_res = np.sum((y_test - predictions) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        # Retrain dengan semua data untuk final model
        final_model = SARIMAX(
            y,
            exog=exog,
            order=best_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        final_result = final_model.fit(disp=False)
        
        # Save final model with test data for dashboard
        os.makedirs("models", exist_ok=True)
        
        # Save model object
        joblib.dump(final_result, "models/arimax_model.pkl")
        
        # Get test years for dashboard
        test_years = df['year'].iloc[train_size:].values
        
        # Save model info with test data
        model_info = {
            'model': final_result,
            'y_test': y_test.values,
            'y_pred': predictions,
            'test_years': test_years,
            'order': best_order,
            'metrics': {
                'mae': float(mae),
                'rmse': float(rmse),
                'mape': float(mape),
                'r2': float(r2)
            }
        }
        
        # Calculate training duration
        training_duration = time.time() - start_time
        
        # Save complete model info with pickle for better object support
        import pickle
        with open("models/arimax_model.pkl", 'wb') as f:
            pickle.dump(model_info, f)
        
        # Save metrics
        metrics = {
            "mae": float(mae),
            "rmse": float(rmse),
            "mape": float(mape),
            "r2": float(r2),
            "order": str(best_order),
            "p": int(best_order[0]),
            "d": int(best_order[1]),
            "q": int(best_order[2]),
            "train_size": train_size,
            "test_size": len(y_test),
            "train_percentage": int(train_test_split * 100),
            "test_percentage": int((1 - train_test_split) * 100),
            "total_data": len(df),
            "training_duration": float(training_duration)
        }
        joblib.dump(metrics, "models/model_metrics.pkl")
        
        # Prepare stats for database
        year_range = f"{int(df['year'].min())}-{int(df['year'].max())}"
        energy_stats = {
            "min": float(y.min()),
            "max": float(y.max()),
            "mean": float(y.mean())
        }
        gdp_stats = {
            "min": float(exog['gdp'].min()),
            "max": float(exog['gdp'].max()),
            "mean": float(exog['gdp'].mean())
        }
        
        # Save to database as CANDIDATE
        model_id = None
        try:
            model_id = save_training_history(metrics, year_range, energy_stats, gdp_stats)
        except Exception as db_error:
            print(f"Warning: Failed to save to database: {db_error}")
            # Continue even if database save fails
        
        # Prepare response message
        message = f"Model berhasil di-training dengan {len(df)} data points. "
        if model_id:
            message += f"Model disimpan sebagai CANDIDATE (ID: {model_id}). Silakan aktivasi di halaman Update Model untuk menggunakannya dalam prediksi."
        else:
            message += "Model tersimpan sebagai file lokal."
        
        return {
            "status": "success",
            "message": message,
            "rows_used": len(df),
            "year_range": year_range,
            "metrics": metrics,
            "energy_stats": energy_stats,
            "gdp_stats": gdp_stats
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error training model: {str(e)}"
        }
