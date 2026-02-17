import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='arimax_forecasting'
)

cursor = conn.cursor(dictionary=True)
cursor.execute('''
    SELECT id, p, d, q, mape, rmse, mae, r2,
           train_size, test_size, forecast_years,
           year_range
    FROM training_history 
    WHERE model_status = 'active'
    ORDER BY created_at DESC 
    LIMIT 1
''')

result = cursor.fetchone()

if result:
    print(f"Model ID: {result['id']}")
    print(f"Order (p,d,q): ({result['p']}, {result['d']}, {result['q']})")
    print(f"MAPE: {result['mape']}%")
    print(f"RMSE: {result['rmse']}")
    print(f"MAE: {result['mae']}")
    print(f"R²: {result['r2']}")
    print(f"Train Size: {result['train_size']}")
    print(f"Test Size: {result['test_size']}")
    print(f"Year Range: {result['year_range']}")
    print(f"Forecast Years: {result['forecast_years']}")
else:
    print("No active model found")

cursor.close()
conn.close()
