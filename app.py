from flask import Flask, render_template
from routes.admin import admin_bp
from routes.api import api_bp
# from services.scheduler_service import initialize_scheduler  # DISABLED: Tidak reliable di lokal
from services.database_service import init_database
from services.data_mysql_service import init_data_tables

app = Flask(__name__)

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



app.register_blueprint(admin_bp)
app.register_blueprint(api_bp, url_prefix="/api")

# SCHEDULER DISABLED - Manual fetch only
# initialize_scheduler()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
