import mysql.connector
import json

conn = mysql.connector.connect(
    host='localhost',
    database='arimax_forecasting',
    user='root',
    password=''
)
cursor = conn.cursor(dictionary=True)

# Get latest prediction
cursor.execute("""
    SELECT id, scenario, years, prediction_date, prediction_data, model_version
    FROM prediction_history 
    ORDER BY prediction_date DESC 
    LIMIT 3
""")

results = cursor.fetchall()

print("\n=== Latest Predictions in Database ===")
for i, r in enumerate(results, 1):
    print(f"\n{i}. ID: {r['id']}")
    print(f"   Date: {r['prediction_date']}")
    print(f"   Scenario: {r['scenario']}")
    print(f"   Years: {r['years']} tahun")
    print(f"   Model: {r['model_version']}")
    
    # Parse data
    pred_data = json.loads(r['prediction_data'])
    print(f"   Data count: {len(pred_data)} values")
    print(f"   Values: {pred_data}")

conn.close()
