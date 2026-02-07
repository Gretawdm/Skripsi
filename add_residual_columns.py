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
    print("Adding residual diagnostic columns to training_history table...")
    
    # Add residual plot columns
    cursor.execute("""
        ALTER TABLE training_history 
        ADD COLUMN residual_plot LONGTEXT NULL,
        ADD COLUMN residual_acf_plot LONGTEXT NULL,
        ADD COLUMN qq_plot LONGTEXT NULL
    """)
    
    db.commit()
    print("✅ Residual diagnostic columns added successfully!")
    
except mysql.connector.Error as err:
    if err.errno == 1060:  # Duplicate column error
        print("⚠️  Residual columns already exist!")
    else:
        print(f"❌ Error: {err}")
        db.rollback()

finally:
    cursor.close()
    db.close()
    print("\nDone!")
