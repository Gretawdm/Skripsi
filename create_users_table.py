import mysql.connector
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

def create_users_table():
    """Create users table with role field"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Drop existing table to recreate with proper schema
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                email VARCHAR(100),
                role ENUM('admin', 'user') DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        print("✓ Tabel users berhasil dibuat")
        
        connection.commit()
        
        # Check if default admin exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            # Create default admin
            hashed_password = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (username, password, full_name, email, role)
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', hashed_password, 'Administrator', 'admin@example.com', 'admin'))
            connection.commit()
            print("✓ Default admin user created (username: admin, password: admin123)")
        
        cursor.close()
        connection.close()
        
        print("\n✓ Setup selesai!")
        
    except mysql.connector.Error as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    create_users_table()
