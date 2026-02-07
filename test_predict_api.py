import requests
import json

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
    response = requests.post(url, json=data)
    print(f'\nStatus Code: {response.status_code}')
    print(f'Response: {json.dumps(response.json(), indent=2)}')
except Exception as e:
    print(f'Error: {e}')
