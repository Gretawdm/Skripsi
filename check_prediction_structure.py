import mysql.connector
import json

conn = mysql.connector.connect(
    host='localhost',
    database='arimax_forecasting',
    user='root',
    password=''
)
cursor = conn.cursor(dictionary=True)

# Cek struktur tabel
cursor.execute('DESCRIBE prediction_history')
cols = cursor.fetchall()
print('=== Columns in prediction_history ===')
for c in cols:
    print(f"  {c['Field']}: {c['Type']}")

# Cek data terakhir
cursor.execute('SELECT * FROM prediction_history ORDER BY prediction_date DESC LIMIT 1')
latest = cursor.fetchone()

if latest:
    print('\n=== Latest Prediction Record ===')
    for key, value in latest.items():
        if key == 'prediction_data' and value:
            try:
                parsed = json.loads(value)
                print(f"  {key}: {parsed[:2]}... (showing first 2 items)")
            except:
                print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")

conn.close()
