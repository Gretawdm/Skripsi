import mysql.connector
import json

conn = mysql.connector.connect(
    host='localhost',
    database='arimax_forecasting',
    user='root',
    password=''
)
cursor = conn.cursor(dictionary=True)

# Get latest moderat prediction
cursor.execute("""
    SELECT id, scenario, years, prediction_date, prediction_data 
    FROM prediction_history 
    WHERE scenario = 'moderat' 
    ORDER BY prediction_date DESC 
    LIMIT 1
""")

result = cursor.fetchone()

if result:
    print(f"\n=== Latest Moderat Prediction ===")
    print(f"ID: {result['id']}")
    print(f"Scenario: {result['scenario']}")
    print(f"Years: {result['years']}")  # Ini yang dipakai untuk dropdown!
    print(f"Date: {result['prediction_date']}")
    
    # Parse prediction_data
    pred_data = json.loads(result['prediction_data'])
    print(f"\nPrediction values count: {len(pred_data)}")
    print(f"Values: {pred_data}")
    
    # Fix: Update years jika tidak sesuai dengan jumlah data
    if result['years'] != len(pred_data):
        print(f"\n⚠️  MISMATCH: years={result['years']} but data has {len(pred_data)} values!")
        print(f"Should update to: {len(pred_data)}")

conn.close()
