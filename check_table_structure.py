import mysql.connector

conn = mysql.connector.connect(
    host='localhost', 
    database='arimax_forecasting', 
    user='root', 
    password=''
)
cur = conn.cursor()

print("=== training_history columns ===")
cur.execute('DESCRIBE training_history')
for row in cur.fetchall():
    print(f"{row[0]:20} {row[1]:20} {row[2]:5} {row[3]:5}")

conn.close()
