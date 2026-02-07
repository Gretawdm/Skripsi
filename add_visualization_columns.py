import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

def add_visualization_columns():
    """Add columns for storing preprocessing visualizations"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Add columns for visualizations (stored as base64 encoded images)
        queries = [
            """
            ALTER TABLE training_history 
            ADD COLUMN acf_plot LONGTEXT NULL
            """,
            """
            ALTER TABLE training_history 
            ADD COLUMN pacf_plot LONGTEXT NULL
            """,
            """
            ALTER TABLE training_history 
            ADD COLUMN preprocessing_plot LONGTEXT NULL
            """,
            """
            ALTER TABLE training_history 
            ADD COLUMN train_test_plot LONGTEXT NULL
            """
        ]
        
        for query in queries:
            try:
                cursor.execute(query)
                print(f"✓ Executed: {query[:50]}...")
            except mysql.connector.Error as e:
                if "Duplicate column name" in str(e):
                    print(f"⚠ Column already exists, skipping...")
                else:
                    print(f"✗ Error: {e}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✓ Visualization columns added successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    add_visualization_columns()
