"""
Script untuk import training history dari file pkl ke database
"""
import joblib
import pandas as pd
from services.database_service import save_training_history

# Load metrics dari file
try:
    metrics = joblib.load("models/model_metrics.pkl")
    print("✓ Loaded metrics from pkl file:")
    print(metrics)
    
    # Load data untuk ambil year range dan stats
    energy_df = pd.read_csv("data/raw/energy.csv")
    gdp_df = pd.read_csv("data/raw/gdp.csv")
    
    # Prepare data
    year_col = "Year" if "Year" in energy_df.columns else "year"
    year_range = f"{int(energy_df[year_col].min())}-{int(energy_df[year_col].max())}"
    
    # Energy stats
    energy_col = None
    for col in ["fossil_fuels__twh", "fossil_fuels", "value", "Energy"]:
        if col in energy_df.columns:
            energy_col = col
            break
    
    if energy_col:
        energy_stats = {
            "min": float(energy_df[energy_col].min()),
            "max": float(energy_df[energy_col].max()),
            "mean": float(energy_df[energy_col].mean())
        }
    else:
        energy_stats = {"min": 0, "max": 0, "mean": 0}
    
    # GDP stats
    gdp_col = "gdp" if "gdp" in gdp_df.columns else "GDP"
    gdp_stats = {
        "min": float(gdp_df[gdp_col].min()),
        "max": float(gdp_df[gdp_col].max()),
        "mean": float(gdp_df[gdp_col].mean())
    }
    
    print(f"\nYear range: {year_range}")
    print(f"Energy stats: {energy_stats}")
    print(f"GDP stats: {gdp_stats}")
    
    # Save to database
    result = save_training_history(metrics, year_range, energy_stats, gdp_stats)
    
    if result:
        print("\n✓ Training history successfully imported to database!")
    else:
        print("\n✗ Failed to import training history")
        
except FileNotFoundError:
    print("✗ model_metrics.pkl not found. Please train the model first.")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
