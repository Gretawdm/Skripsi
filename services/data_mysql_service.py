"""
Service untuk manage data energy dan GDP di MySQL
Hybrid system: CSV untuk training, MySQL untuk history & display
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import pandas as pd
from services.database_service import get_db_connection

def init_data_tables():
    """
    Initialize data tables for energy and GDP
    """
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        # Table for energy data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT NOT NULL UNIQUE,
                entity VARCHAR(100) DEFAULT 'Indonesia',
                fossil_fuels_twh DECIMAL(15, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Table for GDP data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gdp_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT NOT NULL UNIQUE,
                gdp DECIMAL(20, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✓ Data tables initialized successfully!")
        return True
        
    except Error as e:
        print(f"✗ Error initializing data tables: {e}")
        return False

def save_energy_to_db(df, clear_existing=True):
    """
    Save energy dataframe to MySQL
    Uses INSERT ... ON DUPLICATE KEY UPDATE for upsert
    
    Args:
        df: DataFrame containing energy data
        clear_existing: If True, delete all existing records before inserting (default: True)
    """
    try:
        connection = get_db_connection()
        if not connection:
            return 0
        
        cursor = connection.cursor()
        
        # Clear existing data if requested
        if clear_existing:
            cursor.execute("DELETE FROM energy_data")
            print("🗑️  Cleared existing energy data")
        
        # Identify year and value columns
        year_col = "Year" if "Year" in df.columns else "year"
        
        # Find fossil fuels column
        value_col = None
        for col in ["fossil_fuels__twh", "fossil_fuels", "value", "Energy"]:
            if col in df.columns:
                value_col = col
                break
        
        if not value_col:
            print(f"⚠ No energy value column found in: {df.columns.tolist()}")
            return 0
        
        records_saved = 0
        
        for _, row in df.iterrows():
            year = int(row[year_col])
            value = float(row[value_col]) if pd.notna(row[value_col]) else None
            
            if value is not None:
                query = """
                    INSERT INTO energy_data (year, fossil_fuels_twh)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE 
                        fossil_fuels_twh = VALUES(fossil_fuels_twh),
                        updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(query, (year, value))
                records_saved += 1
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return records_saved
        
    except Error as e:
        print(f"✗ Error saving energy data: {e}")
        return 0

def save_gdp_to_db(df, clear_existing=True):
    """
    Save GDP dataframe to MySQL
    
    Args:
        df: DataFrame containing GDP data
        clear_existing: If True, delete all existing records before inserting (default: True)
    """
    try:
        connection = get_db_connection()
        if not connection:
            return 0
        
        cursor = connection.cursor()
        
        # Clear existing data if requested
        if clear_existing:
            cursor.execute("DELETE FROM gdp_data")
            print("🗑️  Cleared existing GDP data")
        
        # Identify columns
        year_col = "year" if "year" in df.columns else "Year"
        gdp_col = "gdp" if "gdp" in df.columns else "GDP"
        
        records_saved = 0
        
        for _, row in df.iterrows():
            year = int(row[year_col])
            gdp = float(row[gdp_col]) if pd.notna(row[gdp_col]) else None
            
            if gdp is not None:
                query = """
                    INSERT INTO gdp_data (year, gdp)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE 
                        gdp = VALUES(gdp),
                        updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(query, (year, gdp))
                records_saved += 1
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return records_saved
        
    except Error as e:
        print(f"✗ Error saving GDP data: {e}")
        return 0

def get_energy_from_db(start_year=None, end_year=None):
    """
    Get energy data from MySQL
    """
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        if start_year and end_year:
            query = """
                SELECT year AS Year, fossil_fuels_twh as fossil_fuels__twh, updated_at
                FROM energy_data
                WHERE year BETWEEN %s AND %s
                ORDER BY year
            """
            cursor.execute(query, (start_year, end_year))
        else:
            query = """
                SELECT year AS Year, fossil_fuels_twh as fossil_fuels__twh, updated_at
                FROM energy_data
                ORDER BY year
            """
            cursor.execute(query)
        
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return results
        
    except Error as e:
        print(f"✗ Error getting energy data: {e}")
        return []

def get_gdp_from_db(start_year=None, end_year=None):
    """
    Get GDP data from MySQL
    """
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        if start_year and end_year:
            query = """
                SELECT year, gdp, updated_at
                FROM gdp_data
                WHERE year BETWEEN %s AND %s
                ORDER BY year
            """
            cursor.execute(query, (start_year, end_year))
        else:
            query = """
                SELECT year, gdp, updated_at
                FROM gdp_data
                ORDER BY year
            """
            cursor.execute(query)
        
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return results
        
    except Error as e:
        print(f"✗ Error getting GDP data: {e}")
        return []

def get_data_stats_from_db():
    """
    Get statistics from MySQL database
    """
    try:
        connection = get_db_connection()
        if not connection:
            return {
                'energy_count': 0,
                'gdp_count': 0,
                'year_range': '-',
                'last_update': '-'
            }
        
        cursor = connection.cursor(dictionary=True)
        
        # Energy stats
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                MIN(year) as min_year,
                MAX(year) as max_year,
                MAX(updated_at) as last_update
            FROM energy_data
        """)
        energy_stats = cursor.fetchone()
        
        # GDP stats
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                MIN(year) as min_year,
                MAX(year) as max_year,
                MAX(updated_at) as last_update
            FROM gdp_data
        """)
        gdp_stats = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Find common year range
        if energy_stats['count'] > 0 and gdp_stats['count'] > 0:
            min_year = max(energy_stats['min_year'], gdp_stats['min_year'])
            max_year = min(energy_stats['max_year'], gdp_stats['max_year'])
            year_range = f"{min_year}-{max_year}"
        else:
            year_range = "-"
        
        # Last update
        last_update = "-"
        if energy_stats['last_update'] or gdp_stats['last_update']:
            dates = [d for d in [energy_stats['last_update'], gdp_stats['last_update']] if d]
            if dates:
                last_update = max(dates).strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'energy_count': energy_stats['count'],
            'gdp_count': gdp_stats['count'],
            'year_range': year_range,
            'last_update': last_update,
            'energy_years': f"{energy_stats['min_year']}-{energy_stats['max_year']}" if energy_stats['count'] > 0 else "-",
            'gdp_years': f"{gdp_stats['min_year']}-{gdp_stats['max_year']}" if gdp_stats['count'] > 0 else "-"
        }
        
    except Error as e:
        print(f"✗ Error getting data stats: {e}")
        return {
            'energy_count': 0,
            'gdp_count': 0,
            'year_range': '-',
            'last_update': '-'
        }
