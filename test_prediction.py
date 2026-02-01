"""
Script untuk test prediksi API
"""
import requests
import json

url = "http://localhost:5000/api/predict"
headers = {"Content-Type": "application/json"}
data = {
    "scenario": "moderat",
    "years": 3
}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Check if saved to database
    history_url = "http://localhost:5000/api/history/prediction"
    history_response = requests.get(history_url)
    print(f"\n\nPrediction History:")
    print(json.dumps(history_response.json(), indent=2))
    
except Exception as e:
    print(f"Error: {e}")
