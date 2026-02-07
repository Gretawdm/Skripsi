import mysql.connector

conn = mysql.connector.connect(
    host='localhost', 
    database='arimax_forecasting', 
    user='root', 
    password=''
)
cursor = conn.cursor(dictionary=True)

# Cek tabel prediction_history
cursor.execute('''
    SELECT id, prediction_date, scenario, years 
    FROM prediction_history 
    ORDER BY prediction_date DESC 
    LIMIT 5
''')
predictions = cursor.fetchall()

print('=== Prediksi History ===')
for p in predictions:
    print(f'ID: {p["id"]} | Date: {p["prediction_date"]} | Scenario: {p["scenario"]} | Years: {p["years"]}')

# Cek detail prediksi terakhir (moderat)
cursor.execute('''
    SELECT * FROM prediction_history 
    WHERE scenario = 'moderat' 
    ORDER BY prediction_date DESC 
    LIMIT 1
''')
latest = cursor.fetchone()

if latest:
    print(f'\n=== Prediksi Terakhir (Moderat) ===')
    print(f'ID: {latest["id"]}')
    print(f'Date: {latest["prediction_date"]}')
    print(f'Scenario: {latest["scenario"]}')
    print(f'Years: {latest["years"]}')
    if 'prediction_values' in latest:
        print(f'Values: {latest["prediction_values"]}')

conn.close()
