import requests
import json
import time

# Wait for Flask to be ready
time.sleep(3)

# Test predict API
url = 'http://127.0.0.1:5000/api/predict'
data = {
    'scenario': 'moderat',
    'years': 7,
    'save_to_database': False
}

print('Testing predict API...')
print(f'Request: {json.dumps(data, indent=2)}')

try:
    response = requests.post(url, json=data, timeout=10)
    print(f'\nStatus Code: {response.status_code}')
    result = response.json()
    
    if 'predictions' in result:
        print(f'\nPredictions (first 3): {result["predictions"][:3]}')
        print(f'Total predictions: {len(result["predictions"])}')
    
    print(f'\nFull Response:')
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f'Error: {e}')
