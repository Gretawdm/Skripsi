"""
Test script untuk memverifikasi bahwa aktivasi model mengupdate prediksi
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def get_current_prediction():
    """Get current prediction from dashboard"""
    response = requests.get(f"{BASE_URL}/api/dashboard/prediction")
    data = response.json()
    
    if data.get('success') and data.get('predictions'):
        predictions = data['predictions']
        print(f"\nPrediksi saat ini (Moderat, 6 tahun):")
        for pred in predictions:
            print(f"  {pred['year']}: {pred['value']} TWh")
        return predictions
    else:
        print(f"\nError getting predictions: {data.get('error')}")
        return None

def get_active_model_info():
    """Get active model info"""
    response = requests.get(f"{BASE_URL}/api/dashboard/model-info")
    data = response.json()
    
    if data.get('success'):
        print(f"\nModel Aktif:")
        print(f"  Version: {data['model_version']}")
        print(f"  MAPE: {data['mape']}%")
        print(f"  R²: {data['r2']}")
        print(f"  Trained: {data['training_date']}")
        print(f"  Activated: {data['activated_at']}")
    else:
        print(f"\nError getting model info: {data.get('error')}")
    
    return data

def get_candidate_models():
    """Get list of candidate models"""
    response = requests.get(f"{BASE_URL}/api/models/candidates")
    data = response.json()
    
    if data.get('success'):
        models = data.get('models', [])
        print(f"\nCandidate Models: {len(models)}")
        for i, model in enumerate(models[:5], 1):
            print(f"  {i}. ID={model['id']} | MAPE={model['mape']}% | Order=({model['p']},{model['d']},{model['q']}) | Trained={model['training_date']}")
        return models
    else:
        print(f"\nError getting candidates: {data.get('error')}")
        return []

if __name__ == "__main__":
    print("="*70)
    print("TEST: Model Activation & Prediction Update")
    print("="*70)
    
    try:
        # Step 1: Get current state
        print("\n[STEP 1] Current state:")
        get_active_model_info()
        initial_predictions = get_current_prediction()
        
        # Step 2: Get candidates
        print("\n[STEP 2] Getting candidate models:")
        candidates = get_candidate_models()
        
        if not candidates:
            print("\n⚠️  No candidate models available to test activation.")
            print("   Please train a new model first.")
        else:
            print(f"\n💡 To test model activation:")
            print(f"   1. Go to http://127.0.0.1:5000/admin/update-model")
            print(f"   2. Activate a different model")
            print(f"   3. Run this script again to verify predictions changed")
            print(f"   4. Or activate via API:")
            print(f"      POST {BASE_URL}/api/models/activate/{candidates[0]['id']}")
        
        print("\n" + "="*70)
        print("✓ Test completed!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to Flask server")
        print("Please make sure the server is running with: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
