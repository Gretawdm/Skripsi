from flask import Flask, render_template, jsonify
from routes.admin import admin_bp
from routes.api import api_bp
from routes.auth import auth_bp
from services.data_mysql_service import get_energy_from_db, get_gdp_from_db
# from services.scheduler_service import initialize_scheduler  # DISABLED: Tidak reliable di lokal
from services.database_service import init_database
from services.data_mysql_service import init_data_tables

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Untuk session management

# Initialize database tables on startup
try:
    init_database()
    init_data_tables()
    print("✓ Database initialized successfully")
except Exception as e:
    print(f"⚠ Warning: Database initialization failed: {e}")

@app.route("/")
def home():
    return render_template("index.html")
    # return "API ARIMAX Energy is running 🚀"

@app.route("/prediksi")
def prediksi():
    return render_template("prediksi.html")

@app.route("/metode")
def metode():
    return render_template("metode.html")

@app.route('/api/dashboard/actual-gdp')
def api_actual_gdp():

    energy_rows = get_energy_from_db()
    gdp_rows = get_gdp_from_db()

    actual = [
        {
            "year": row["Year"], 
            "value": float(row["fossil_fuels__twh"])
        }
        for row in energy_rows
    ]

    gdp = [
        {
            "year": row["year"], 
            "value": float(row["gdp"])
        }
        for row in gdp_rows
    ]

    return jsonify({
        "actual": actual,
        "gdp": gdp
    })


app.register_blueprint(admin_bp)
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")

# SCHEDULER DISABLED - Manual fetch only
# initialize_scheduler()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
