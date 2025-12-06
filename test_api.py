#!/usr/bin/env python3
"""
API Test Script - Tests the FastAPI endpoints
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n[TEST] Health Check")
    print("-" * 50)
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_process():
    """Test /process endpoint"""
    print("\n[TEST] Process Endpoint (JSON Response)")
    print("-" * 50)
    
    payload = {
        "message": "The customer demo went great! They loved it but asked if we could add real-time notifications. They're willing to pay 20% more.",
        "sender": "Sarah Chen",
        "project_id": "PRJ-ALPHA",
        "message_id": "MSG-20241206-001"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_process_nion_map():
    """Test /process/nion-map endpoint"""
    print("\n[TEST] Process Endpoint (NION MAP Response)")
    print("-" * 50)
    
    payload = {
        "message": "The customer demo went great! They loved it but asked if we could add real-time notifications. They're willing to pay 20% more.",
        "sender": "Sarah Chen",
        "project_id": "PRJ-ALPHA",
        "message_id": "MSG-20241206-002"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process/nion-map", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"\nNION MAP Output:\n{response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def test_process_json():
    """Test /process/json endpoint"""
    print("\n[TEST] Process Endpoint (Detailed JSON Response)")
    print("-" * 50)
    
    payload = {
        "message": "The customer demo went great! They loved it but asked if we could add real-time notifications. They're willing to pay 20% more.",
        "sender": "Sarah Chen",
        "project_id": "PRJ-ALPHA",
        "message_id": "MSG-20241206-003"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/process/json", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    print("=" * 50)
    print("NION API TEST SUITE")
    print("=" * 50)
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            print("✓ Server is ready")
            break
        except:
            if i < 9:
                print(f"  Retry {i+1}/10...")
                time.sleep(1)
            else:
                print("✗ Server not responding")
                sys.exit(1)
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Process Endpoint", test_process()))
    results.append(("Process with NION MAP", test_process_nion_map()))
    results.append(("Process with JSON", test_process_json()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
