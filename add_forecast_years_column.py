"""
Script untuk menambahkan kolom forecast_years ke tabel training_history
"""
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

def add_forecast_years_column():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'arimax_forecasting' 
            AND TABLE_NAME = 'training_history' 
            AND COLUMN_NAME = 'forecast_years'
        """)
        
        column_exists = cursor.fetchone()[0] > 0
        
        if not column_exists:
            print("Adding forecast_years column...")
            cursor.execute("""
                ALTER TABLE training_history 
                ADD COLUMN forecast_years INT DEFAULT 3
            """)
            connection.commit()
            print("✓ Column forecast_years added successfully!")
        else:
            print("✓ Column forecast_years already exists!")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_forecast_years_column()
