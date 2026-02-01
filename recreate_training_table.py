"""
Script untuk recreate training_history table dengan schema yang benar
"""
from services.database_service import get_db_connection

try:
    connection = get_db_connection()
    if not connection:
        print("✗ Cannot connect to database")
        exit(1)
    
    cursor = connection.cursor()
    
    # Drop old table
    print("Dropping old training_history table...")
    cursor.execute("DROP TABLE IF EXISTS training_history")
    
    # Create new table with correct schema
    print("Creating new training_history table...")
    cursor.execute("""
        CREATE TABLE training_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            training_date DATETIME NOT NULL,
            model_version VARCHAR(50) DEFAULT 'ARIMAX v1.0',
            p INT NOT NULL,
            d INT NOT NULL,
            q INT NOT NULL,
            mape DECIMAL(10, 4),
            rmse DECIMAL(10, 4),
            mae DECIMAL(10, 4),
            r2 DECIMAL(10, 4),
            train_size INT,
            test_size INT,
            train_percentage INT,
            test_percentage INT,
            total_data INT,
            year_range VARCHAR(50),
            energy_min DECIMAL(15, 4),
            energy_max DECIMAL(15, 4),
            energy_mean DECIMAL(15, 4),
            gdp_min DECIMAL(20, 2),
            gdp_max DECIMAL(20, 2),
            gdp_mean DECIMAL(20, 2),
            status VARCHAR(20) DEFAULT 'success',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("✓ Table training_history recreated successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
