import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''  # Default XAMPP password kosong
}

def get_db_connection():
    """
    Create database connection
    Returns connection object or None if failed
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    """
    Initialize database tables if not exist
    """
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        # Create training_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_history (
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
        
        # Create data_update_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_update_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                update_date DATETIME NOT NULL,
                update_type VARCHAR(50) NOT NULL,
                source VARCHAR(100),
                records_added INT DEFAULT 0,
                records_updated INT DEFAULT 0,
                status VARCHAR(20) DEFAULT 'success',
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create prediction_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
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
        
        print("Database tables initialized successfully!")
        return True
        
    except Error as e:
        print(f"Error initializing database: {e}")
        return False

def save_training_history(metrics, year_range, energy_stats, gdp_stats, forecast_years=3, viz_plots=None, preprocessing_steps=None):
    """
    Save training result to database as CANDIDATE
    
    Args:
        metrics: Dictionary containing model metrics
        year_range: String like "1965-2024"
        energy_stats: Dictionary with energy statistics
        gdp_stats: Dictionary with GDP statistics
        forecast_years: Number of years to forecast (default: 3)
        viz_plots: Dictionary with visualization plots as base64 strings
        preprocessing_steps: List of preprocessing step dictionaries
        
    Returns:
        model_id: ID of the saved model (for file naming)
    """
    try:
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        
        # Convert preprocessing_steps to JSON string if provided
        preprocessing_steps_json = None
        if preprocessing_steps:
            preprocessing_steps_json = json.dumps(preprocessing_steps, ensure_ascii=False)
        
        # Build query dynamically based on whether viz_plots is provided
        if viz_plots:
            query = """
                INSERT INTO training_history (
                    training_date, p, d, q, mape, rmse, mae, r2,
                    train_size, test_size, train_percentage, test_percentage,
                    total_data, year_range,
                    energy_min, energy_max, energy_mean,
                    gdp_min, gdp_max, gdp_mean, status, model_status, forecast_years,
                    acf_plot, pacf_plot, preprocessing_plot, train_test_plot,
                    residual_plot, residual_acf_plot, qq_plot,
                    preprocessing_steps
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s
                )
            """
            
            values = (
                datetime.now(),
                metrics.get('p', 0),
                metrics.get('d', 0),
                metrics.get('q', 0),
                metrics.get('mape', 0),
                metrics.get('rmse', 0),
                metrics.get('mae', 0),
                metrics.get('r2', 0),
                metrics.get('train_size', 0),
                metrics.get('test_size', 0),
                metrics.get('train_percentage', 0),
                metrics.get('test_percentage', 0),
                metrics.get('total_data', 0),
                year_range,
                energy_stats.get('min', 0),
                energy_stats.get('max', 0),
                energy_stats.get('mean', 0),
                gdp_stats.get('min', 0),
                gdp_stats.get('max', 0),
                gdp_stats.get('mean', 0),
                'success',
                'candidate',
                forecast_years,
                viz_plots.get('acf_plot'),
                viz_plots.get('pacf_plot'),
                viz_plots.get('preprocessing_plot'),
                viz_plots.get('train_test_plot'),
                viz_plots.get('residual_plot'),
                viz_plots.get('residual_acf_plot'),
                viz_plots.get('qq_plot'),
                preprocessing_steps_json
            )
        else:
            query = """
                INSERT INTO training_history (
                    training_date, p, d, q, mape, rmse, mae, r2,
                    train_size, test_size, train_percentage, test_percentage,
                    total_data, year_range,
                    energy_min, energy_max, energy_mean,
                    gdp_min, gdp_max, gdp_mean, status, model_status, forecast_years,
                    preprocessing_steps
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s
                )
            """
            
            values = (
                datetime.now(),
                metrics.get('p', 0),
                metrics.get('d', 0),
                metrics.get('q', 0),
                metrics.get('mape', 0),
                metrics.get('rmse', 0),
                metrics.get('mae', 0),
                metrics.get('r2', 0),
                metrics.get('train_size', 0),
                metrics.get('test_size', 0),
                metrics.get('train_percentage', 0),
                metrics.get('test_percentage', 0),
                metrics.get('total_data', 0),
                year_range,
                energy_stats.get('min', 0),
                energy_stats.get('max', 0),
                energy_stats.get('mean', 0),
                gdp_stats.get('min', 0),
                gdp_stats.get('max', 0),
                gdp_stats.get('mean', 0),
                'success',
                'candidate',
                forecast_years,
                preprocessing_steps_json
            )
        
        cursor.execute(query, values)
        model_id = cursor.lastrowid  # Get the ID of inserted row
        connection.commit()
        
        cursor.close()
        connection.close()
        
        print(f"✓ Training history saved as CANDIDATE (ID: {model_id})")
        
        # Save a copy of the model file with unique ID for future activation
        try:
            import shutil
            main_model = "models/arimax_model.pkl"
            unique_model = f"models/arimax_model_{model_id}.pkl"
            
            if os.path.exists(main_model):
                shutil.copy2(main_model, unique_model)
                print(f"✓ Model file saved: {unique_model}")
        except Exception as copy_error:
            print(f"⚠ Warning: Could not save model copy: {copy_error}")
        
        return model_id
        
    except Error as e:
        print(f"Error saving training history: {e}")
        return None

def get_training_history(limit=50):
    """
    Get training history from database
    
    Args:
        limit: Maximum number of records to retrieve
    
    Returns:
        List of training history records
    """
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT * FROM training_history
            ORDER BY training_date DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        # Convert datetime to string for JSON serialization
        for record in results:
            if record.get('training_date'):
                record['training_date'] = record['training_date'].strftime('%Y-%m-%d %H:%M:%S')
            if record.get('created_at'):
                record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert Decimal to float
            for key in ['mape', 'rmse', 'mae', 'r2', 'energy_min', 'energy_max', 'energy_mean', 'gdp_min', 'gdp_max', 'gdp_mean']:
                if record.get(key):
                    record[key] = float(record[key])
        
        cursor.close()
        connection.close()
        
        return results
        
    except Error as e:
        print(f"Error getting training history: {e}")
        return []

def save_data_update_history(update_type, source, records_added=0, records_updated=0, status='success', message=''):
    """
    Save data update history
    
    Args:
        update_type: 'fetch_api' or 'manual_upload'
        source: Source of data
        records_added: Number of new records
        records_updated: Number of updated records
        status: 'success' or 'failed'
        message: Additional message
    """
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        query = """
            INSERT INTO data_update_history (
                update_date, update_type, source,
                records_added, records_updated, status, message
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            datetime.now(),
            update_type,
            source,
            records_added,
            records_updated,
            status,
            message
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error saving data update history: {e}")
        return False

def get_data_update_history(limit=50):
    """
    Get data update history from database
    """
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT * FROM data_update_history
            ORDER BY update_date DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        # Convert datetime to string
        for record in results:
            if record.get('update_date'):
                record['update_date'] = record['update_date'].strftime('%Y-%m-%d %H:%M:%S')
            if record.get('created_at'):
                record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        connection.close()
        
        return results
        
    except Error as e:
        print(f"Error getting data update history: {e}")
        return []

def save_prediction_history(scenario, years, prediction_data, model_version='ARIMAX v1.0'):
    """
    Save prediction history
    """
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        query = """
            INSERT INTO prediction_history (
                prediction_date, scenario, years, 
                prediction_data, model_version
            ) VALUES (%s, %s, %s, %s, %s)
        """
        
        values = (
            datetime.now(),
            scenario,
            years,
            json.dumps(prediction_data),
            model_version
        )
        
        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error saving prediction history: {e}")
        return False

def get_prediction_history(limit=50):
    """
    Get prediction history from database
    """
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT * FROM prediction_history
            ORDER BY prediction_date DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        # Convert datetime to string and parse JSON
        for record in results:
            if record.get('prediction_date'):
                record['prediction_date'] = record['prediction_date'].strftime('%Y-%m-%d %H:%M:%S')
            if record.get('created_at'):
                record['created_at'] = record['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if record.get('prediction_data'):
                record['prediction_data'] = json.loads(record['prediction_data'])
        
        cursor.close()
        connection.close()
        
        return results
        
    except Error as e:
        print(f"Error getting prediction history: {e}")
        return []

def get_history_summary():
    """
    Get summary statistics for history page
    """
    try:
        connection = get_db_connection()
        if not connection:
            return {
                'total_training': 0,
                'total_data_update': 0,
                'total_prediction': 0,
                'today_activities': 0
            }
        
        cursor = connection.cursor()
        
        # Total training
        cursor.execute("SELECT COUNT(*) FROM training_history")
        total_training = cursor.fetchone()[0]
        
        # Total data updates
        cursor.execute("SELECT COUNT(*) FROM data_update_history")
        total_data_update = cursor.fetchone()[0]
        
        # Total predictions
        cursor.execute("SELECT COUNT(*) FROM prediction_history")
        total_prediction = cursor.fetchone()[0]
        
        # Today's activities
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM training_history WHERE DATE(training_date) = CURDATE()) +
                (SELECT COUNT(*) FROM data_update_history WHERE DATE(update_date) = CURDATE()) +
                (SELECT COUNT(*) FROM prediction_history WHERE DATE(prediction_date) = CURDATE())
            AS today_count
        """)
        today_activities = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return {
            'total_training': total_training,
            'total_data_update': total_data_update,
            'total_prediction': total_prediction,
            'today_activities': today_activities
        }
        
    except Error as e:
        print(f"Error getting history summary: {e}")
        return {
            'total_training': 0,
            'total_data_update': 0,
            'total_prediction': 0,
            'today_activities': 0
        }

def clear_all_history():
    """
    Clear all history data (for testing purposes)
    """
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM training_history")
        cursor.execute("DELETE FROM data_update_history")
        cursor.execute("DELETE FROM prediction_history")
        
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"Error clearing history: {e}")
        return False

def test_connection():
    """
    Test database connection
    """
    connection = get_db_connection()
    if connection:
        connection.close()
        return True
    return False


# ===== MODEL STAGING SYSTEM =====

def get_active_model():
    """
    Get currently active model from database
    """
    try:
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT * FROM training_history 
            WHERE model_status = 'active'
            ORDER BY activated_at DESC
            LIMIT 1
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return result
        
    except Error as e:
        print(f"Error getting active model: {e}")
        return None


def get_candidate_models(limit=10):
    """
    Get all candidate models (not activated yet)
    """
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT * FROM training_history 
            WHERE model_status = 'candidate'
            ORDER BY training_date DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return results
        
    except Error as e:
        print(f"Error getting candidate models: {e}")
        return []


def activate_model(model_id, activated_by='admin'):
    """
    Activate a model - set as active and archive previous active model
    Also updates the main model file for predictions
    
    Args:
        model_id: ID of model to activate
        activated_by: Username who activated the model
    """
    try:
        import shutil
        
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        # Archive current active model
        cursor.execute("""
            UPDATE training_history 
            SET model_status = 'archived'
            WHERE model_status = 'active'
        """)
        
        # Activate new model
        cursor.execute("""
            UPDATE training_history 
            SET model_status = 'active',
                activated_at = NOW(),
                activated_by = %s
            WHERE id = %s
        """, (activated_by, model_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Update main model file
        # Copy the specific model file to be the active one
        model_file_path = f"models/arimax_model_{model_id}.pkl"
        main_model_path = "models/arimax_model.pkl"
        
        if os.path.exists(model_file_path):
            shutil.copy2(model_file_path, main_model_path)
            print(f"✓ Model file updated: {model_file_path} -> {main_model_path}")
        else:
            print(f"⚠ Warning: Model file not found: {model_file_path}")
            print("   Predictions will use the existing model file.")
        
        return True
        
    except Error as e:
        print(f"Error activating model: {e}")
        return False


def delete_candidate_model(model_id):
    """
    Delete a candidate model (only if it's not active)
    """
    try:
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        # Only delete if it's a candidate
        cursor.execute("""
            DELETE FROM training_history 
            WHERE id = %s AND model_status = 'candidate'
        """, (model_id,))
        
        affected = cursor.rowcount
        connection.commit()
        cursor.close()
        connection.close()
        
        return affected > 0
        
    except Error as e:
        print(f"Error deleting candidate model: {e}")
        return False


def get_all_models_comparison():
    """
    Get all models with status for comparison
    """
    try:
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                id, training_date, p, d, q,
                mape, rmse, mae, r2,
                total_data, model_status,
                activated_at, activated_by,
                train_size, test_size, 
                train_percentage, test_percentage,
                forecast_years
            FROM training_history 
            WHERE model_status IN ('active', 'candidate')
            ORDER BY 
                CASE model_status 
                    WHEN 'active' THEN 1 
                    WHEN 'candidate' THEN 2 
                END,
                training_date DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return results
        
    except Error as e:
        print(f"Error getting models comparison: {e}")
        return []
