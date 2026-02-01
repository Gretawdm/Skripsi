from flask import Flask, request, jsonify
from services.predict_service import predict_energy_service
from services.update_data_api import update_from_api
from services.update_data_api import preview_api_data
from services.train_service import retrain_model
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "API ARIMAX Energy is running 🚀"

from flask import render_template

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    scenario = data.get("scenario")
    years = int(data.get("years"))

    if scenario not in ["optimis", "moderat", "pesimistis"]:
        return jsonify({"error": "Invalid scenario"}), 400
    
    if years <1 or years > 5:
        return jsonify({"error": "Periode prediksi max 5 tahun"}), 400

    result = predict_energy_service(scenario, years)
    
    return jsonify({
        "scenario": scenario,
        "years": years,
        "prediction": result
    })

last_update_info = {
    "energy": None,
    "gdp": None
}

@app.route("/update-data", methods=["GET"])
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

@app.route("/data-status", methods=["GET"])
def data_status():
    return jsonify({
        "energy": last_update_info["energy"],
        "gdp": last_update_info["gdp"]
    })

@app.route("/debug/api-data", methods=["GET"])
def debug_api():
    return preview_api_data()

# 🔴 INI YANG SERING LUPA
if __name__ == "__main__":
    app.run(debug=True)
