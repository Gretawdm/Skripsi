import requests
import json
import time

time.sleep(2)

print('=== Testing /api/prediction/latest ===')
try:
    response = requests.get('http://127.0.0.1:5000/api/prediction/latest', timeout=10)
    print(f'Status Code: {response.status_code}')
    data = response.json()
    
    if 'predictions' in data:
        print(f'\nPredictions count: {len(data["predictions"])}')
        print(f'Max years: {data.get("years", "N/A")}')
        print(f'Scenario: {data.get("scenario", "N/A")}')
        print(f'\nFirst 3 predictions:')
        for p in data['predictions'][:3]:
            print(f'  {p["year"]}: {p["prediction_value"]} TWh')
    else:
        print(f'\nResponse: {json.dumps(data, indent=2)}')
except Exception as e:
    print(f'Error: {e}')
