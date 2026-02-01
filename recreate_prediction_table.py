"""
Script untuk recreate prediction_history table dan test save
"""
from services.database_service import get_db_connection, save_prediction_history

try:
    connection = get_db_connection()
    if not connection:
        print("✗ Cannot connect to database")
        exit(1)
    
    cursor = connection.cursor()
    
    # Drop old table
    print("Dropping old prediction_history table...")
    cursor.execute("DROP TABLE IF EXISTS prediction_history")
    
    # Create new table
    print("Creating new prediction_history table...")
    cursor.execute("""
        CREATE TABLE prediction_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            prediction_date DATETIME NOT NULL,
            scenario VARCHAR(50) NOT NULL,
            years INT NOT NULL,
            prediction_data JSON,
            model_version VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("✓ Table prediction_history recreated successfully!")
    
    # Test save
    print("\nTesting save_prediction_history...")
    test_prediction = [100.5, 200.3, 300.7]
    result = save_prediction_history("moderat", 3, test_prediction)
    
    if result:
        print("✓ Test prediction saved successfully!")
    else:
        print("✗ Failed to save test prediction")
    
    # Query to check
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM prediction_history")
    rows = cursor.fetchall()
    
    print(f"\nRecords in database: {len(rows)}")
    for row in rows:
        print(row)
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
