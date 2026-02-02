"""
Script untuk update forecast_years model aktif jadi 3 tahun
"""
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

def update_active_model_forecast_years():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Update active model forecast_years to 3
        cursor.execute("""
            UPDATE training_history 
            SET forecast_years = 3 
            WHERE model_status = 'active'
        """)
        
        rows_affected = cursor.rowcount
        connection.commit()
        
        if rows_affected > 0:
            print(f"✓ Updated active model forecast_years to 3 years")
            print("  Silakan refresh dashboard untuk melihat perubahan")
        else:
            print("✗ No active model found")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_active_model_forecast_years()
