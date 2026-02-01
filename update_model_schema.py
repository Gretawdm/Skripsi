"""
Update database schema untuk Model Staging System
"""
from services.database_service import get_db_connection

try:
    connection = get_db_connection()
    if not connection:
        print("✗ Cannot connect to database")
        exit(1)
    
    cursor = connection.cursor()
    
    print("Adding model_status columns to training_history...")
    
    # Check if columns already exist
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'arimax_forecasting' 
        AND TABLE_NAME = 'training_history' 
        AND COLUMN_NAME IN ('model_status', 'activated_at', 'activated_by')
    """)
    existing_columns = [row[0] for row in cursor.fetchall()]
    
    # Add model_status if not exists
    if 'model_status' not in existing_columns:
        cursor.execute("""
            ALTER TABLE training_history 
            ADD COLUMN model_status ENUM('candidate', 'active', 'archived') DEFAULT 'candidate'
        """)
        print("✓ Added model_status column")
    else:
        print("ℹ model_status column already exists")
    
    # Add activated_at if not exists
    if 'activated_at' not in existing_columns:
        cursor.execute("""
            ALTER TABLE training_history 
            ADD COLUMN activated_at DATETIME NULL
        """)
        print("✓ Added activated_at column")
    else:
        print("ℹ activated_at column already exists")
    
    # Add activated_by if not exists
    if 'activated_by' not in existing_columns:
        cursor.execute("""
            ALTER TABLE training_history 
            ADD COLUMN activated_by VARCHAR(50) NULL
        """)
        print("✓ Added activated_by column")
    else:
        print("ℹ activated_by column already exists")
    
    # Set existing model as active (the first one)
    cursor.execute("""
        UPDATE training_history 
        SET model_status = 'active', activated_at = NOW(), activated_by = 'system'
        WHERE id = (SELECT MIN(id) FROM (SELECT id FROM training_history) as temp)
    """)
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("\n✓ Database schema updated successfully!")
    print("✓ Existing model set as ACTIVE")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
