import requests
import json

r = requests.get('http://127.0.0.1:5000/api/dashboard/recent-activities')
data = r.json()

print('\n=== ALL Recent Activities ===')
print(f"Total: {len(data.get('activities', []))}")

for i, activity in enumerate(data.get('activities', []), 1):
    print(f"\n{i}. {activity['title']}")
    print(f"   Type: {activity['type']}")
    print(f"   Description: {activity['description']}")
    print(f"   Time: {activity['timestamp']}")
