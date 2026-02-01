"""
Script untuk testing API dashboard
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_model_info():
    """Test /api/dashboard/model-info endpoint"""
    print("\n" + "="*60)
    print("Testing /api/dashboard/model-info")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/dashboard/model-info")
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    print(f"\nResponse:")
    print(json.dumps(data, indent=2))
    
    # Check required fields
    if data.get('success'):
        print("\n✓ Model info loaded successfully")
        if 'testData' in data:
            print("✓ Test data available for comparison chart")
        else:
            print("✗ Test data NOT available - comparison chart will be empty")
        
        if 'errorData' in data:
            print("✓ Error data available for error distribution chart")
        else:
            print("✗ Error data NOT available - error chart will be empty")
    else:
        print(f"\n✗ Error: {data.get('error')}")

def test_prediction():
    """Test /api/dashboard/prediction endpoint"""
    print("\n" + "="*60)
    print("Testing /api/dashboard/prediction")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/dashboard/prediction")
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    print(f"\nResponse (showing first few items):")
    
    # Print summary instead of full data
    if data.get('success'):
        print(f"✓ Success: True")
        print(f"  - Historical data points: {len(data.get('historical', []))}")
        print(f"  - Prediction data points: {len(data.get('predictions', []))}")
        print(f"  - Total records: {data.get('total_records')}")
        print(f"  - Data range: {data.get('data_range')}")
        print(f"  - Trend: {data.get('trend')} TWh/year")
    else:
        print(f"✗ Error: {data.get('error')}")

def test_recent_activities():
    """Test /api/dashboard/recent-activities endpoint"""
    print("\n" + "="*60)
    print("Testing /api/dashboard/recent-activities")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/dashboard/recent-activities")
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    
    if data.get('success'):
        activities = data.get('activities', [])
        print(f"✓ Found {len(activities)} activities")
        for i, activity in enumerate(activities[:3], 1):
            print(f"\n  {i}. {activity.get('title')}")
            print(f"     Type: {activity.get('type')}")
            print(f"     Time: {activity.get('timestamp')}")
    else:
        print(f"✗ Error: {data.get('error')}")

def test_system_status():
    """Test /api/dashboard/system-status endpoint"""
    print("\n" + "="*60)
    print("Testing /api/dashboard/system-status")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/dashboard/system-status")
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    
    if data.get('success'):
        print(f"✓ System status loaded")
        print(f"  - Uptime: {data.get('uptime')}")
        print(f"  - Model Server: {'Running' if data.get('modelServerRunning') else 'Stopped'}")
        print(f"  - Database: {'Connected' if data.get('databaseConnected') else 'Disconnected'}")
    else:
        print(f"✗ Error: {data.get('error')}")

if __name__ == "__main__":
    print("\n🧪 Dashboard API Testing")
    print("Make sure Flask server is running on http://127.0.0.1:5000\n")
    
    try:
        test_model_info()
        test_prediction()
        test_recent_activities()
        test_system_status()
        
        print("\n" + "="*60)
        print("✓ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to Flask server")
        print("Please make sure the server is running with: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
