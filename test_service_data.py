import sys
sys.path.append('.')
from services.database_service import get_training_history, get_data_update_history, get_prediction_history

print("=== Training History (dari service) ===")
training = get_training_history(limit=3)
for t in training:
    print(f"  Date: {t.get('training_date')} | Created: {t.get('created_at')}")

print("\n=== Data Update History (dari service) ===")
updates = get_data_update_history(limit=3)
for u in updates:
    print(f"  Date: {u.get('update_date')} | Created: {u.get('created_at')}")

print("\n=== Prediction History (dari service) ===")
predictions = get_prediction_history(limit=3)
for p in predictions:
    print(f"  Date: {p.get('prediction_date')} | Created: {p.get('created_at')}")
