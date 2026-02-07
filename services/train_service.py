import pandas as pd
import joblib
import os
import numpy as np
import time
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pmdarima import auto_arima
from services.database_service import save_training_history

def plot_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"

def generate_preprocessing_plots(y, y_train, y_test, train_size):
    """Generate preprocessing visualization plots"""
    plots = {}
    
    # 1. ACF Plot
    try:
        fig, ax = plt.subplots(figsize=(10, 4))
        plot_acf(y, lags=20, ax=ax)
        ax.set_title('Autocorrelation Function (ACF)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Lag')
        ax.set_ylabel('Correlation')
        plots['acf_plot'] = plot_to_base64(fig)
    except Exception as e:
        print(f"Warning: ACF plot failed: {e}")
        plots['acf_plot'] = None
    
    # 2. PACF Plot
    try:
        fig, ax = plt.subplots(figsize=(10, 4))
        plot_pacf(y, lags=20, ax=ax, method='ywm')
        ax.set_title('Partial Autocorrelation Function (PACF)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Lag')
        ax.set_ylabel('Correlation')
        plots['pacf_plot'] = plot_to_base64(fig)
    except Exception as e:
        print(f"Warning: PACF plot failed: {e}")
        plots['pacf_plot'] = None
    
    # 3. Data Before/After Split (Preprocessing)
    try:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(y.index, y.values, label='Full Data', color='#01384F', linewidth=2)
        ax.axvline(x=train_size, color='red', linestyle='--', linewidth=2, label=f'Train/Test Split ({train_size})')
        ax.fill_between(range(train_size), y.min(), y.max(), alpha=0.1, color='green', label='Training Data')
        ax.fill_between(range(train_size, len(y)), y.min(), y.max(), alpha=0.1, color='orange', label='Test Data')
        ax.set_title('Data Preprocessing: Train-Test Split', fontsize=12, fontweight='bold')
        ax.set_xlabel('Index')
        ax.set_ylabel('Energy Consumption (TWh)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plots['preprocessing_plot'] = plot_to_base64(fig)
    except Exception as e:
        print(f"Warning: Preprocessing plot failed: {e}")
        plots['preprocessing_plot'] = None
    
    # 4. Train vs Test Visualization
    try:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(range(len(y_train)), y_train.values, label='Training Data', color='#53B863', linewidth=2, marker='o', markersize=4)
        ax.plot(range(len(y_train), len(y)), y_test.values, label='Test Data', color='#FF6B6B', linewidth=2, marker='s', markersize=4)
        ax.set_title('Training vs Testing Data Split', fontsize=12, fontweight='bold')
        ax.set_xlabel('Data Point')
        ax.set_ylabel('Energy Consumption (TWh)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plots['train_test_plot'] = plot_to_base64(fig)
    except Exception as e:
        print(f"Warning: Train/test plot failed: {e}")
        plots['train_test_plot'] = None
    
    return plots

def generate_residual_diagnostics(residuals):
    """
    Generate residual diagnostic plots and statistical tests
    Returns dict with plots and test results
    """
    diagnostics = {}
    
    # 1. Residual Plot Over Time
    try:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(residuals, color='#01384F', linewidth=1.5, marker='o', markersize=3)
        ax.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Zero Line')
        ax.set_title('Residual Plot (Error Over Time)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Observation')
        ax.set_ylabel('Residuals')
        ax.legend()
        ax.grid(True, alpha=0.3)
        diagnostics['residual_plot'] = plot_to_base64(fig)
    except Exception as e:
        print(f"Warning: Residual plot failed: {e}")
        diagnostics['residual_plot'] = None
    
    # 2. ACF Plot of Residuals (White Noise Check)
    try:
        fig, ax = plt.subplots(figsize=(10, 4))
        plot_acf(residuals, lags=min(20, len(residuals)//2), ax=ax)
        ax.set_title('ACF of Residuals (White Noise Test)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Lag')
        ax.set_ylabel('Autocorrelation')
        diagnostics['residual_acf_plot'] = plot_to_base64(fig)
    except Exception as e:
        print(f"Warning: Residual ACF plot failed: {e}")
        diagnostics['residual_acf_plot'] = None
    
    # 3. Q-Q Plot (Normality Check)
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        stats.probplot(residuals, dist="norm", plot=ax)
        ax.set_title('Q-Q Plot (Normality Test)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        diagnostics['qq_plot'] = plot_to_base64(fig)
    except Exception as e:
        print(f"Warning: Q-Q plot failed: {e}")
        diagnostics['qq_plot'] = None
    
    # 4. Ljung-Box Test (White Noise)
    try:
        lb_test = acorr_ljungbox(residuals, lags=min(10, len(residuals)//5), return_df=True)
        # Check if any p-value < 0.05 (reject H0 = not white noise)
        lb_pvalue = lb_test['lb_pvalue'].iloc[-1]  # Last lag p-value
        lb_pass = lb_pvalue > 0.05
        diagnostics['ljungbox_pvalue'] = float(lb_pvalue)
        diagnostics['ljungbox_pass'] = lb_pass
    except Exception as e:
        print(f"Warning: Ljung-Box test failed: {e}")
        diagnostics['ljungbox_pvalue'] = None
        diagnostics['ljungbox_pass'] = None
    
    # 5. Jarque-Bera Test (Normality)
    try:
        jb_stat, jb_pvalue = stats.jarque_bera(residuals)
        jb_pass = jb_pvalue > 0.05
        diagnostics['jarque_bera_pvalue'] = float(jb_pvalue)
        diagnostics['jarque_bera_pass'] = jb_pass
    except Exception as e:
        print(f"Warning: Jarque-Bera test failed: {e}")
        diagnostics['jarque_bera_pvalue'] = None
        diagnostics['jarque_bera_pass'] = None
    
    # 6. Residual Statistics
    diagnostics['residual_mean'] = float(np.mean(residuals))
    diagnostics['residual_std'] = float(np.std(residuals))
    diagnostics['residual_min'] = float(np.min(residuals))
    diagnostics['residual_max'] = float(np.max(residuals))
    
    return diagnostics

def retrain_model(train_test_split=0.8, order_mode='auto', manual_order=None, forecast_years=3):
    """
    Retrain ARIMAX model dengan data terbaru
    
    Args:
        train_test_split (float): Ratio untuk train data (0.0-1.0). Default 0.8 (80% training, 20% testing)
        order_mode (str): 'auto' untuk auto_arima atau 'manual' untuk set manual. Default 'auto'
        manual_order (tuple): (p,d,q) jika order_mode='manual'. Default None
        forecast_years (int): Number of years to forecast in dashboard. Default 3
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
        
        # ==================================================================
        # CAPTURE PREPROCESSING STEPS FOR DISPLAY IN HISTORY
        # ==================================================================
        preprocessing_steps = []
        
        # STEP 1: Identifikasi Data
        step1 = {
            "step": 1,
            "title": "Identifikasi Data",
            "description": "Mengidentifikasi dan memuat dataset Energy dan GDP",
            "details": [
                f"Total records Energy: {len(energy_clean)} tahun ({energy_clean['year'].min()}-{energy_clean['year'].max()})",
                f"Total records GDP: {len(gdp_clean)} tahun ({gdp_clean['year'].min()}-{gdp_clean['year'].max()})",
                f"Records setelah merge: {len(df)} tahun ({df['year'].min()}-{df['year'].max()})",
                f"Variabel target: Energy (TWh)",
                f"Variabel exogenous: GDP (Billion USD)"
            ],
            "status": "success"
        }
        preprocessing_steps.append(step1)
        
        # STEP 2: Pengecekan Missing Values
        total_records = len(df)
        missing_info = df.isnull().sum()
        
        print(f"\n{'='*60}")
        print("PENGECEKAN MISSING VALUES")
        print(f"{'='*60}")
        
        if missing_info.sum() > 0:
            print(f"⚠️  DITEMUKAN MISSING VALUES:")
            missing_details = []
            for col in df.columns:
                if missing_info[col] > 0:
                    pct = (missing_info[col] / total_records) * 100
                    print(f"   - {col}: {missing_info[col]} records ({pct:.2f}%)")
                    missing_details.append(f"{col}: {missing_info[col]} records ({pct:.2f}%)")
            
            # Drop missing values
            df_before = len(df)
            df = df.dropna()
            df_after = len(df)
            dropped = df_before - df_after
            
            print(f"\n✅ Missing values di-drop:")
            print(f"   - Records sebelum: {df_before}")
            print(f"   - Records sesudah: {df_after}")
            print(f"   - Total di-drop: {dropped} records ({(dropped/df_before)*100:.2f}%)")
            
            step2 = {
                "step": 2,
                "title": "Pengecekan Missing Value",
                "description": "Deteksi dan penanganan missing values",
                "details": [
                    f"⚠️ Ditemukan missing values:",
                    *missing_details,
                    f"Records sebelum cleaning: {df_before}",
                    f"Records sesudah cleaning: {df_after}",
                    f"Total di-drop: {dropped} records ({(dropped/df_before)*100:.2f}%)"
                ],
                "status": "warning"
            }
        else:
            print("✅ Tidak ada missing values - data bersih!")
            print(f"   Total records: {total_records}")
            
            step2 = {
                "step": 2,
                "title": "Pengecekan Missing Value",
                "description": "Deteksi dan penanganan missing values",
                "details": [
                    f"✅ Tidak ada missing values ditemukan",
                    f"Total records: {total_records}",
                    f"Data sudah bersih dan siap diproses"
                ],
                "status": "success"
            }
        
        preprocessing_steps.append(step2)
        print(f"{'='*60}\n")
        
        # Prepare data for ARIMAX
        y = df["energy"]
        exog = df[["gdp"]]
        
        # STEP 3: Statistik Deskriptif
        step3 = {
            "step": 3,
            "title": "Statistik Deskriptif",
            "description": "Analisis statistik data sebelum modeling",
            "details": [
                f"Energy - Min: {y.min():.2f} TWh, Max: {y.max():.2f} TWh, Mean: {y.mean():.2f} TWh",
                f"GDP - Min: {exog['gdp'].min():.2f}B USD, Max: {exog['gdp'].max():.2f}B USD, Mean: {exog['gdp'].mean():.2f}B USD",
                f"Periode data: {df['year'].min()}-{df['year'].max()} ({len(df)} tahun)",
                f"Standar deviasi Energy: {y.std():.2f}",
                f"Standar deviasi GDP: {exog['gdp'].std():.2f}"
            ],
            "status": "success"
        }
        preprocessing_steps.append(step3)
        
        # Train-test split untuk evaluasi (gunakan parameter dari user)
        train_size = int(len(df) * train_test_split)
        y_train = y.iloc[:train_size]
        y_test = y.iloc[train_size:]
        exog_train = exog.iloc[:train_size]
        exog_test = exog.iloc[train_size:]
        
        # STEP 4: Split Data
        step4 = {
            "step": 4,
            "title": "Split Data Training & Testing",
            "description": "Pembagian dataset untuk training dan evaluasi model",
            "details": [
                f"Ratio split: {int(train_test_split*100)}% training, {int((1-train_test_split)*100)}% testing",
                f"Data training: {len(y_train)} records ({df['year'].iloc[0]}-{df['year'].iloc[train_size-1]})",
                f"Data testing: {len(y_test)} records ({df['year'].iloc[train_size]}-{df['year'].iloc[-1]})",
                f"Total data: {len(df)} records"
            ],
            "status": "success"
        }
        preprocessing_steps.append(step4)
        
        # Generate preprocessing plots
        print("Generating visualization plots...")
        viz_plots = generate_preprocessing_plots(y, y_train, y_test, train_size)
        
        # STEP 5: Identifikasi Parameter ACF & PACF
        step5 = {
            "step": 5,
            "title": "Identifikasi Parameter (p,d,q)",
            "description": "Analisis ACF dan PACF untuk menentukan order ARIMAX",
            "details": [
                "📊 ACF Plot digunakan untuk identifikasi MA order (q)",
                "📊 PACF Plot digunakan untuk identifikasi AR order (p)",
                "💡 Grafik menunjukkan korelasi lag yang signifikan",
                "⚠️ Nilai p,d,q bisa ditentukan otomatis (auto_arima) atau manual"
            ],
            "status": "success"
        }
        preprocessing_steps.append(step5)
        
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
            
            # STEP 6: Auto ARIMA
            step6 = {
                "step": 6,
                "title": "Penentuan Parameter dengan Auto ARIMA",
                "description": "Pencarian otomatis parameter optimal menggunakan AIC",
                "details": [
                    f"✅ Mode: Automatic Parameter Selection",
                    f"📈 Best Order found: ({best_order[0]}, {best_order[1]}, {best_order[2]})",
                    f"   - p (AR): {best_order[0]} - Autoregressive order",
                    f"   - d (I): {best_order[1]} - Differencing order",
                    f"   - q (MA): {best_order[2]} - Moving Average order",
                    f"🎯 Parameter dipilih berdasarkan AIC terendah"
                ],
                "status": "success"
            }
        else:
            # Manual order from user
            if manual_order and isinstance(manual_order, (tuple, list)) and len(manual_order) == 3:
                best_order = tuple(manual_order)
                print(f"Using manual ARIMAX order: {best_order}")
            else:
                # Default fallback
                best_order = (3, 2, 6)
                print(f"Using default ARIMAX order: {best_order}")
            
            # STEP 6: Manual Parameter
            step6 = {
                "step": 6,
                "title": "Penentuan Parameter Manual",
                "description": "Parameter ARIMAX ditentukan secara manual",
                "details": [
                    f"⚙️ Mode: Manual Parameter Selection",
                    f"📈 Order yang digunakan: ({best_order[0]}, {best_order[1]}, {best_order[2]})",
                    f"   - p (AR): {best_order[0]} - Autoregressive order",
                    f"   - d (I): {best_order[1]} - Differencing order",
                    f"   - q (MA): {best_order[2]} - Moving Average order",
                    f"💡 Parameter dapat di-override tanpa mengikuti ACF/PACF"
                ],
                "status": "success"
            }
        
        preprocessing_steps.append(step6)
        
        print(f"Training with {len(df)} records (train: {train_size}, test: {len(y_test)})")
        
        # STEP 7: Training Model
        step7 = {
            "step": 7,
            "title": "Training Model ARIMAX",
            "description": "Melatih model SARIMAX dengan data training",
            "details": [
                f"🔧 Model: ARIMAX (ARIMA with Exogenous variables)",
                f"📊 Target variable: Energy (TWh)",
                f"📈 Exogenous variable: GDP (Billion USD)",
                f"🎯 Order: ({best_order[0]}, {best_order[1]}, {best_order[2]})",
                f"📝 Training data: {len(y_train)} records",
                f"⏳ Proses fitting model sedang berjalan..."
            ],
            "status": "success"
        }
        preprocessing_steps.append(step7)
        
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
        
        # Calculate residuals from test set
        residuals = y_test - predictions
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
        
        # R-squared
        ss_res = np.sum((y_test - predictions) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        # STEP 8: Evaluasi Model
        step8 = {
            "step": 8,
            "title": "Evaluasi Performa Model",
            "description": "Menghitung metrics evaluasi pada data testing",
            "details": [
                f"📊 Testing data: {len(y_test)} records",
                f"✅ MAPE (Mean Absolute Percentage Error): {mape:.2f}%",
                f"✅ RMSE (Root Mean Squared Error): {rmse:.2f}",
                f"✅ MAE (Mean Absolute Error): {mae:.2f}",
                f"✅ R² (Coefficient of Determination): {r2:.4f}",
                f"🎯 Model accuracy: {'Excellent' if mape < 10 else 'Good' if mape < 20 else 'Fair' if mape < 30 else 'Needs Improvement'}"
            ],
            "status": "success" if mape < 20 else "warning" if mape < 30 else "danger"
        }
        preprocessing_steps.append(step8)
        
        # Generate Residual Diagnostics
        print("Performing residual diagnostics...")
        residual_diagnostics = generate_residual_diagnostics(residuals)
        
        # STEP 9: Diagnosis Residual
        diag_details = [
            f"📊 Residual Statistics:",
            f"   - Mean: {residual_diagnostics['residual_mean']:.4f} (should be ~0)",
            f"   - Std Dev: {residual_diagnostics['residual_std']:.4f}",
            f"   - Min: {residual_diagnostics['residual_min']:.4f}",
            f"   - Max: {residual_diagnostics['residual_max']:.4f}",
            ""
        ]
        
        # Ljung-Box Test
        if residual_diagnostics['ljungbox_pvalue'] is not None:
            lb_status = "✅ PASS" if residual_diagnostics['ljungbox_pass'] else "❌ FAIL"
            diag_details.append(f"🔬 Ljung-Box Test (White Noise):")
            diag_details.append(f"   - p-value: {residual_diagnostics['ljungbox_pvalue']:.4f}")
            diag_details.append(f"   - Result: {lb_status} (p > 0.05 = white noise)")
            diag_details.append("")
        
        # Jarque-Bera Test
        if residual_diagnostics['jarque_bera_pvalue'] is not None:
            jb_status = "✅ PASS" if residual_diagnostics['jarque_bera_pass'] else "⚠️ WARNING"
            diag_details.append(f"🔬 Jarque-Bera Test (Normality):")
            diag_details.append(f"   - p-value: {residual_diagnostics['jarque_bera_pvalue']:.4f}")
            diag_details.append(f"   - Result: {jb_status} (p > 0.05 = normal)")
            diag_details.append("")
        
        # Overall assessment
        overall_pass = (
            residual_diagnostics.get('ljungbox_pass', False) and
            residual_diagnostics.get('jarque_bera_pass', False) and
            abs(residual_diagnostics['residual_mean']) < 0.1
        )
        
        diag_details.append(f"🎯 Overall Assessment: {'✅ Model assumptions satisfied' if overall_pass else '⚠️ Some assumptions may be violated'}")
        
        step9 = {
            "step": 9,
            "title": "Diagnosis Residual",
            "description": "Uji asumsi model: white noise dan normalitas residual",
            "details": diag_details,
            "status": "success" if overall_pass else "warning"
        }
        preprocessing_steps.append(step9)
        
        # Merge residual plots with existing viz_plots
        viz_plots.update(residual_diagnostics)
        
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
            model_id = save_training_history(metrics, year_range, energy_stats, gdp_stats, forecast_years, viz_plots, preprocessing_steps)
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
