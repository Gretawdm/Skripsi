import mysql.connector

conn = mysql.connector.connect(
    host='localhost', 
    database='arimax_forecasting', 
    user='root', 
    password=''
)
cursor = conn.cursor()

# Count energy data
cursor.execute('SELECT COUNT(*) FROM energy_data')
energy_count = cursor.fetchone()[0]

cursor.execute('SELECT MIN(year), MAX(year) FROM energy_data')
energy_range = cursor.fetchone()

# Count GDP data
cursor.execute('SELECT COUNT(*) FROM gdp_data')
gdp_count = cursor.fetchone()[0]

cursor.execute('SELECT MIN(year), MAX(year) FROM gdp_data')
gdp_range = cursor.fetchone()

print('\n=== DATA DI DATABASE ===')
print(f'Tabel energy_data: {energy_count} records ({energy_range[0]}-{energy_range[1]})')
print(f'Tabel gdp_data: {gdp_count} records ({gdp_range[0]}-{gdp_range[1]})')

# Show last 5 energy records
cursor.execute('SELECT year, fossil_fuels_twh FROM energy_data ORDER BY year DESC LIMIT 5')
print(f'\n5 Data Energy Terakhir:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]} TWh')

# Show last 5 GDP records
cursor.execute('SELECT year, gdp FROM gdp_data ORDER BY year DESC LIMIT 5')
print(f'\n5 Data GDP Terakhir:')
for row in cursor.fetchall():
    print(f'  {row[0]}: ${row[1]:,.2f}')

cursor.close()
conn.close()
