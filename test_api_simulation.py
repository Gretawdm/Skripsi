import sys
sys.path.append('.')
from services.database_service import get_training_history, get_data_update_history, get_prediction_history
from datetime import datetime

print("=== Simulating API get_recent_activities ===\n")

activities = []

# Get training history
print("1. Getting training history...")
training_history = get_training_history(limit=5)
print(f"   Found: {len(training_history)} records")

for item in training_history:
    timestamp = item.get('created_at') or item.get('training_date')
    if timestamp and isinstance(timestamp, str):
        from datetime import datetime as dt
        try:
            timestamp_obj = dt.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            timestamp = timestamp_obj.isoformat()
        except:
            pass
    elif timestamp:
        timestamp = timestamp.isoformat()
    else:
        timestamp = datetime.now().isoformat()
        
    activities.append({
        "type": "training",
        "title": f"Model Training - {item.get('model_version', 'ARIMAX')}",
        "description": f"MAPE: {item.get('mape', 0):.2f}% | R²: {item.get('r2', 0):.3f}",
        "timestamp": timestamp
    })

print(f"   Added {len([a for a in activities if a['type'] == 'training'])} training activities")

# Get data update history
print("\n2. Getting data update history...")
data_history = get_data_update_history(limit=5)
print(f"   Found: {len(data_history)} records")

for item in data_history:
    timestamp = item.get('created_at') or item.get('update_date')
    if timestamp and isinstance(timestamp, str):
        from datetime import datetime as dt
        try:
            timestamp_obj = dt.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            timestamp = timestamp_obj.isoformat()
        except:
            pass
    elif timestamp:
        timestamp = timestamp.isoformat()
    else:
        timestamp = datetime.now().isoformat()
        
    activities.append({
        "type": "data",
        "title": f"Data Update - {item.get('update_type', 'All')}",
        "description": f"{item.get('records_updated', 0)} records updated",
        "timestamp": timestamp
    })

print(f"   Added {len([a for a in activities if a['type'] == 'data'])} data update activities")

# Get prediction history
print("\n3. Getting prediction history...")
prediction_history = get_prediction_history(limit=5)
print(f"   Found: {len(prediction_history)} records")

for item in prediction_history:
    timestamp = item.get('created_at') or item.get('prediction_date')
    if timestamp and isinstance(timestamp, str):
        from datetime import datetime as dt
        try:
            timestamp_obj = dt.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            timestamp = timestamp_obj.isoformat()
        except:
            pass
    elif timestamp:
        timestamp = timestamp.isoformat()
    else:
        timestamp = datetime.now().isoformat()
        
    activities.append({
        "type": "prediction",
        "title": f"Prediction - {item.get('scenario', 'Unknown').capitalize()}",
        "description": f"Prediksi {item.get('years', 0)} tahun ke depan",
        "timestamp": timestamp
    })

print(f"   Added {len([a for a in activities if a['type'] == 'prediction'])} prediction activities")

# Sort
activities.sort(key=lambda x: x['timestamp'], reverse=True)

print(f"\n=== Final Activities (Total: {len(activities)}) ===")
for i, activity in enumerate(activities[:10], 1):
    print(f"{i}. [{activity['type']}] {activity['title']} - {activity['timestamp']}")
