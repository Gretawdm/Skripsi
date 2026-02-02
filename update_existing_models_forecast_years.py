"""
Script untuk update model yang sudah ada agar punya forecast_years = 3
"""
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

def update_existing_models():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Update all existing models that have NULL forecast_years
        print("Updating existing models with forecast_years = 3...")
        cursor.execute("""
            UPDATE training_history 
            SET forecast_years = 3 
            WHERE forecast_years IS NULL OR forecast_years = 0
        """)
        
        rows_affected = cursor.rowcount
        connection.commit()
        
        print(f"✓ Updated {rows_affected} model(s) with forecast_years = 3")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_existing_models()
