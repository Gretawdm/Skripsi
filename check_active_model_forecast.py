"""
Script untuk cek forecast_years dari model aktif
"""
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

def check_active_model():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        # Get active model
        cursor.execute("""
            SELECT id, p, d, q, mape, train_size, test_size, forecast_years, training_date
            FROM training_history 
            WHERE model_status = 'active'
            ORDER BY activated_at DESC
            LIMIT 1
        """)
        
        model = cursor.fetchone()
        
        if model:
            print("✓ Model Aktif:")
            print(f"  ID: {model['id']}")
            print(f"  Order: ({model['p']}, {model['d']}, {model['q']})")
            print(f"  MAPE: {model['mape']}%")
            print(f"  Train/Test: {model['train_size']}/{model['test_size']}")
            print(f"  Forecast Years: {model['forecast_years']}")
            print(f"  Training Date: {model['training_date']}")
            
            if model['forecast_years'] is None or model['forecast_years'] == 0:
                print("\n⚠ WARNING: forecast_years is NULL/0, will use default 3")
                print("  Updating...")
                cursor.execute("""
                    UPDATE training_history 
                    SET forecast_years = 3 
                    WHERE id = %s
                """, (model['id'],))
                connection.commit()
                print("✓ Updated to 3 years")
        else:
            print("✗ No active model found")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_active_model()
