import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
db = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'arimax_forecasting')
)

cursor = db.cursor()

try:
    # Add preprocessing_steps column to store JSON data of all preprocessing steps
    print("Adding preprocessing_steps column to training_history table...")
    
    cursor.execute("""
        ALTER TABLE training_history 
        ADD COLUMN preprocessing_steps LONGTEXT NULL
        AFTER train_test_plot
    """)
    
    db.commit()
    print("✅ Column preprocessing_steps added successfully!")
    
except mysql.connector.Error as err:
    if err.errno == 1060:  # Duplicate column error
        print("⚠️  Column preprocessing_steps already exists!")
    else:
        print(f"❌ Error: {err}")
        db.rollback()

finally:
    cursor.close()
    db.close()
    print("\nDone!")
