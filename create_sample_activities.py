"""
Script untuk membuat dummy activities dengan timestamp berbeda
Berguna untuk testing tampilan "Aktivitas Terbaru" di dashboard
"""
import mysql.connector
from datetime import datetime, timedelta
import json

DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

def create_sample_activities():
    """Create sample activities with different timestamps"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        now = datetime.now()
        
        # Create training history with different times
        training_times = [
            now - timedelta(minutes=5),
            now - timedelta(hours=2),
            now - timedelta(hours=6),
            now - timedelta(days=1),
            now - timedelta(days=3)
        ]
        
        print("\nCreating sample training history...")
        for i, time in enumerate(training_times, 1):
            cursor.execute("""
                INSERT INTO training_history (
                    training_date, model_version, p, d, q,
                    mape, rmse, mae, r2, train_size, test_size,
                    train_percentage, test_percentage, total_data,
                    year_range, energy_min, energy_max, energy_mean,
                    gdp_min, gdp_max, gdp_mean, model_status
                ) VALUES (
                    %s, 'ARIMAX v1.0', 3, 2, 0,
                    5.5, 150.2, 120.5, 0.68, 48, 12,
                    80, 20, 60,
                    '1965-2024', 100.5, 5000.2, 2500.8,
                    1000000000, 15000000000000, 8000000000000, 'candidate'
                )
            """, (time,))
            print(f"  {i}. Training at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create data update history
        update_times = [
            now - timedelta(minutes=10),
            now - timedelta(hours=4),
            now - timedelta(days=2)
        ]
        
        print("\nCreating sample data update history...")
        for i, time in enumerate(update_times, 1):
            cursor.execute("""
                INSERT INTO data_update_history (
                    update_date, update_type, source,
                    records_added, records_updated, status, message
                ) VALUES (
                    %s, 'All', 'World Bank API',
                    15, 15, 'success', 'Data successfully updated'
                )
            """, (time,))
            print(f"  {i}. Data update at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create prediction history
        prediction_times = [
            now - timedelta(minutes=2),
            now - timedelta(hours=1),
            now - timedelta(hours=5)
        ]
        
        print("\nCreating sample prediction history...")
        for i, time in enumerate(prediction_times, 1):
            scenario = ['optimis', 'moderat', 'pesimistis'][i % 3]
            prediction_data = [5000 + (i * 100) for _ in range(5)]
            
            cursor.execute("""
                INSERT INTO prediction_history (
                    prediction_date, scenario, years,
                    prediction_data, model_version
                ) VALUES (
                    %s, %s, 5, %s, 'ARIMAX (3,2,0)'
                )
            """, (time, scenario, json.dumps(prediction_data)))
            print(f"  {i}. Prediction ({scenario}) at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✓ Sample activities created successfully!")
        print("  Refresh your dashboard to see activities with different timestamps.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*70)
    print("Creating Sample Activities for Dashboard Testing")
    print("="*70)
    
    create_sample_activities()
    
    print("\n" + "="*70)
    print("Done! Open http://127.0.0.1:5000/admin/dashboard to see results")
    print("="*70)
