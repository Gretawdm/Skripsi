from flask import Blueprint, jsonify, render_template, request
from services.update_data_api import (
    update_from_api, 
    fetch_data_from_api, 
    upload_data_from_files,
    get_data_stats,
    get_energy_data,
    get_gdp_data
)
from services.train_service import retrain_model
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin')

last_update_info = {
    "energy": None,
    "gdp": None
}

@admin_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@admin_bp.route("/scraping-data")
def scraping_data():
    return render_template("scraping_data.html", page_title="Scraping Data")

@admin_bp.route("/update-model")
def update_model():
    return render_template("update_model.html")

@admin_bp.route("/riwayat")
def riwayat():  
    return render_template("riwayat.html", page_title="Riwayat")

@admin_bp.route("/update-data", methods=["GET"])
def update_data_and_train():
    result = update_from_api()

    now = datetime.now().strftime("%d %b %Y %H:%M:%S")
    last_update_info["energy"] = now
    last_update_info["gdp"] = now

    train_result = retrain_model()

    return jsonify({
        "message": "Data updated & model retrained",
        "data": result,
        "model": train_result,
        "update_at": now
    })

@admin_bp.route("/data-status", methods=["GET"])
def data_status():
    return jsonify(last_update_info)
