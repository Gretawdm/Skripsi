import requests

r = requests.get('http://127.0.0.1:5000/api/dashboard/recent-activities')
data = r.json()

print('\nRecent Activities:')
for i, activity in enumerate(data.get('activities', [])[:8], 1):
    print(f"  {i}. {activity['title']}")
    print(f"     Time: {activity['timestamp']}")
    print()
