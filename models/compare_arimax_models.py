"""
ARIMAX Model Comparison Tool
=============================
Script untuk membandingkan performa beberapa ARIMAX model dengan order berbeda.
Menampilkan tabel perbandingan metrics di terminal.

Cara pakai:
$ cd models
$ python compare_arimax_models.py
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from pmdarima import auto_arima
import warnings
warnings.filterwarnings('ignore')

# Warna untuk terminal output
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Color.BOLD}{Color.HEADER}{'='*80}{Color.ENDC}")
    print(f"{Color.BOLD}{Color.HEADER}{text.center(80)}{Color.ENDC}")
    print(f"{Color.BOLD}{Color.HEADER}{'='*80}{Color.ENDC}\n")

def print_success(text):
    print(f"{Color.OKGREEN}✓ {text}{Color.ENDC}")

def print_info(text):
    print(f"{Color.OKCYAN}ℹ {text}{Color.ENDC}")

def print_warning(text):
    print(f"{Color.WARNING}⚠ {text}{Color.ENDC}")

def load_and_prepare_data():
    """Load dan prepare data untuk training"""
    print_header("LOADING DATA")
    
    # Load data
    energy = pd.read_csv('../data/raw/energy.csv')
    gdp = pd.read_csv('../data/raw/gdp.csv')
    
    print_info(f"Data energi: {len(energy)} records")
    print_info(f"Data GDP: {len(gdp)} records")
    
    # Standardize column names
    energy_year_col = "Year" if "Year" in energy.columns else "year"
    gdp_year_col = "year" if "year" in gdp.columns else "Year"
    
    # Identifikasi kolom nilai energi
    energy_value_col = None
    for col in ["fossil_fuels__twh", "fossil_fuels", "value", "Energy"]:
        if col in energy.columns:
            energy_value_col = col
            break
    
    if not energy_value_col:
        raise ValueError(f"Kolom energi tidak ditemukan. Available: {list(energy.columns)}")
    
    gdp_value_col = "gdp" if "gdp" in gdp.columns else "GDP"
    
    # Prepare data
    energy_clean = energy[[energy_year_col, energy_value_col]].copy()
    energy_clean.columns = ["year", "energy"]
    
    gdp_clean = gdp[[gdp_year_col, gdp_value_col]].copy()
    gdp_clean.columns = ["year", "gdp"]
    
    # Merge dengan inner join
    df = pd.merge(energy_clean, gdp_clean, on="year", how="inner")
    df = df.dropna()
    df = df.sort_values("year")
    
    print_success(f"Data merged: {len(df)} records ({df['year'].min()}-{df['year'].max()})")
    
    # Train-test split
    train_size = int(len(df) * 0.8)
    
    y = df["energy"]
    exog = df[["gdp"]]
    
    y_train = y.iloc[:train_size]
    y_test = y.iloc[train_size:]
    exog_train = exog.iloc[:train_size]
    exog_test = exog.iloc[train_size:]
    
    print_info(f"Train size: {len(y_train)} records")
    print_info(f"Test size: {len(y_test)} records")
    
    return y_train, y_test, exog_train, exog_test

def calculate_metrics(y_true, y_pred):
    """Hitung metrics"""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    # R-squared
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot)
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape,
        'R2': r2
    }

def test_model(order, y_train, y_test, exog_train, exog_test):
    """Test satu ARIMAX model dengan order tertentu"""
    try:
        model = SARIMAX(
            y_train,
            exog=exog_train,
            order=order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        result = model.fit(disp=False)
        predictions = result.forecast(steps=len(y_test), exog=exog_test)
        
        metrics = calculate_metrics(y_test, predictions)
        metrics['Status'] = 'Success'
        metrics['AIC'] = result.aic
        metrics['BIC'] = result.bic
        
        return metrics
        
    except Exception as e:
        return {
            'MAE': float('inf'),
            'RMSE': float('inf'),
            'MAPE': float('inf'),
            'R2': -float('inf'),
            'AIC': float('inf'),
            'BIC': float('inf'),
            'Status': f'Failed: {str(e)[:30]}'
        }

def main():
    print_header("ARIMAX MODEL COMPARISON TOOL")
    
    # Load data
    y_train, y_test, exog_train, exog_test = load_and_prepare_data()
    
    # Definisikan beberapa model untuk di-test
    print_header("TESTING MODELS")
    
    models_to_test = [
        (1, 1, 1),
        (2, 1, 1),
        (1, 1, 2),
        (2, 2, 1),
        (1, 2, 2),
        (2, 1, 2),
        (3, 1, 1),
        (1, 1, 3),
        (2, 2, 2),
        (3, 2, 1),
    ]
    
    results = []
    
    print_info("Testing predefined orders...")
    for i, order in enumerate(models_to_test, 1):
        print(f"  {i}/{len(models_to_test)} Testing ARIMAX{order}...", end='')
        metrics = test_model(order, y_train, y_test, exog_train, exog_test)
        results.append({
            'Order': str(order),
            'p': order[0],
            'd': order[1],
            'q': order[2],
            **metrics
        })
        if metrics['Status'] == 'Success':
            print(f" {Color.OKGREEN}✓{Color.ENDC}")
        else:
            print(f" {Color.FAIL}✗{Color.ENDC}")
    
    # Auto ARIMA
    print_info("\nRunning Auto ARIMA to find optimal order...")
    try:
        auto_model = auto_arima(
            y_train,
            exogenous=exog_train,
            start_p=0,
            start_q=0,
            max_p=3,
            max_q=3,
            d=None,
            seasonal=False,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )
        
        auto_order = auto_model.order
        print_success(f"Auto ARIMA found optimal order: {auto_order}")
        
        # Test auto order jika belum ada di list
        if auto_order not in models_to_test:
            metrics = test_model(auto_order, y_train, y_test, exog_train, exog_test)
            results.append({
                'Order': f"{auto_order} (AUTO)",
                'p': auto_order[0],
                'd': auto_order[1],
                'q': auto_order[2],
                **metrics
            })
        else:
            # Mark which one is auto-selected
            for r in results:
                if r['Order'] == str(auto_order):
                    r['Order'] = f"{auto_order} (AUTO)"
                    break
    
    except Exception as e:
        print_warning(f"Auto ARIMA failed: {str(e)}")
    
    # Convert to DataFrame
    df_results = pd.DataFrame(results)
    
    # Filter only successful models
    df_success = df_results[df_results['Status'] == 'Success'].copy()
    
    if len(df_success) == 0:
        print_warning("No successful models!")
        return
    
    # Sort by MAPE (lower is better)
    df_success = df_success.sort_values('MAPE')
    
    # Display results
    print_header("COMPARISON RESULTS")
    
    print(f"{Color.BOLD}Ranking by MAPE (lower is better):{Color.ENDC}\n")
    
    # Print table header
    print(f"{'Rank':<6}{'Order':<20}{'MAPE':<12}{'RMSE':<12}{'MAE':<12}{'R²':<10}{'AIC':<12}{'BIC':<12}")
    print("─" * 100)
    
    # Print each model
    for rank, (idx, row) in enumerate(df_success.iterrows(), 1):
        # Highlight best model
        if rank == 1:
            color = Color.OKGREEN + Color.BOLD
            marker = "🏆"
        elif rank == 2:
            color = Color.OKCYAN
            marker = "🥈"
        elif rank == 3:
            color = Color.WARNING
            marker = "🥉"
        else:
            color = ""
            marker = "  "
        
        print(f"{color}{marker} {rank:<4}"
              f"{row['Order']:<20}"
              f"{row['MAPE']:>10.2f}% "
              f"{row['RMSE']:>10.2f}  "
              f"{row['MAE']:>10.2f}  "
              f"{row['R2']:>8.4f}  "
              f"{row['AIC']:>10.2f}  "
              f"{row['BIC']:>10.2f}"
              f"{Color.ENDC}")
    
    # Print best model summary
    best = df_success.iloc[0]
    
    print_header("BEST MODEL")
    print(f"{Color.BOLD}Order:{Color.ENDC} {best['Order']}")
    print(f"{Color.BOLD}Performance:{Color.ENDC}")
    print(f"  • MAPE: {Color.OKGREEN}{best['MAPE']:.2f}%{Color.ENDC}")
    print(f"  • RMSE: {best['RMSE']:.2f}")
    print(f"  • MAE:  {best['MAE']:.2f}")
    print(f"  • R²:   {best['R2']:.4f}")
    print(f"\n{Color.BOLD}Information Criteria:{Color.ENDC}")
    print(f"  • AIC:  {best['AIC']:.2f}")
    print(f"  • BIC:  {best['BIC']:.2f}")
    
    # Recommendation
    print_header("RECOMMENDATION")
    print(f"✅ {Color.OKGREEN}Gunakan order {best['Order']} untuk model production{Color.ENDC}")
    print(f"📊 Model ini memberikan MAPE terendah: {Color.BOLD}{best['MAPE']:.2f}%{Color.ENDC}")
    
    # Save results to CSV
    df_success.to_csv('arimax_comparison_results.csv', index=False)
    print_success(f"\nResults saved to: arimax_comparison_results.csv")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
