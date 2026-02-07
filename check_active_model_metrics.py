import mysql.connector
from services.database_service import get_db_connection

def check_active_model():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get active model info from training_history
        query = """
        SELECT model_version, mape, forecast_years, model_status, training_date, p, d, q
        FROM training_history
        WHERE model_status = 'active'
        ORDER BY training_date DESC
        LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            print("\n=== Active Model Metrics ===")
            print(f"Model: {result['model_version']} - ARIMAX ({result['p']},{result['d']},{result['q']})")
            print(f"MAPE: {result['mape']}%")
            print(f"Forecast Years: {result['forecast_years']}")
            print(f"Training Date: {result['training_date']}")
            print(f"\nAccuracy (100 - MAPE): {100 - float(result['mape']):.2f}%")
        else:
            print("No active model found!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_active_model()
