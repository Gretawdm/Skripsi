import mysql.connector

conn = mysql.connector.connect(
    host='localhost', 
    database='arimax_forecasting', 
    user='root', 
    password=''
)
cur = conn.cursor()

print("=== Data Count in History Tables ===")
cur.execute('SELECT COUNT(*) FROM training_history')
print(f"Training History: {cur.fetchone()[0]} records")

cur.execute('SELECT COUNT(*) FROM data_update_history')
print(f"Data Update History: {cur.fetchone()[0]} records")

cur.execute('SELECT COUNT(*) FROM prediction_history')
print(f"Prediction History: {cur.fetchone()[0]} records")

print("\n=== Recent Training History ===")
cur.execute('SELECT training_date, model_version, mape FROM training_history ORDER BY training_date DESC LIMIT 5')
for row in cur.fetchall():
    print(f"  {row[0]} - {row[1]} (MAPE: {row[2]}%)")

print("\n=== Recent Data Update History ===")
cur.execute('SELECT update_date, update_type, records_updated FROM data_update_history ORDER BY update_date DESC LIMIT 5')
for row in cur.fetchall():
    print(f"  {row[0]} - {row[1]} ({row[2]} records)")

print("\n=== Recent Prediction History ===")
cur.execute('SELECT prediction_date, scenario, years FROM prediction_history ORDER BY prediction_date DESC LIMIT 5')
for row in cur.fetchall():
    print(f"  {row[0]} - {row[1]} ({row[2]} years)")

conn.close()
