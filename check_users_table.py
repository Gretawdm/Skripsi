import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    
    print("Struktur tabel users:")
    print("-" * 50)
    for col in columns:
        print(f"{col[0]:<20} {col[1]:<20}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
